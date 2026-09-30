"""Verify auth API request/response schemas correct."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas.auth_schema import (
    AuthStatusResponse,
    InitializeRequest,
    InitializeResponse,
    UnlockRequest,
    UnlockResponse,
)


class TestUnlockRequest:
    def test_minimal_valid(self):
        req = UnlockRequest(passkey="123456")
        assert req.passkey == "123456"
        assert req.is_developer is False

    def test_developer_mode(self):
        req = UnlockRequest(passkey="dev-key-123", is_developer=True)
        assert req.is_developer is True
        assert req.passkey == "dev-key-123"

    def test_short_passkey_rejected(self):
        with pytest.raises(ValidationError):
            UnlockRequest(passkey="ab")

    def test_exact_min_length_passes(self):
        req = UnlockRequest(passkey="1234")
        assert req.passkey == "1234"


class TestUnlockResponse:
    def test_success_response(self):
        resp = UnlockResponse(
            success=True,
            role="OWNER",
            message="Unlocked",
            license_status="ACTIVE",
            grace_days=0,
        )
        assert resp.success is True
        assert resp.role == "OWNER"
        assert resp.license_status == "ACTIVE"

    def test_developer_response(self):
        resp = UnlockResponse(
            success=True,
            role="DEVELOPER",
            message="Dev unlock",
        )
        assert resp.role == "DEVELOPER"

    def test_failure_response(self):
        resp = UnlockResponse(
            success=False,
            role="UNAUTHENTICATED",
            message="Failed",
        )
        assert resp.success is False


class TestAuthStatusResponse:
    def test_locked_status(self):
        resp = AuthStatusResponse(
            role="UNAUTHENTICATED",
            is_locked=True,
            license_status="LOCKED",
            license_message="DB locked",
            grace_days_left=0,
        )
        assert resp.is_locked is True
        assert resp.license_status == "LOCKED"

    def test_unlocked_with_license(self):
        resp = AuthStatusResponse(
            is_locked=False,
            role="OWNER",
            license_status="ACTIVE",
            license_message="OK",
            grace_days_left=0,
            license_id="DEV-001",
            valid_until=datetime(2027, 1, 1),
        )
        assert resp.is_locked is False
        assert resp.license_id == "DEV-001"

    def test_grace_period(self):
        resp = AuthStatusResponse(
            is_locked=False,
            role="OWNER",
            license_status="GRACE_PERIOD",
            license_message="Expiring",
            grace_days_left=2,
        )
        assert resp.grace_days_left == 2


class TestInitializeRequest:
    def test_defaults(self):
        req = InitializeRequest(owner_passkey="secure-pin-123")
        assert req.owner_passkey == "secure-pin-123"
        assert req.license_id == "DEV-LOCAL-001"

    def test_custom_license_id(self):
        req = InitializeRequest(owner_passkey="longpin", license_id="CUSTOM-001")
        assert req.license_id == "CUSTOM-001"

    def test_short_passkey_rejected(self):
        with pytest.raises(ValidationError):
            InitializeRequest(owner_passkey="short")

    def test_exact_min_length_passes(self):
        req = InitializeRequest(owner_passkey="123456")
        assert req.owner_passkey == "123456"


class TestInitializeResponse:
    def test_basic_response(self):
        resp = InitializeResponse(
            success=True,
            message="Initialized",
            hardware_id="hw-001",
        )
        assert resp.success is True
        assert resp.hardware_id == "hw-001"
