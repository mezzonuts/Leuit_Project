"""LEUIT Backend Test Suite - Smoke tests for CI."""
import pytest


def test_backend_imports() -> None:
    """Verify core modules can be imported."""
    from app.core.config import settings
    assert settings.APP_NAME == "LEUIT"


def test_security_hardware() -> None:
    """Verify hardware fingerprint generation works."""
    from app.core.security.hardware import get_machine_fingerprint
    fingerprint = get_machine_fingerprint()
    assert len(fingerprint) == 64  # SHA256 hex
    assert fingerprint != ""


def test_security_key_envelope() -> None:
    """Verify dual-key envelope encryption works."""
    from app.core.security.key_envelope import KeyEnvelope

    dek = KeyEnvelope.generate_dek()
    assert len(dek) == 32

    # Test owner encryption round-trip
    encrypted, salt = KeyEnvelope.encrypt_dek_for_owner(dek, "test-passkey-123")
    decrypted = KeyEnvelope.decrypt_dek_for_owner(encrypted, "test-passkey-123")
    assert decrypted == dek

    # Test wrong passkey fails
    with pytest.raises(ValueError):
        KeyEnvelope.decrypt_dek_for_owner(encrypted, "wrong-passkey")