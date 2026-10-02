"""Outlet schemas for API validation."""
from __future__ import annotations

from pydantic import BaseModel, Field


class OutletBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    address: str | None = Field(None, max_length=1000)
    phone: str | None = Field(None, max_length=50)
    is_active: bool = True
    settings: str | None = None


class OutletCreate(OutletBase):
    pass


class OutletUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    address: str | None = Field(None, max_length=1000)
    phone: str | None = Field(None, max_length=50)
    is_active: bool | None = None
    settings: str | None = None


class OutletResponse(OutletBase):
    id: int
    created_at: str | None = None
    updated_at: str | None = None


class OutletListResponse(BaseModel):
    items: list[OutletResponse]
    total: int = 0
