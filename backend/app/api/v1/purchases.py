from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, verify_license
from app.models.ingredient import Ingredient
from app.models.purchase import InventoryPurchase, PaymentMethod, PaymentStatus, Supplier
from app.schemas.purchase_schema import (
    AccountsPayableAlert,
    AccountsPayableResponse,
    PurchaseCreate,
    PurchaseListResponse,
    PurchaseResponse,
    SupplierCreate,
    SupplierResponse,
    SupplierUpdate,
)

router = APIRouter(prefix="/purchases", tags=["Purchases"])

# Supplier endpoints
@router.get("/suppliers", response_model=list[SupplierResponse])
def list_suppliers(
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
):
    """List all suppliers."""
    suppliers = db.query(Supplier).order_by(Supplier.name).all()
    return [SupplierResponse.model_validate(s) for s in suppliers]

@router.post("/suppliers", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
def create_supplier(
    data: SupplierCreate,
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
):
    """Create new supplier."""
    supplier = Supplier(**data.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return SupplierResponse.model_validate(supplier)

@router.put("/suppliers/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: int,
    data: SupplierUpdate,
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
):
    """Update supplier."""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(supplier, field, value)

    db.commit()
    db.refresh(supplier)
    return SupplierResponse.model_validate(supplier)

@router.delete("/suppliers/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
):
    """Delete supplier (only if no purchases)."""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    purchase_count = db.query(InventoryPurchase).filter(
        InventoryPurchase.supplier_id == supplier_id
    ).count()

    if purchase_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete supplier with existing purchases")

    db.delete(supplier)
    db.commit()
    return

# Purchase endpoints
@router.get("", response_model=PurchaseListResponse)
def list_purchases(
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
):
    """List purchases with filters."""
    query = db.query(InventoryPurchase).join(Ingredient).join(Supplier)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Ingredient.name.ilike(search_term),
                Supplier.name.ilike(search_term),
            )
        )

    if status_filter and status_filter in ["PAID", "UNPAID"]:
        query = query.filter(InventoryPurchase.payment_status == status_filter)

    total = query.count()
    items = query.order_by(desc(InventoryPurchase.purchase_date)).offset(skip).limit(limit).all()

    return PurchaseListResponse(
        items=[PurchaseResponse.model_validate(item) for item in items],
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        total_pages=(total + limit - 1) // limit,
    )

@router.post("", response_model=PurchaseResponse, status_code=status.HTTP_201_CREATED)
def create_purchase(
    data: PurchaseCreate,
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
):
    """Record new purchase."""
    # Validate ingredient
    ingredient = db.query(Ingredient).filter(Ingredient.id == data.ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    # Validate supplier
    supplier = db.query(Supplier).filter(Supplier.id == data.supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    # Validate credit purchase requires due_date
    if data.payment_method == PaymentMethod.CREDIT and data.payment_status == PaymentStatus.UNPAID:
        if not data.due_date:
            raise HTTPException(status_code=400, detail="due_date required for CREDIT UNPAID purchases")

    purchase = InventoryPurchase(**data.model_dump())
    db.add(purchase)

    # Update ingredient stock (only for cash or paid credit)
    if data.payment_method == PaymentMethod.CASH or data.payment_status == PaymentStatus.PAID:
        ingredient.current_stock += data.quantity
    else:
        # For credit unpaid, stock will be added when paid
        pass

    db.commit()
    db.refresh(purchase)
    return PurchaseResponse.model_validate(purchase)

@router.post("/{purchase_id}/pay", response_model=PurchaseResponse)
def pay_purchase(
    purchase_id: int,
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
):
    """Mark purchase as paid and update stock."""
    purchase = db.query(InventoryPurchase).filter(InventoryPurchase.id == purchase_id).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")

    if purchase.payment_status == PaymentStatus.PAID:
        raise HTTPException(status_code=400, detail="Already paid")

    purchase.payment_status = PaymentStatus.PAID
    purchase.updated_at = datetime.now(UTC)

    # Add stock when paid
    ingredient = db.query(Ingredient).filter(Ingredient.id == purchase.ingredient_id).first()
    if ingredient:
        ingredient.current_stock += purchase.quantity

    db.commit()
    db.refresh(purchase)
    return PurchaseResponse.model_validate(purchase)

@router.get("/payables", response_model=AccountsPayableResponse)
def get_payables(
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
):
    """Get accounts payable summary."""
    # Get unpaid credit purchases grouped by supplier
    unpaid_purchases = db.query(InventoryPurchase).filter(
        InventoryPurchase.payment_method == PaymentMethod.CREDIT,
        InventoryPurchase.payment_status == PaymentStatus.UNPAID,
    ).all()

    # Group by supplier
    supplier_totals = {}
    for p in unpaid_purchases:
        if p.supplier_id not in supplier_totals:
            supplier_totals[p.supplier_id] = {
                "supplier": p.supplier,
                "total_unpaid": 0.0,
                "nearest_due_date": p.due_date,
                "purchase_count": 0,
            }
        supplier_totals[p.supplier_id]["total_unpaid"] += float(p.total_cost)
        supplier_totals[p.supplier_id]["purchase_count"] += 1
        if p.due_date and (supplier_totals[p.supplier_id]["nearest_due_date"] is None or p.due_date < supplier_totals[p.supplier_id]["nearest_due_date"]):
            supplier_totals[p.supplier_id]["nearest_due_date"] = p.due_date

    alerts = []
    total_unpaid = 0.0
    urgent_count = 0

    for supplier_id, data in supplier_totals.items():
        days_until = 0
        if data["nearest_due_date"]:
            from datetime import datetime
            delta = data["nearest_due_date"] - datetime.now(UTC)
            days_until = max(0, delta.days)

        if days_until <= 3 and days_until >= 0:
            urgent_count += 1

        total_unpaid += data["total_unpaid"]

        alerts.append(AccountsPayableAlert(
            supplier_id=supplier_id,
            supplier_name=data["supplier"].name,
            total_unpaid=data["total_unpaid"],
            nearest_due_date=data["nearest_due_date"] or datetime.now(UTC),
            days_until_due=days_until,
            purchase_count=data["purchase_count"],
        ))

    return AccountsPayableResponse(
        alerts=alerts,
        total_unpaid=round(total_unpaid, 2),
        urgent_count=urgent_count,
    )

@router.get("/restock-sheet")
def get_restock_sheet(
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
):
    """Get restock recommendations (simple version - full version in forecast)."""
    from app.models.ingredient import Ingredient

    ingredients = db.query(Ingredient).filter(Ingredient.is_active).all()

    items = []
    for ing in ingredients:
        stock_ratio = (float(ing.current_stock) / float(ing.min_stock_threshold) * 100) if ing.min_stock_threshold > 0 else 100

        if stock_ratio < 150:  # Needs restocking
            # Simple prediction: average daily usage * 7 days
            avg_daily = 10.0  # placeholder
            predicted_7d = avg_daily * 7
            safety_stock = float(ing.min_stock_threshold) * 1.2
            recommended_qty = max(0, predicted_7d + safety_stock - float(ing.current_stock))

            if recommended_qty > 0:
                priority = "high" if stock_ratio < 100 else "medium"
                items.append({
                    "ingredient_id": ing.id,
                    "ingredient_name": ing.name,
                    "unit": ing.unit,
                    "current_stock": float(ing.current_stock),
                    "predicted_consumption_7d": round(predicted_7d, 2),
                    "recommended_order_qty": round(recommended_qty, 2),
                    "safety_stock": round(safety_stock, 2),
                    "estimated_cost": round(recommended_qty * float(ing.cost_per_unit), 2),
                    "priority": priority,
                    "supplier_id": None,
                    "supplier_name": None,
                    "lead_time_days": ing.lead_time_days,
                })

    return {"items": items}