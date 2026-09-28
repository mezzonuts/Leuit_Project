# Security module exports
from app.core.security.hardware import get_machine_fingerprint, get_hardware_info
from app.core.security.licensing import (
    verify_license_token,
    verify_license_signature,
    check_hardware_binding,
    check_monotonic_clock,
    evaluate_license_status,
    load_license_from_file,
    save_license_to_file,
    SecurityException,
    LicenseData,
)
from app.core.security.key_envelope import (
    KeyEnvelope,
    derive_sqlcipher_key,
    generate_key_rotation_package,
)

__all__ = [
    "get_machine_fingerprint",
    "get_hardware_info",
    "verify_license_token",
    "verify_license_signature",
    "check_hardware_binding",
    "check_monotonic_clock",
    "evaluate_license_status",
    "load_license_from_file",
    "save_license_to_file",
    "SecurityException",
    "LicenseData",
    "KeyEnvelope",
    "derive_sqlcipher_key",
    "generate_key_rotation_package",
]