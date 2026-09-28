from typing import Generator, Optional
from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.core.security import verify_license_token, load_license_from_file, SecurityException
from app.models.security import AppLicense

# Database session dependency
def get_db() -> Generator[Session, None, None]:
    yield from get_session()

# License verification dependency
def verify_license(
    x_passkey: Optional[str] = Header(None, alias="X-Passkey"),
    db: Session = Depends(get_db)
) -> dict:
    """
    Verify license status and database unlock state.
    Returns license info dict.
    """
    # Check if license file exists and is valid
    license_data = load_license_from_file()
    if not license_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="License file not found. Please activate your license."
        )

    token_bytes, signature_bytes = license_data

    try:
        result = verify_license_token(token_bytes, signature_bytes, db)
        return result
    except SecurityException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

# Optional passkey header for authenticated endpoints
def get_passkey(x_passkey: Optional[str] = Header(None, alias="X-Passkey")) -> Optional[str]:
    return x_passkey

# Role verification
def require_owner(
    license_info: dict = Depends(verify_license)
) -> dict:
    if license_info.get("role") != "OWNER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner access required"
        )
    return license_info

def require_developer(
    license_info: dict = Depends(verify_license)
) -> dict:
    if license_info.get("role") != "DEVELOPER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Developer access required"
        )
    return license_info