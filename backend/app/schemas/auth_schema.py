from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class UnlockRequest(BaseModel):
    passkey: str = Field(..., min_length=4)
    is_developer: bool = False

class UnlockResponse(BaseModel):
    success: bool
    role: Literal["OWNER", "DEVELOPER", "UNAUTHENTICATED"]
    message: str | None = None
    last_unlocked_at: datetime | None = None
    license_status: str | None = None
    grace_days: int | None = None

class AuthStatusResponse(BaseModel):
    is_locked: bool
    role: Literal["OWNER", "DEVELOPER", "UNAUTHENTICATED"]
    last_unlocked_at: datetime | None = None
    license_status: Literal["ACTIVE", "GRACE_PERIOD", "LOCKED"]
    license_message: str
    grace_days_left: int
    license_id: str | None = None
    valid_until: datetime | None = None

class InitializeRequest(BaseModel):
    owner_passkey: str = Field(..., min_length=6)
    license_id: str = "DEV-LOCAL-001"

class InitializeResponse(BaseModel):
    success: bool
    message: str
    hardware_id: str