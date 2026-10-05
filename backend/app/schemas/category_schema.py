"""Category schemas."""
from __future__ import annotations

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    color: str = Field(default="#16a34a", pattern=r"^#[0-9a-fA-F]{6}$")


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    color: str | None = Field(None, pattern=r"^#[0-9a-fA-F]{6}$")


class CategoryResponse(BaseModel):
    id: int
    name: str
    color: str
    created_at: str | None = None


class CategoryListResponse(BaseModel):
    items: list[CategoryResponse]
    total: int = 0
