from collections.abc import Generator

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import _engine, get_session
from app.core.security import SecurityException, load_license_from_file, verify_license_token


def get_db() -> Generator[Session, None, None]:
    yield from get_session()

def require_db_unlocked() -> None:
    if _engine is None:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Database terkunci. Silakan unlock terlebih dahulu.",
        )

def verify_license(
    x_passkey: str | None = Header(None, alias="X-Passkey"),
    db: Session = Depends(get_db)
) -> dict:
    if _engine is None:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Database terkunci. Silakan unlock terlebih dahulu.",
        )

    license_data = load_license_from_file()
    if not license_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="License file not found. Please activate your license.",
        )

    token_bytes, signature_bytes = license_data

    try:
        result = verify_license_token(token_bytes, signature_bytes, db)
        return result
    except SecurityException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

def get_passkey(x_passkey: str | None = Header(None, alias="X-Passkey")) -> str | None:
    return x_passkey

def require_owner(
    license_info: dict = Depends(verify_license)
) -> dict:
    if license_info.get("status") == "LOCKED":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner access required",
        )
    return license_info

def require_developer(
    license_info: dict = Depends(verify_license)
) -> dict:
    if license_info.get("status") == "LOCKED":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Developer access required",
        )
    return license_info
