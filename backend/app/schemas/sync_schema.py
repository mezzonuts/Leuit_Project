from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# POS Sync schemas
class PosSyncUploadResponse(BaseModel):
    status: Literal["success", "partial", "failed"]
    new_inserted: int = Field(ge=0)
    duplicates_skipped: int = Field(ge=0)
    message: str | None = None

class PosSyncHistoryItem(BaseModel):
    id: int
    file_name: str = Field(max_length=255)
    uploaded_at: datetime
    total_rows_read: int = Field(ge=0)
    new_rows_inserted: int = Field(ge=0)
    duplicate_rows_skipped: int = Field(ge=0)
    date_range_start: datetime | None = None
    date_range_end: datetime | None = None
    reconciled_stock_items: int = Field(ge=0)

class PosSyncHistoryResponse(BaseModel):
    items: list[PosSyncHistoryItem]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total_pages: int = Field(ge=0)

class PosSyncDetailResponse(BaseModel):
    sync_id: int
    file_name: str
    uploaded_at: datetime
    total_rows_read: int = Field(ge=0)
    new_rows_inserted: int = Field(ge=0)
    duplicate_rows_skipped: int = Field(ge=0)
    date_range_start: datetime | None = None
    date_range_end: datetime | None = None
    reconciled_stock_items: int = Field(ge=0)
    new_transactions: list[dict] = Field(default_factory=list)
