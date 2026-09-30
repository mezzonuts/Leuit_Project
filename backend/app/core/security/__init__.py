# Security module exports
from app.core.security.hardware import get_hardware_info, get_machine_fingerprint
from app.core.security.key_envelope import (
    KeyEnvelope,
    derive_sqlcipher_key,
    generate_key_rotation_package,
)
from app.core.security.licensing import (
    LicenseData,
    SecurityException,
    check_hardware_binding,
    check_monotonic_clock,
    evaluate_license_status,
    load_license_from_file,
    save_license_to_file,
    verify_license_signature,
    verify_license_token,
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