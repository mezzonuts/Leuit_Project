from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, verify_license, get_passkey
from app.schemas.auth_schema import (
    UnlockRequest,
    UnlockResponse,
    AuthStatusResponse,
)
from app.core.database import init_database, verify_database_key
from app.core.security import verify_license_token, load_license_from_file, save_license_to_file
from app.core.security.key_envelope import KeyEnvelope, derive_sqlcipher_key
from app.models.security import SecurityKeyring
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/unlock", response_model=UnlockResponse)
def unlock_database(
    request: UnlockRequest,
    db: Session = Depends(get_db)
):
    """
    Unlock encrypted database using Owner PIN or Developer Recovery Key.
    """
    passkey = request.passkey
    is_developer = request.is_developer

    # Load license file to get encrypted DEK envelopes
    license_file = load_license_from_file()
    if not license_file:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="License file not found. Please activate license first."
        )

    # Get keyring from database (stored envelopes)
    keyring = db.query(SecurityKeyring).first()
    if not keyring:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Keyring not initialized. Contact administrator."
        )

    try:
        # Try to decrypt DEK using provided passkey
        dek = None
        if is_developer:
            # Developer mode: would use private key (not implemented in MVP)
            # For MVP, developer uses a special master passkey
            import hashlib
            dev_master_key = hashlib.sha256(b"LEUIT_DEV_MASTER_2024").digest().hex()
            if passkey != dev_master_key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Developer Recovery Key"
                )
            # Decrypt using developer envelope (simplified for MVP)
            dek = KeyEnvelope.open_envelope_owner(
                {"encrypted_dek_owner": keyring.encrypted_dek_owner},
                passkey
            )
        else:
            # Owner mode: decrypt with passkey
            dek = KeyEnvelope.open_envelope_owner(
                {"encrypted_dek_owner": keyring.encrypted_dek_owner},
                passkey
            )

        # Verify the DEK works with database
        sqlcipher_key = derive_sqlcipher_key(bytes.fromhex(dek))
        if not verify_database_key(sqlcipher_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid passkey. Database cannot be decrypted."
            )

        # Initialize database with the key
        init_database(sqlcipher_key)

        # Verify license status
        license_data = load_license_from_file()
        if license_data:
            token_bytes, signature_bytes = license_data
            license_result = verify_license_token(token_bytes, signature_bytes, db)

            return UnlockResponse(
                success=True,
                role="DEVELOPER" if is_developer else "OWNER",
                message="Database unlocked successfully",
                last_unlocked_at=None,
                license_status=license_result.get("status"),
                grace_days=license_result.get("grace_days_left"),
            )

        return UnlockResponse(
            success=True,
            role="DEVELOPER" if is_developer else "OWNER",
            message="Database unlocked successfully (license check skipped)",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unlock database: {str(e)}"
        )

@router.get("/status", response_model=AuthStatusResponse)
def get_auth_status(
    db: Session = Depends(get_db)
):
    """
    Get current authentication and license status.
    """
    # Check if database is unlocked (engine initialized)
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

    # Database is unlocked, check license
    license_data = load_license_from_file()
    if not license_data:
        return AuthStatusResponse(
            is_locked=False,
            role="OWNER",  # Assume owner if unlocked
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