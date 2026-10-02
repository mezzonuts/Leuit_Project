import csv
import io
from datetime import UTC

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, verify_license
from app.core.cache import get_cache, invalidate_cache, set_cache
from app.models.ingredient import Ingredient
from app.models.transaction import IngredientDailyUsage
from app.schemas.ingredient_schema import (
    IngredientCreate,
    IngredientListResponse,
    IngredientResponse,
    IngredientUpdate,
    StockOpnameRequest,
    StockOpnameResponse,
    ValuationItem,
    ValuationSummary,
)

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.get("", response_model=IngredientListResponse)
def list_ingredients(
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: str | None = Query(None),
    active_only: bool = Query(True),
):
    """List all ingredients with pagination and search."""
    query = db.query(Ingredient)

    if active_only:
        query = query.filter(Ingredient.is_active)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Ingredient.name.ilike(search_term),
                Ingredient.barcode_sku.ilike(search_term),
            )
        )

    total = query.count()
    items = query.order_by(Ingredient.name).offset(skip).limit(limit).all()

    return IngredientListResponse(
        items=[IngredientResponse.model_validate(item) for item in items],
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        total_pages=(total + limit - 1) // limit,
    )

@router.post("", response_model=IngredientResponse, status_code=status.HTTP_201_CREATED)
def create_ingredient(
    data: IngredientCreate,
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
):
    """Create new ingredient."""
    if data.barcode_sku:
        existing = db.query(Ingredient).filter(
            Ingredient.barcode_sku == data.barcode_sku
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Barcode/SKU already exists")

    ingredient = Ingredient(**data.model_dump())
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)
    invalidate_cache("valuation")
    invalidate_cache("inventory")
    return IngredientResponse.model_validate(ingredient)

@router.get("/valuation/summary", response_model=ValuationSummary)
def get_valuation_summary(
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
):
    """Get warehouse valuation summary."""
    cache_key = "valuation_summary"
    cached = get_cache(cache_key)
    if cached is not None:
        return ValuationSummary(**cached)

    ingredients = db.query(Ingredient).filter(Ingredient.is_active).all()

    total_valuation = sum(
        float(ing.current_stock) * float(ing.cost_per_unit) for ing in ingredients
    )
    low_stock_count = sum(
        1 for ing in ingredients
        if float(ing.current_stock) < float(ing.min_stock_threshold)
    )
    expired_soon_count = sum(
        1 for ing in ingredients
        if ing.shelf_life_days <= 3
    )

    summary = ValuationSummary(
        total_valuation=round(total_valuation, 2),
        total_ingredients=len(ingredients),
        low_stock_count=low_stock_count,
        expired_soon_count=expired_soon_count,
    )

    set_cache(cache_key, summary.model_dump(), ttl=300)
    return summary

@router.get("/valuation/items", response_model=list[ValuationItem])
def get_valuation_items(
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
):
    """Get detailed valuation per ingredient."""
    cache_key = "valuation_items"
    cached = get_cache(cache_key)
    if cached is not None:
        return [ValuationItem(**item) for item in cached]

    ingredients = db.query(Ingredient).filter(Ingredient.is_active).all()

    items = [
        ValuationItem(
            id=ing.id,
            name=ing.name,
            barcode_sku=ing.barcode_sku,
            current_stock=float(ing.current_stock),
            unit=ing.unit,
            cost_per_unit=float(ing.cost_per_unit),
            total_valuation=round(float(ing.current_stock) * float(ing.cost_per_unit), 2),
            shelf_life_days=ing.shelf_life_days,
            min_stock_threshold=float(ing.min_stock_threshold),
        )
        for ing in ingredients
    ]

    set_cache(cache_key, [item.model_dump() for item in items], ttl=300)
    return items

@router.get("/valuation/export-csv")
def export_valuation_csv(
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
):
    """Export valuation report as CSV."""
    ingredients = db.query(Ingredient).filter(Ingredient.is_active).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "ID", "Nama Bahan", "Barcode/SKU", "Sisa Stok", "Satuan",
        "HPP per Satuan", "Total Valuasi", "Masa Simpan (Hari)", "Minimum Threshold"
    ])

    for ing in ingredients:
        writer.writerow([
            ing.id,
            ing.name,
            ing.barcode_sku or "",
            float(ing.current_stock),
            ing.unit,
            float(ing.cost_per_unit),
            round(float(ing.current_stock) * float(ing.cost_per_unit), 2),
            ing.shelf_life_days,
            float(ing.min_stock_threshold),
        ])

    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=valuasi-aset.csv"}
    )

@router.get("/usage-trend")
def get_usage_trend(
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
    ingredient_id: int | None = Query(None),
    days: int = Query(30, ge=1, le=365),
):
    """Get ingredient usage trend for charting."""
    from datetime import datetime, timedelta

    end_date = datetime.now(UTC)
    start_date = end_date - timedelta(days=days)

    query = db.query(IngredientDailyUsage).filter(
        IngredientDailyUsage.usage_date >= start_date,
        IngredientDailyUsage.usage_date <= end_date,
    )

    if ingredient_id:
        query = query.filter(IngredientDailyUsage.ingredient_id == ingredient_id)

    usage = query.order_by(IngredientDailyUsage.usage_date).all()

    result = []
    for u in usage:
        result.append({
            "date": u.usage_date.isoformat(),
            "ingredient_id": u.ingredient_id,
            "ingredient_name": u.ingredient.name if u.ingredient else None,
            "total_quantity_used": float(u.total_quantity_used),
        })

    return result

@router.get("/alerts")
def get_critical_alerts(
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
):
    """Get critical alerts (low stock, expiring soon)."""
    ingredients = db.query(Ingredient).filter(Ingredient.is_active).all()

    alerts = []
    for ing in ingredients:
        stock_ratio = (float(ing.current_stock) / float(ing.min_stock_threshold) * 100) if ing.min_stock_threshold > 0 else 100

        if stock_ratio < 100:
            alerts.append({
                "id": ing.id,
                "name": ing.name,
                "type": "stock_low",
                "message": f"Stok {float(ing.current_stock)} {ing.unit} di bawah threshold {float(ing.min_stock_threshold)} {ing.unit}",
                "severity": "high" if stock_ratio < 50 else "medium",
                "ingredient_id": ing.id,
            })

        if ing.shelf_life_days <= 3:
            alerts.append({
                "id": ing.id,
                "name": ing.name,
                "type": "expiry",
                "message": f"Basi dalam {ing.shelf_life_days} hari",
                "severity": "high" if ing.shelf_life_days <= 1 else "medium",
                "ingredient_id": ing.id,
            })

    return alerts

@router.get("/{ingredient_id}", response_model=IngredientResponse)
def get_ingredient(
    ingredient_id: int,
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
):
    """Get single ingredient by ID."""
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return IngredientResponse.model_validate(ingredient)

@router.put("/{ingredient_id}", response_model=IngredientResponse)
def update_ingredient(
    ingredient_id: int,
    data: IngredientUpdate,
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
):
    """Update ingredient."""
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    if data.barcode_sku and data.barcode_sku != ingredient.barcode_sku:
        existing = db.query(Ingredient).filter(
            Ingredient.barcode_sku == data.barcode_sku
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Barcode/SKU already exists")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ingredient, field, value)

    db.commit()
    db.refresh(ingredient)
    invalidate_cache("valuation")
    invalidate_cache("inventory")
    return IngredientResponse.model_validate(ingredient)

@router.delete("/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingredient(
    ingredient_id: int,
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
):
    """Soft delete ingredient (archive)."""
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    ingredient.is_active = False
    db.commit()
    invalidate_cache("valuation")
    invalidate_cache("inventory")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/{ingredient_id}/stock-opname", response_model=StockOpnameResponse)
def stock_opname(
    ingredient_id: int,
    data: StockOpnameRequest,
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
):
    """Record stock opname (physical count adjustment)."""
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    previous_stock = float(ingredient.current_stock)
    new_stock = data.quantity
    difference = new_stock - previous_stock

    ingredient.current_stock = new_stock
    db.commit()

    return StockOpnameResponse(
        ingredient_id=ingredient_id,
        previous_stock=previous_stock,
        new_stock=new_stock,
        difference=difference,
        timestamp=func.now(),
    )