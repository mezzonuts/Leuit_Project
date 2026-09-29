from datetime import datetime

from pydantic import BaseModel


# POS Sync schemas
class PosSyncUploadResponse(BaseModel):
    status: str
    new_inserted: int
    duplicates_skipped: int
    message: str | None = None

class PosSyncHistoryItem(BaseModel):
    id: int
    file_name: str
    uploaded_at: datetime
    total_rows_read: int
    new_rows_inserted: int
    duplicate_rows_skipped: int
    date_range_start: datetime | None = None
    date_range_end: datetime | None = None
    reconciled_stock_items: int

class PosSyncHistoryResponse(BaseModel):
    items: list[PosSyncHistoryItem]
    total: int
    page: int
    page_size: int
    total_pages: int

class PosSyncDetailResponse(BaseModel):
    sync_id: int
    file_name: str
    uploaded_at: datetime
    total_rows_read: int
    new_rows_inserted: int
    duplicate_rows_skipped: int
    date_range_start: datetime | None
    date_range_end: datetime | None
    reconciled_stock_items: int
    new_transactions: list[dict]  # Simplified for response