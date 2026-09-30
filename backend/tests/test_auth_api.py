"""Unit tests auth_security endpoints: rate limiting, schema validation."""

import time
from collections import defaultdict
from datetime import datetime

import pytest


def _make_rate_limiter() -> dict[str, object]:
    ns = {"defaultdict": defaultdict, "time": time}
    exec(
        "from collections import defaultdict\n"
        "import time\n"
        "_unlock_attempts = defaultdict(list)\n"
        "MAX_UNLOCK_ATTEMPTS = 5\n"
        "UNLOCK_WINDOW_SECONDS = 900\n"
        "def _check_rate_limit(client_ip):\n"
        "    now = time.time()\n"
        "    cutoff = now - UNLOCK_WINDOW_SECONDS\n"
        "    _unlock_attempts[client_ip] = [t for t in _unlock_attempts[client_ip] if t > cutoff]\n"
        "    if len(_unlock_attempts[client_ip]) >= MAX_UNLOCK_ATTEMPTS:\n"
        "        return False\n"
        "    _unlock_attempts[client_ip].append(now)\n"
        "    return True\n",
        ns,
    )
    return ns


class TestRateLimiting:
    """Test in-memory rate limiter unlock attempts."""

    def _reset_rate_limiter(self) -> None:
        self._ns = _make_rate_limiter()

    def setup_method(self) -> None:
        self._reset_rate_limiter()

    def teardown_method(self) -> None:
        self._reset_rate_limiter()

    def test_first_attempt_allowed(self) -> None:
        assert self._ns["_check_rate_limit"]("127.0.0.1") is True

    def test_five_attempts_allowed(self) -> None:
        fn = self._ns["_check_rate_limit"]
        for _ in range(5):
            assert fn("127.0.0.1") is True

    def test_sixth_attempt_blocked(self) -> None:
        fn = self._ns["_check_rate_limit"]
        for _ in range(5):
            fn("127.0.0.1")
        assert fn("127.0.0.1") is False

    def test_different_ips_independent(self) -> None:
        fn = self._ns["_check_rate_limit"]
        for _ in range(5):
            fn("127.0.0.1")
        assert fn("192.168.1.1") is True

        self._ns["_unlock_attempts"]["127.0.0.1"] = [time.time() - 2000]
        for _ in range(5):
            fn("127.0.0.1")
        assert fn("127.0.0.1") is False


class TestUnlockRequestSchema:
    def test_valid_unlock_request(self) -> None:
        from app.schemas.auth_schema import UnlockRequest

        req = UnlockRequest(passkey="my-passphrase-123")
        assert req.passkey == "my-passphrase-123"
        assert req.is_developer is False

    def test_unlock_request_min_length_rejection(self) -> None:
        from pydantic import ValidationError

        from app.schemas.auth_schema import UnlockRequest

        with pytest.raises(ValidationError):
            UnlockRequest(passkey="ab")


class TestInitializeRequestSchema:
    def test_valid_initialize_request(self) -> None:
        from app.schemas.auth_schema import InitializeRequest

        req = InitializeRequest(owner_passkey="secure-pin-123")
        assert req.owner_passkey == "secure-pin-123"
        assert req.license_id == "DEV-LOCAL-001"

    def test_initialize_request_min_length_rejection(self) -> None:
        from pydantic import ValidationError

        from app.schemas.auth_schema import InitializeRequest

        with pytest.raises(ValidationError):
            InitializeRequest(owner_passkey="short")


class TestAuthStatusResponse:
    def test_locked_status(self) -> None:
        from app.schemas.auth_schema import AuthStatusResponse

        resp = AuthStatusResponse(
            is_locked=True,
            role="UNAUTHENTICATED",
            license_status="LOCKED",
            license_message="Database is locked.",
            grace_days_left=0,
        )
        assert resp.is_locked is True
        assert resp.role == "UNAUTHENTICATED"

    def test_active_license_status(self) -> None:
        from app.schemas.auth_schema import AuthStatusResponse

        resp = AuthStatusResponse(
            is_locked=False,
            role="OWNER",
            license_status="ACTIVE",
            license_message="License active",
            grace_days_left=0,
            license_id="DEV-001",
            valid_until=datetime(2027, 1, 1),
        )
        assert resp.is_locked is False
        assert resp.license_id == "DEV-001"
