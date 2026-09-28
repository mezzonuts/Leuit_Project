import json
import time
import nacl.signing
import nacl.exceptions
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.core.security.hardware import get_machine_fingerprint

# Load Ed25519 public key from settings
CLOUD_PUBLIC_KEY: bytes = bytes.fromhex(settings.CLOUD_PUBLIC_KEY_HEX) if settings.CLOUD_PUBLIC_KEY_HEX else b""

class SecurityException(Exception):
    """Custom exception for security-related errors."""
    pass

class LicenseData:
    """License data structure."""
    def __init__(
        self,
        license_id: str,
        hardware_id: str,
        valid_until: int,
        issued_at: int,
        features: Optional[list] = None,
        metadata: Optional[dict] = None
    ):
        self.license_id = license_id
        self.hardware_id = hardware_id
        self.valid_until = valid_until
        self.issued_at = issued_at
        self.features = features or ["full"]
        self.metadata = metadata or {}

    def to_dict(self) -> dict:
        return {
            "license_id": self.license_id,
            "hardware_id": self.hardware_id,
            "valid_until": self.valid_until,
            "issued_at": self.issued_at,
            "features": self.features,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LicenseData":
        return cls(
            license_id=data["license_id"],
            hardware_id=data["hardware_id"],
            valid_until=data["valid_until"],
            issued_at=data["issued_at"],
            features=data.get("features"),
            metadata=data.get("metadata"),
        )

def verify_license_signature(token_bytes: bytes, signature_bytes: bytes) -> Optional[LicenseData]:
    """
    Verify Ed25519 signature of license token.
    Returns LicenseData if valid, None if invalid.
    """
    if not CLOUD_PUBLIC_KEY:
        raise SecurityException("Cloud public key not configured")

    try:
        verify_key = nacl.signing.VerifyKey(CLOUD_PUBLIC_KEY)
        payload = verify_key.verify(token_bytes, signature_bytes)
        license_dict = json.loads(payload.decode('utf-8'))
        return LicenseData.from_dict(license_dict)
    except (nacl.exceptions.BadSignatureError, json.JSONDecodeError, KeyError) as e:
        raise SecurityException(f"Invalid license signature: {str(e)}")

def check_hardware_binding(license_data: LicenseData) -> bool:
    """Verify license is bound to current machine."""
    current_fingerprint = get_machine_fingerprint()
    return license_data.hardware_id == current_fingerprint

def check_monotonic_clock(db: Session) -> bool:
    """
    Check for system time manipulation (clock turned back).
    Returns True if clock is valid, False if time travel detected.
    """
    current_unix = int(time.time())

    # Get last recorded timestamp
    result = db.execute(
        text("SELECT MAX(last_seen_timestamp) FROM security_audit_clock")
    ).scalar()

    last_timestamp = result or 0

    if current_unix < last_timestamp:
        # Time travel detected!
        return False

    # Record current timestamp
    db.execute(
        text("INSERT INTO security_audit_clock (last_seen_timestamp) VALUES (:ts)"),
        {"ts": current_unix}
    )
    db.commit()

    return True

def evaluate_license_status(license_data: LicenseData) -> Dict[str, Any]:
    """
    Evaluate license status based on expiry and grace period.
    Returns dict with status, message, and days remaining.
    """
    current_unix = int(time.time())
    valid_until = license_data.valid_until
    grace_limit = valid_until + (settings.GRACE_PERIOD_DAYS * 86400)

    if current_unix > grace_limit:
        return {
            "status": "LOCKED",
            "message": "Langganan telah kedaluwarsa. Silakan perpanjang lisensi.",
            "days_left": 0,
            "grace_days_left": 0,
        }
    elif current_unix > valid_until:
        days_left = (grace_limit - current_unix) // 86400 + 1
        return {
            "status": "GRACE_PERIOD",
            "message": f"Masa tenggang berjalan. Sisa {days_left} hari.",
            "days_left": max(0, (valid_until - current_unix) // 86400 + 1),
            "grace_days_left": days_left,
        }
    else:
        days_left = (valid_until - current_unix) // 86400 + 1
        return {
            "status": "ACTIVE",
            "message": "Lisensi aktif",
            "days_left": days_left,
            "grace_days_left": 0,
        }

def verify_license_token(
    token_bytes: bytes,
    signature_bytes: bytes,
    db: Session
) -> Dict[str, Any]:
    """
    Complete license verification pipeline:
    1. Verify Ed25519 signature
    2. Check hardware binding
    3. Check monotonic clock
    4. Evaluate expiry status
    """
    # 1. Verify cryptographic signature
    license_data = verify_license_signature(token_bytes, signature_bytes)

    # 2. Verify hardware binding
    if not check_hardware_binding(license_data):
        raise SecurityException("Lisensi ini terikat pada perangkat keras lain!")

    # 3. Monotonic clock guard
    if not check_monotonic_clock(db):
        raise SecurityException(
            "Manipulasi jam sistem terdeteksi! Sinkronkan jam komputer Anda dengan server waktu."
        )

    # 4. Evaluate license status
    status = evaluate_license_status(license_data)

    return {
        **status,
        "license_id": license_data.license_id,
        "issued_at": license_data.issued_at,
        "valid_until": license_data.valid_until,
        "features": license_data.features,
    }

def load_license_from_file(filepath: Optional[str] = None) -> Optional[tuple]:
    """Load license token and signature from local file."""
    path = filepath or settings.LICENSE_FILE_PATH

    try:
        with open(path, "r") as f:
            data = json.load(f)

        token = data.get("token", "").encode()
        signature = bytes.fromhex(data.get("signature", ""))

        if token and signature:
            return token, signature
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        pass

    return None

def save_license_to_file(token_bytes: bytes, signature_bytes: bytes, filepath: Optional[str] = None) -> bool:
    """Save license token and signature to local file."""
    path = filepath or settings.LICENSE_FILE_PATH

    try:
        import os
        os.makedirs(os.path.dirname(path), exist_ok=True)

        data = {
            "token": token_bytes.decode(),
            "signature": signature_bytes.hex(),
            "saved_at": int(time.time()),
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        return True
    except Exception:
        return False