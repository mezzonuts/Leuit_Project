from datetime import datetime

from pydantic import BaseModel, Field

from app.models.purchase import PaymentMethod, PaymentStatus


# Supplier schemas
class SupplierBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    phone_whatsapp: str | None = Field(None, max_length=50)
    payment_terms_days: int = Field(0, ge=0)

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    phone_whatsapp: str | None = Field(None, max_length=50)
    payment_terms_days: int | None = Field(None, ge=0)

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
    due_date: datetime | None = None

class PurchaseCreate(PurchaseBase):
    @classmethod
    def validate_due_date(cls, values: "PurchaseCreate") -> "PurchaseCreate":
        if values.payment_method == PaymentMethod.CREDIT and values.payment_status == PaymentStatus.UNPAID:
            if not values.due_date:
                raise ValueError("due_date required for CREDIT UNPAID purchases")
        return values

class PurchaseUpdate(BaseModel):
    purchase_date: datetime | None = None
    ingredient_id: int | None = Field(None, ge=1)
    supplier_id: int | None = Field(None, ge=1)
    quantity: float | None = Field(None, gt=0)
    total_cost: float | None = Field(None, ge=0)
    payment_method: PaymentMethod | None = None
    payment_status: PaymentStatus | None = None
    due_date: datetime | None = None

class PurchaseResponse(PurchaseBase):
    id: int
    ingredient_name: str | None = None
    supplier_name: str | None = None
    is_overdue: bool
    days_until_due: int
    created_at: datetime

    class Config:
        from_attributes = True

class PurchaseListResponse(BaseModel):
    items: list[PurchaseResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

# Payables
class AccountsPayableAlert(BaseModel):
    supplier_id: int
    supplier_name: str
    phone_whatsapp: str | None = None
    total_unpaid: float
    nearest_due_date: datetime
    days_until_due: int
    purchase_count: int

class AccountsPayableResponse(BaseModel):
    alerts: list[AccountsPayableAlert]
    total_unpaid: float
    urgent_count: int

class SupplierStatsResponse(BaseModel):
    supplier_id: int
    supplier_name: str
    total_purchases: float
    unpaid_total: float
    avg_order_value: float
    purchase_count: int
    period_days: int