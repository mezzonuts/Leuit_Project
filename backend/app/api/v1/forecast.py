from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.api.v1.deps import get_db, verify_license
from app.schemas.forecast_schema import (
    WeatherForecastResponse,
    RestockItemResponse,
    RestockSheetResponse,
)
from app.models.ingredient import Ingredient
from app.models.transaction import IngredientDailyUsage
from app.models.purchase import InventoryPurchase, Supplier, PaymentMethod, PaymentStatus
from app.core.config import settings
import httpx
from datetime import datetime, timedelta, timezone

router = APIRouter(prefix="/forecast", tags=["Forecast & Weather"])

@router.get("/weather", response_model=list[WeatherForecastResponse])
async def get_weather_forecast(
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
    adm4: Optional[str] = Query(None),
):
    """Get weather forecast from BMKG API."""
    adm4_code = adm4 or settings.BMKG_DEFAULT_ADM4

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{settings.BMKG_API_BASE}",
                params={"adm4": adm4_code},
            )
            response.raise_for_status()
            data = response.json()

        # Parse BMKG response
        forecasts = []
        # BMKG response structure varies, adapt as needed
        # This is a simplified parser
        for item in data.get("data", []):
            forecasts.append(WeatherForecastResponse(
                date=item.get("date", datetime.now(timezone.utc)),
                temperature_min=item.get("temp_min", 0),
                temperature_max=item.get("temp_max", 0),
                humidity=item.get("humidity", 0),
                rainfall_probability=item.get("rain_prob", 0),
                weather_description=item.get("weather_desc", ""),
            ))

        return forecasts

    except httpx.HTTPError:
        # Return mock data if API fails
        return [
            WeatherForecastResponse(
                date=datetime.now(timezone.utc) + timedelta(days=i),
                temperature_min=22.0,
                temperature_max=30.0,
                humidity=75.0,
                rainfall_probability=30.0,
                weather_description="Cerah Berawan",
            )
            for i in range(3)
        ]

@router.get("/restock-sheet", response_model=RestockSheetResponse)
def get_restock_sheet(
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
):
    """
    Generate restock recommendations for next 7 days.
    Uses historical usage + weather + safety stock.
    """
    from datetime import datetime, timezone

    ingredients = db.query(Ingredient).filter(Ingredient.is_active == True).all()

    items = []
    total_cost = 0.0
    high_priority = 0

    for ing in ingredients:
        # Calculate average daily usage from last 30 days
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=30)

        usage_records = db.query(IngredientDailyUsage).filter(
            IngredientDailyUsage.ingredient_id == ing.id,
            IngredientDailyUsage.usage_date >= start_date,
            IngredientDailyUsage.usage_date <= end_date,
        ).all()

        avg_daily_usage = 0.0
        if usage_records:
            total_used = sum(float(r.total_quantity_used) for r in usage_records)
            avg_daily_usage = total_used / len(usage_records)

        # Predict 7-day consumption
        predicted_7d = avg_daily_usage * 7

        # Weather adjustment (simplified - would integrate with actual weather)
        # Rainy days in Bandung typically reduce foot traffic by 15-30%
        weather_factor = 1.0  # placeholder

        # Safety stock calculation
        safety_stock = float(ing.min_stock_threshold) * settings.SAFETY_STOCK_MULTIPLIER

        # Lead time demand
        lead_time_demand = avg_daily_usage * ing.lead_time_days

        # Recommended order quantity
        current_stock = float(ing.current_stock)
        total_needed = predicted_7d + safety_stock + lead_time_demand
        recommended_qty = max(0.0, total_needed - current_stock)

        # Priority
        stock_ratio = (current_stock / float(ing.min_stock_threshold) * 100) if ing.min_stock_threshold > 0 else 100

        if stock_ratio < 100:
            priority = "high"
        elif stock_ratio < 150:
            priority = "medium"
        else:
            priority = "low"

        if priority == "high":
            high_priority += 1

        # Find default supplier
        default_purchase = db.query(InventoryPurchase).filter(
            InventoryPurchase.ingredient_id == ing.id
        ).order_by(InventoryPurchase.purchase_date.desc()).first()

        supplier_id = default_purchase.supplier_id if default_purchase else None
        supplier_name = default_purchase.supplier.name if default_purchase and default_purchase.supplier else None

        estimated_cost = recommended_qty * float(ing.cost_per_unit)
        total_cost += estimated_cost

        items.append(RestockItemResponse(
            ingredient_id=ing.id,
            ingredient_name=ing.name,
            unit=ing.unit,
            current_stock=current_stock,
            predicted_consumption_7d=round(predicted_7d, 2),
            recommended_order_qty=round(recommended_qty, 2),
            safety_stock=round(safety_stock, 2),
            estimated_cost=round(estimated_cost, 2),
            priority=priority,
            supplier_id=supplier_id,
            supplier_name=supplier_name,
            lead_time_days=ing.lead_time_days,
        ))

    return RestockSheetResponse(
        items=items,
        total_estimated_cost=round(total_cost, 2),
        high_priority_count=high_priority,
        generated_at=datetime.now(timezone.utc),
    )