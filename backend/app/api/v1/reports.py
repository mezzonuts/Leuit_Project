"""Consolidated reports API endpoints for multi-outlet."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, verify_license
from app.models.ingredient import Ingredient
from app.models.outlet import Outlet
from app.models.purchase import InventoryPurchase
from app.models.transaction import SalesTransaction

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/consolidated")
def get_consolidated_report(
    outlet_id: int | None = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
) -> dict:
    """Get consolidated report across all outlets (or filtered by outlet_id)."""
    end_date = datetime.now(UTC)
    start_date = end_date - timedelta(days=days)

    # Get all active outlets
    outlets = db.query(Outlet).filter(Outlet.is_active).all()

    # Build per-outlet breakdown
    outlet_reports = []
    total_valuation = 0.0
    total_purchases = 0.0
    total_sales_count = 0

    for outlet in outlets:
        # Inventory valuation for this outlet
        query = db.query(Ingredient).filter(Ingredient.is_active)
        if outlet_id:
            query = query.filter(Ingredient.outlet_id == outlet_id)
        else:
            query = query.filter((Ingredient.outlet_id == outlet.id) | (Ingredient.outlet_id.is_(None)))

        ingredients = query.all()
        outlet_valuation = sum(float(i.current_stock) * float(i.cost_per_unit) for i in ingredients)

        # Purchases for this outlet
        purchase_query = db.query(InventoryPurchase).filter(
            InventoryPurchase.purchase_date >= start_date,
            InventoryPurchase.purchase_date <= end_date,
        )
        if outlet_id:
            purchase_query = purchase_query.filter(InventoryPurchase.outlet_id == outlet_id)
        else:
            purchase_query = purchase_query.filter(
                (InventoryPurchase.outlet_id == outlet.id) | (InventoryPurchase.outlet_id.is_(None))
            )

        purchases = purchase_query.all()
        outlet_purchases = sum(float(p.total_cost) for p in purchases)

        # Sales transactions for this outlet
        sales_query = db.query(SalesTransaction).filter(
            SalesTransaction.transaction_time >= start_date,
            SalesTransaction.transaction_time <= end_date,
        )
        sales_count = sales_query.count()

        outlet_reports.append({
            "outlet_id": outlet.id,
            "outlet_name": outlet.name,
            "valuation": round(outlet_valuation, 2),
            "purchases_total": round(outlet_purchases, 2),
            "sales_count": sales_count,
            "ingredient_count": len(ingredients),
        })

        total_valuation += outlet_valuation
        total_purchases += outlet_purchases
        total_sales_count += sales_count

    return {
        "reports": outlet_reports,
        "summary": {
            "total_valuation": round(total_valuation, 2),
            "total_purchases": round(total_purchases, 2),
            "total_sales_count": total_sales_count,
            "outlet_count": len(outlets),
            "period_days": days,
        },
        "generated_at": datetime.now(UTC).isoformat(),
    }
