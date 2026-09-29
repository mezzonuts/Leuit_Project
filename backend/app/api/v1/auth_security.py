import time
from collections import defaultdict
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from nacl.public import PrivateKey
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.core.config import settings
from app.core.database import init_database, verify_database_key
from app.core.security import load_license_from_file, verify_license_token
from app.core.security.hardware import get_machine_fingerprint
from app.core.security.key_envelope import KeyEnvelope, derive_sqlcipher_key
from app.models.security import SecurityKeyring, SecurityUnlockAudit
from app.schemas.auth_schema import (
    AuthStatusResponse,
    InitializeRequest,
    InitializeResponse,
    UnlockRequest,
    UnlockResponse,
)

_unlock_attempts: dict[str, list[float]] = defaultdict(list)
MAX_UNLOCK_ATTEMPTS = 5
UNLOCK_WINDOW_SECONDS = 900  # 15 minutes


def _check_rate_limit(client_ip: str) -> bool:
    now = time.time()
    cutoff = now - UNLOCK_WINDOW_SECONDS
    _unlock_attempts[client_ip] = [t for t in _unlock_attempts[client_ip] if t > cutoff]
    if len(_unlock_attempts[client_ip]) >= MAX_UNLOCK_ATTEMPTS:
        return False
    _unlock_attempts[client_ip].append(now)
    return True


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/initialize", response_model=InitializeResponse)
def initialize_database_endpoint(request: InitializeRequest):
    from nacl.public import PublicKey

    from app.core.database import init_database
    from app.core.security.key_envelope import KeyEnvelope, derive_sqlcipher_key
    from app.models.security import SecurityKeyring

    hardware_id = get_machine_fingerprint()

    dev_pub_path = Path(settings.PUBLIC_KEY_PATH)
    if not dev_pub_path.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Developer public key file not found.",
        )
    dev_pub_hex = dev_pub_path.read_text().strip()
    dev_public_key = PublicKey(bytes.fromhex(dev_pub_hex))

    dek = KeyEnvelope.generate_dek()

    envelope = KeyEnvelope.create_envelope(dek, request.owner_passkey, dev_public_key)

    sqlcipher_key = derive_sqlcipher_key(dek)
    init_database(sqlcipher_key)

    from app.core.database import get_session
    db = next(get_session())
    try:
        keyring = SecurityKeyring(
            encrypted_dek_owner=envelope["encrypted_dek_owner"],
            encrypted_dek_developer=envelope["encrypted_dek_developer"],
        )
        db.add(keyring)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    return InitializeResponse(
        success=True,
        message="Database initialized successfully. Keyring created with dual-envelope encryption.",
        hardware_id=hardware_id,
    )


@router.post("/unlock", response_model=UnlockResponse)
def unlock_database(
    request: UnlockRequest,
    db: Session = Depends(get_db),
):
    client_ip = "127.0.0.1"
    if not _check_rate_limit(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Terlalu banyak percobaan. Coba lagi dalam 15 menit.",
        )

    passkey = request.passkey
    is_developer = request.is_developer

    license_file = load_license_from_file()
    if not license_file:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="License file not found. Please activate license first."
        )

    keyring = db.query(SecurityKeyring).first()
    if not keyring:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Keyring not initialized. Contact administrator."
        )

    try:
        dek = None
        if is_developer:
            dev_priv_path = Path(settings.DEV_PRIVATE_KEY_PATH)
            if not dev_priv_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Developer private key file not found.",
                )
            dev_priv_hex = dev_priv_path.read_text().strip()
            dev_private_key = PrivateKey(bytes.fromhex(dev_priv_hex))
            dek = KeyEnvelope.open_envelope_developer(
                {"encrypted_dek_developer": keyring.encrypted_dek_developer},
                dev_private_key,
            )
        else:
            dek = KeyEnvelope.open_envelope_owner(
                {"encrypted_dek_owner": keyring.encrypted_dek_owner},
                passkey
            )

        sqlcipher_key = derive_sqlcipher_key(bytes.fromhex(dek))
        if not verify_database_key(sqlcipher_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid passkey. Database cannot be decrypted."
            )

        init_database(sqlcipher_key)

        license_data = load_license_from_file()
        if license_data:
            token_bytes, signature_bytes = license_data
            license_result = verify_license_token(token_bytes, signature_bytes, db)

            try:
                audit = SecurityUnlockAudit(
                    role="DEVELOPER" if is_developer else "OWNER",
                    success=1,
                )
                db.add(audit)
                db.commit()
            except Exception:
                pass

            return UnlockResponse(
                success=True,
                role="DEVELOPER" if is_developer else "OWNER",
                message="Database unlocked successfully",
                last_unlocked_at=None,
                license_status=license_result.get("status"),
                grace_days=license_result.get("grace_days_left"),
            )

        try:
            audit = SecurityUnlockAudit(
                role="DEVELOPER" if is_developer else "OWNER",
                success=1,
            )
            db.add(audit)
            db.commit()
        except Exception:
            pass

        return UnlockResponse(
            success=True,
            role="DEVELOPER" if is_developer else "OWNER",
            message="Database unlocked successfully (license check skipped)",
        )

    except HTTPException as e:
        try:
            audit = SecurityUnlockAudit(
                role="DEVELOPER" if is_developer else "OWNER",
                success=0,
                failure_reason=str(e.detail),
            )
            db.add(audit)
            db.commit()
        except Exception:
            pass
        raise
    except Exception as e:
        try:
            audit = SecurityUnlockAudit(
                role="DEVELOPER" if is_developer else "OWNER",
                success=0,
                failure_reason=str(e),
            )
            db.add(audit)
            db.commit()
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unlock database: {str(e)}"
        )


@router.get("/status", response_model=AuthStatusResponse)
def get_auth_status(
    db: Session = Depends(get_db)
):
    from app.core.database import _engine
    is_locked = _engine is None

    if is_locked:
        return AuthStatusResponse(
            is_locked=True,
            role="UNAUTHENTICATED",
            license_status="LOCKED",
            license_message="Database is locked. Enter passkey to unlock.",
            grace_days_left=0,
        )

    license_data = load_license_from_file()
    if not license_data:
        return AuthStatusResponse(
            is_locked=False,
            role="OWNER",
            last_unlocked_at=None,
            license_status="LOCKED",
            license_message="License file not found",
            grace_days_left=0,
        )

    try:
        token_bytes, signature_bytes = license_data
        result = verify_license_token(token_bytes, signature_bytes, db)

        return AuthStatusResponse(
            is_locked=False,
            role=result.get("role", "OWNER"),
            license_status=result.get("status", "ACTIVE"),
            license_message=result.get("message", ""),
            grace_days_left=result.get("grace_days_left", 0),
            license_id=result.get("license_id"),
            valid_until=result.get("valid_until"),
        )
    except Exception as e:
        return AuthStatusResponse(
            is_locked=False,
            role="OWNER",
            license_status="LOCKED",
            license_message=f"License verification failed: {str(e)}",
            grace_days_left=0,
        )
