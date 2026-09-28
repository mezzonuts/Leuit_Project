from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# POS Sync schemas
class PosSyncUploadResponse(BaseModel):
    status: str
    new_inserted: int
    duplicates_skipped: int
    message: Optional[str] = None

class PosSyncHistoryItem(BaseModel):
    id: int
    file_name: str
    uploaded_at: datetime
    total_rows_read: int
    new_rows_inserted: int
    duplicate_rows_skipped: int
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    reconciled_stock_items: int

class PosSyncHistoryResponse(BaseModel):
    items: List[PosSyncHistoryItem]
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
    date_range_start: Optional[datetime]
    date_range_end: Optional[datetime]
    reconciled_stock_items: int
    new_transactions: List[dict]  # Simplified for response