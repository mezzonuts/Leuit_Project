"""Unit tests security modules: KeyEnvelope, Hardware, Licensing."""
import time
from unittest.mock import MagicMock

import pytest
from nacl.public import PrivateKey

# ── KeyEnvelope Tests ──

class TestKeyEnvelope:
    def test_generate_dek_returns_32_bytes(self) -> None:
        from app.core.security.key_envelope import KeyEnvelope

        dek = KeyEnvelope.generate_dek()
        assert len(dek) == 32

    def test_owner_encrypt_decrypt_roundtrip(self) -> None:
        from app.core.security.key_envelope import KeyEnvelope

        dek = KeyEnvelope.generate_dek()
        encrypted, salt = KeyEnvelope.encrypt_dek_for_owner(dek, "my-passkey-123")
        decrypted = KeyEnvelope.decrypt_dek_for_owner(encrypted, "my-passkey-123")
        assert decrypted == dek

    def test_owner_wrong_passkey_fails(self) -> None:
        from app.core.security.key_envelope import KeyEnvelope

        dek = KeyEnvelope.generate_dek()
        encrypted, _ = KeyEnvelope.encrypt_dek_for_owner(dek, "correct-passkey")
        with pytest.raises(ValueError, match="Invalid passkey"):
            KeyEnvelope.decrypt_dek_for_owner(encrypted, "wrong-passkey")

    def test_different_passkeys_produce_different_ciphertext(self) -> None:
        from app.core.security.key_envelope import KeyEnvelope

        dek = KeyEnvelope.generate_dek()
        enc_a, _ = KeyEnvelope.encrypt_dek_for_owner(dek, "passkey-a")
        enc_b, _ = KeyEnvelope.encrypt_dek_for_owner(dek, "passkey-b")
        assert enc_a != enc_b

    def test_developer_encrypt_decrypt_roundtrip(self) -> None:
        from app.core.security.key_envelope import KeyEnvelope

        privkey = PrivateKey.generate()
        dek = KeyEnvelope.generate_dek()
        encrypted = KeyEnvelope.encrypt_dek_for_developer(dek, privkey.public_key)
        decrypted = KeyEnvelope.decrypt_dek_for_developer(encrypted, privkey)
        assert decrypted == dek

    def test_developer_wrong_key_fails(self) -> None:
        from app.core.security.key_envelope import KeyEnvelope

        dek = KeyEnvelope.generate_dek()
        encrypted = KeyEnvelope.encrypt_dek_for_developer(dek, PrivateKey.generate().public_key)
        with pytest.raises(ValueError):
            KeyEnvelope.decrypt_dek_for_developer(encrypted, PrivateKey.generate())

    def test_create_and_open_envelope_owner(self) -> None:
        from app.core.security.key_envelope import KeyEnvelope

        privkey = PrivateKey.generate()
        dek = KeyEnvelope.generate_dek()
        envelope = KeyEnvelope.create_envelope(dek, "owner-pin", privkey.public_key)

        assert "encrypted_dek_owner" in envelope
        assert "encrypted_dek_developer" in envelope
        assert envelope["version"] == 1

        recovered = KeyEnvelope.open_envelope_owner(envelope, "owner-pin")
        assert recovered == dek

    def test_create_and_open_envelope_developer(self) -> None:
        from app.core.security.key_envelope import KeyEnvelope

        privkey = PrivateKey.generate()
        dek = KeyEnvelope.generate_dek()
        envelope = KeyEnvelope.create_envelope(dek, "owner-pin", privkey.public_key)

        recovered = KeyEnvelope.open_envelope_developer(envelope, privkey)
        assert recovered == dek

    def test_dek_size_constants(self) -> None:
        from app.core.security.key_envelope import DEK_SIZE, NONCE_SIZE, SALT_SIZE

        assert DEK_SIZE == 32
        assert SALT_SIZE == 16
        assert NONCE_SIZE == 12


# ── Hardware Fingerprint Tests ──

class TestHardwareFingerprint:
    def test_returns_64_char_hex(self) -> None:
        from app.core.security.hardware import get_machine_fingerprint

        fp = get_machine_fingerprint()
        assert len(fp) == 64
        assert all(c in "0123456789abcdef" for c in fp)

    def test_is_deterministic(self) -> None:
        from app.core.security.hardware import get_machine_fingerprint

        get_machine_fingerprint.cache_clear()
        fp1 = get_machine_fingerprint()
        fp2 = get_machine_fingerprint()
        assert fp1 == fp2

    def test_hardware_info_returns_dict(self) -> None:
        from app.core.security.hardware import get_hardware_info

        info = get_hardware_info()
        assert isinstance(info, dict)
        assert "system" in info


# ── Licensing Tests ──

class TestLicenseData:
    def test_from_dict_roundtrip(self) -> None:
        from app.core.security.licensing import LicenseData

        data = {
            "license_id": "TEST-001",
            "hardware_id": "abc123",
            "valid_until": int(time.time()) + 86400,
            "issued_at": int(time.time()),
            "features": ["full"],
        }
        ld = LicenseData.from_dict(data)
        assert ld.license_id == "TEST-001"
        d = ld.to_dict()
        assert d["license_id"] == "TEST-001"

    def test_defaults(self) -> None:
        from app.core.security.licensing import LicenseData

        ld = LicenseData("L-1", "hw", 100, 0)
        assert ld.features == ["full"]
        assert ld.metadata == {}


class TestLicenseStatus:
    def test_active_license(self) -> None:
        from app.core.security.licensing import LicenseData, evaluate_license_status

        future = int(time.time()) + 86400 * 30
        ld = LicenseData("L-1", "hw", future, int(time.time()))
        result = evaluate_license_status(ld)
        assert result["status"] == "ACTIVE"
        assert result["days_left"] > 0

    def test_expired_in_grace_period(self) -> None:
        from app.core.security.licensing import LicenseData, evaluate_license_status

        past = int(time.time()) - 86400 * 1
        ld = LicenseData("L-2", "hw", past, int(time.time()) - 86400 * 10)
        result = evaluate_license_status(ld)
        assert result["status"] == "GRACE_PERIOD"

    def test_expired_locked(self) -> None:
        from app.core.security.licensing import LicenseData, evaluate_license_status

        old = int(time.time()) - 86400 * 30
        ld = LicenseData("L-3", "hw", old, old)
        result = evaluate_license_status(ld)
        assert result["status"] == "LOCKED"
        assert result["days_left"] == 0


class TestHardwareBinding:
    def test_matching_fingerprint(self) -> None:
        from app.core.security.hardware import get_machine_fingerprint
        from app.core.security.licensing import LicenseData, check_hardware_binding

        fp = get_machine_fingerprint()
        ld = LicenseData("L-4", fp, int(time.time()), int(time.time()))
        assert check_hardware_binding(ld) is True

    def test_mismatched_fingerprint(self) -> None:
        from app.core.security.licensing import LicenseData, check_hardware_binding

        ld = LicenseData("L-5", "WRONG_FINGERPRINT", int(time.time()), int(time.time()))
        assert check_hardware_binding(ld) is False


class TestMonotonicClock:
    def test_valid_clock(self) -> None:
        from app.core.security.licensing import check_monotonic_clock

        mock_db = MagicMock()
        mock_db.execute.return_value.scalar.return_value = 0
        assert check_monotonic_clock(mock_db) is True

    def test_clock_manipulation_detected(self) -> None:
        from app.core.security.licensing import check_monotonic_clock

        mock_db = MagicMock()
        future_ts = int(time.time()) + 86400
        mock_db.execute.return_value.scalar.return_value = future_ts
        assert check_monotonic_clock(mock_db) is False


class TestSecurityException:
    def test_is_exception(self) -> None:
        from app.core.security.licensing import SecurityException

        assert issubclass(SecurityException, Exception)
        with pytest.raises(SecurityException, match="test error"):
            raise SecurityException("test error")
