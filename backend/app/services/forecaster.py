"""Forecasting services: usage averaging, consumption prediction, restock priority."""
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.transaction import IngredientDailyUsage


def calculate_avg_daily_usage(db: Session, ingredient_id: int) -> float:
    """Average daily usage over last 30 days. Returns 0.0 when no records."""
    end_date = datetime.now(UTC)
    start_date = end_date - timedelta(days=30)
    records = (
        db.query(IngredientDailyUsage)
        .filter(
            IngredientDailyUsage.ingredient_id == ingredient_id,
            IngredientDailyUsage.usage_date >= start_date,
            IngredientDailyUsage.usage_date <= end_date,
        )
        .all()
    )
    if not records:
        return 0.0
    total = sum(float(r.total_quantity_used) for r in records)
    return total / len(records)


def predict_consumption(avg_daily_usage: float, days: int = 7) -> float:
    """Project consumption over a horizon in days (default 7)."""
    return avg_daily_usage * days


def calculate_safety_stock(
    min_stock_threshold: float, multiplier: float | None = None
) -> float:
    """Safety stock = threshold * multiplier (default: settings.SAFETY_STOCK_MULTIPLIER)."""
    if multiplier is None:
        multiplier = settings.SAFETY_STOCK_MULTIPLIER
    return float(min_stock_threshold) * multiplier


def calculate_recommended_order_qty(
    current_stock: float,
    predicted_7d: float,
    safety_stock: float,
    lead_time_demand: float,
) -> float:
    """Order qty = max(0, predicted + safety + lead time demand - current stock)."""
    total_needed = predicted_7d + safety_stock + lead_time_demand
    return max(0.0, total_needed - current_stock)


def calculate_priority(current_stock: float, min_stock_threshold: float) -> str:
    """Restock priority from stock ratio vs threshold: <100% high, <150% medium, else low."""
    if min_stock_threshold <= 0:
        return "low"
    ratio = current_stock / min_stock_threshold * 100
    if ratio < 100:
        return "high"
    if ratio < 150:
        return "medium"
    return "low"
