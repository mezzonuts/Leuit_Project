from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.ingredient_schema import IngredientResponse
from app.models.purchase import PaymentMethod, PaymentStatus

# Supplier schemas
class SupplierBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    phone_whatsapp: Optional[str] = Field(None, max_length=50)
    payment_terms_days: int = Field(0, ge=0)

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone_whatsapp: Optional[str] = Field(None, max_length=50)
    payment_terms_days: Optional[int] = Field(None, ge=0)

class SupplierResponse(SupplierBase):
    id: int
    is_credit: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Purchase schemas
class PurchaseBase(BaseModel):
    purchase_date: datetime
    ingredient_id: int = Field(..., ge=1)
    supplier_id: int = Field(..., ge=1)
    quantity: float = Field(..., gt=0)
    total_cost: float = Field(..., ge=0)
    payment_method: PaymentMethod
    payment_status: PaymentStatus = PaymentStatus.PAID
    due_date: Optional[datetime] = None

class PurchaseCreate(PurchaseBase):
    @classmethod
    def validate_due_date(cls, values):
        if values.payment_method == PaymentMethod.CREDIT and values.payment_status == PaymentStatus.UNPAID:
            if not values.due_date:
                raise ValueError("due_date required for CREDIT UNPAID purchases")
        return values

class PurchaseUpdate(BaseModel):
    purchase_date: Optional[datetime] = None
    ingredient_id: Optional[int] = Field(None, ge=1)
    supplier_id: Optional[int] = Field(None, ge=1)
    quantity: Optional[float] = Field(None, gt=0)
    total_cost: Optional[float] = Field(None, ge=0)
    payment_method: Optional[PaymentMethod] = None
    payment_status: Optional[PaymentStatus] = None
    due_date: Optional[datetime] = None

class PurchaseResponse(PurchaseBase):
    id: int
    ingredient_name: Optional[str] = None
    supplier_name: Optional[str] = None
    is_overdue: bool
    days_until_due: int
    created_at: datetime

    class Config:
        from_attributes = True

class PurchaseListResponse(BaseModel):
    items: List[PurchaseResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

# Payables
class AccountsPayableAlert(BaseModel):
    supplier_id: int
    supplier_name: str
    total_unpaid: float
    nearest_due_date: datetime
    days_until_due: int
    purchase_count: int

class AccountsPayableResponse(BaseModel):
    alerts: List[AccountsPayableAlert]
    total_unpaid: float
    urgent_count: int