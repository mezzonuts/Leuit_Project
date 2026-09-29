from datetime import datetime

from pydantic import BaseModel, Field


# Ingredient schemas
class IngredientBase(BaseModel):
    barcode_sku: str | None = Field(None, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    unit: str = Field(..., pattern="^(ml|gram|pcs)$")
    cost_per_unit: float = Field(..., ge=0)
    shelf_life_days: int = Field(..., ge=1)
    current_stock: float = Field(0, ge=0)
    min_stock_threshold: float = Field(0, ge=0)
    lead_time_days: int = Field(1, ge=0)

class IngredientCreate(IngredientBase):
    pass

class IngredientUpdate(BaseModel):
    barcode_sku: str | None = Field(None, max_length=100)
    name: str | None = Field(None, min_length=1, max_length=255)
    unit: str | None = Field(None, pattern="^(ml|gram|pcs)$")
    cost_per_unit: float | None = Field(None, ge=0)
    shelf_life_days: int | None = Field(None, ge=1)
    current_stock: float | None = Field(None, ge=0)
    min_stock_threshold: float | None = Field(None, ge=0)
    lead_time_days: int | None = Field(None, ge=0)
    is_active: bool | None = None

class IngredientResponse(IngredientBase):
    id: int
    is_active: bool
    stock_ratio: float
    stock_status: str
    valuation: float
    days_until_expiry: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class IngredientListResponse(BaseModel):
    items: list[IngredientResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

# Stock Opname
class StockOpnameRequest(BaseModel):
    quantity: float = Field(..., ge=0)

class StockOpnameResponse(BaseModel):
    ingredient_id: int
    previous_stock: float
    new_stock: float
    difference: float
    timestamp: datetime

# Valuation
class ValuationSummary(BaseModel):
    total_valuation: float
    total_ingredients: int
    low_stock_count: int
    expired_soon_count: int

class ValuationItem(BaseModel):
    id: int
    name: str
    barcode_sku: str | None
    current_stock: float
    unit: str
    cost_per_unit: float
    total_valuation: float
    shelf_life_days: int
    min_stock_threshold: float