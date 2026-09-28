from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class UnlockRequest(BaseModel):
    passkey: str = Field(..., min_length=4)
    is_developer: bool = False

class UnlockResponse(BaseModel):
    success: bool
    role: Literal["OWNER", "DEVELOPER", "UNAUTHENTICATED"]
    message: Optional[str] = None
    last_unlocked_at: Optional[datetime] = None
    license_status: Optional[str] = None
    grace_days: Optional[int] = None

class AuthStatusResponse(BaseModel):
    is_locked: bool
    role: Literal["OWNER", "DEVELOPER", "UNAUTHENTICATED"]
    last_unlocked_at: Optional[datetime] = None
    license_status: Literal["ACTIVE", "GRACE_PERIOD", "LOCKED"]
    license_message: str
    grace_days_left: int
    license_id: Optional[str] = None
    valid_until: Optional[datetime] = None