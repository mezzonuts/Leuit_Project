"""Forecasting services: usage averaging, consumption prediction, restock priority.

Enhanced with Prophet integration for advanced forecasting.
"""
from __future__ import annotations

import logging
import pickle
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
from prophet import Prophet
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.transaction import IngredientDailyUsage

logger = logging.getLogger(__name__)

# Model storage directory
MODEL_DIR = Path(settings.FORECAST_MODEL_DIR) if hasattr(settings, 'FORECAST_MODEL_DIR') else Path("./models/forecast")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Indonesian holidays (2024-2026)
INDONESIAN_HOLIDAYS = [
    # 2024
    "2024-01-01", "2024-02-10", "2024-03-11", "2024-04-10", "2024-04-11",
    "2024-05-01", "2024-05-09", "2024-05-23", "2024-06-01", "2024-06-17",
    "2024-07-17", "2024-08-17", "2024-09-16", "2024-12-25",
    # 2025
    "2025-01-01", "2025-01-29", "2025-03-30", "2025-04-18", "2025-04-19",
    "2025-05-01", "2025-05-29", "2025-06-01", "2025-06-06", "2025-06-27",
    "2025-07-19", "2025-08-17", "2025-09-05", "2025-12-25",
    # 2026
    "2026-01-01", "2026-02-17", "2026-03-20", "2026-04-03", "2026-04-04",
    "2026-05-01", "2026-05-14", "2026-05-18", "2026-05-28", "2026-06-01",
    "2026-06-15", "2026-07-20", "2026-08-17", "2026-09-03", "2026-12-25",
]


def calculate_avg_daily_usage(db: Session, ingredient_id: int, days: int = 30) -> float:
    """Average daily usage over N days. Returns 0.0 when no records."""
    end_date = datetime.now(UTC)
    start_date = end_date - timedelta(days=days)
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


# ========== Prophet Forecasting ==========

def _prepare_prophet_data(db: Session, ingredient_id: int, days: int = 90) -> pd.DataFrame:
    """Prepare historical data for Prophet training."""
    end_date = datetime.now(UTC)
    start_date = end_date - timedelta(days=days)
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
        return pd.DataFrame(columns=["ds", "y"])
    
    df = pd.DataFrame([
        {"ds": r.usage_date, "y": float(r.total_quantity_used)}
        for r in records
    ])
    df["ds"] = pd.to_datetime(df["ds"])
    df = df.sort_values("ds")
    return df


def _create_prophet_model(
    yearly_seasonality: bool = True,
    weekly_seasonality: bool = True,
    daily_seasonality: bool = False,
    seasonality_mode: str = "multiplicative",
) -> Prophet:
    """Create Prophet model with Indonesian holidays."""
    # Prepare holidays dataframe
    holidays_df = pd.DataFrame({
        "holiday": "indonesian_holiday",
        "ds": pd.to_datetime(INDONESIAN_HOLIDAYS),
        "lower_window": 0,
        "upper_window": 1,
    })
    
    model = Prophet(
        yearly_seasonality=yearly_seasonality,
        weekly_seasonality=weekly_seasonality,
        daily_seasonality=daily_seasonality,
        seasonality_mode=seasonality_mode,
        interval_width=0.95,
        holidays=holidays_df,
    )
    
    return model


def _train_prophet_model(db: Session, ingredient_id: int, days: int = 90) -> tuple[Prophet, pd.DataFrame]:
    """Train Prophet model on historical data."""
    df = _prepare_prophet_data(db, ingredient_id, days)
    
    if df.empty or len(df) < 10:
        logger.warning(f"Insufficient data for ingredient {ingredient_id}: {len(df)} records")
        return None, df
    
    model = _create_prophet_model()
    model.fit(df)
    
    return model, df


def _get_model_path(ingredient_id: int) -> Path:
    """Get model file path."""
    return MODEL_DIR / f"prophet_ingredient_{ingredient_id}.pkl"


def save_model(ingredient_id: int, model: Prophet) -> Path:
    """Save trained model to disk."""
    path = _get_model_path(ingredient_id)
    with open(path, "wb") as f:
        pickle.dump(model, f)
    logger.info(f"Model saved for ingredient {ingredient_id} at {path}")
    return path


def load_model(ingredient_id: int) -> Prophet | None:
    """Load trained model from disk."""
    path = _get_model_path(ingredient_id)
    if not path.exists():
        return None
    with open(path, "rb") as f:
        model = pickle.load(f)
    logger.info(f"Model loaded for ingredient {ingredient_id} from {path}")
    return model


def _get_weather_data(adm4_code: str | None = None) -> dict[str, float] | None:
    """Get weather data for forecasting adjustment."""
    try:
        import asyncio

        from app.services.weather_client import get_weather_forecast
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        forecast = loop.run_until_complete(get_weather_forecast(adm4_code))
        loop.close()
        
        if forecast:
            # Use first day forecast for adjustment
            first_day = forecast[0]
            return {
                "temperature_avg": (first_day.temperature_min + first_day.temperature_max) / 2,
                "humidity": first_day.humidity,
                "rainfall_prob": first_day.rainfall_probability,
            }
    except Exception as e:
        logger.warning(f"Failed to get weather data: {e}")
    return None


def _apply_weather_adjustment(prediction: float, weather: dict[str, float] | None) -> float:
    """Adjust prediction based on weather conditions."""
    if not weather:
        return prediction
    
    # Rain reduces consumption (people stay home)
    rain_factor = 1.0 - (weather.get("rainfall_prob", 0) / 100) * 0.15
    
    # High temperature increases cold drink consumption
    temp = weather.get("temperature_avg", 27)
    temp_factor = 1.0 + max(0, (temp - 27) * 0.02)
    
    # High humidity slightly reduces consumption
    humidity = weather.get("humidity", 75)
    humidity_factor = 1.0 - max(0, (humidity - 80) * 0.005)
    
    adjustment = rain_factor * temp_factor * humidity_factor
    return prediction * adjustment


def forecast_with_prophet(
    db: Session,
    ingredient_id: int,
    horizon_days: int = 30,
    retrain: bool = False,
    adm4_code: str | None = None,
) -> dict[str, Any]:
    """
    Generate forecast using Prophet model.
    
    Returns dict with:
    - predictions: list of {date, yhat, yhat_lower, yhat_upper}
    - model_info: training info
    - weather_adjusted: whether weather adjustment was applied
    """
    # Try to load existing model
    model = None if retrain else load_model(ingredient_id)
    
    if model is None:
        model, df = _train_prophet_model(db, ingredient_id)
        if model is None:
            return {
                "predictions": [],
                "model_info": {"error": "Insufficient data for training"},
                "weather_adjusted": False,
            }
        # Save new model
        save_model(ingredient_id, model)
    else:
        df = _prepare_prophet_data(db, ingredient_id)
    
    # Get weather data for adjustment
    weather = _get_weather_data()
    
    # Make future predictions
    future = model.make_future_dataframe(periods=horizon_days, freq="D")
    forecast = model.predict(future)
    
    # Extract future predictions (last horizon_days)
    future_forecast = forecast.tail(horizon_days)
    
    predictions = []
    for _, row in future_forecast.iterrows():
        yhat = max(0, row["yhat"])
        yhat_lower = max(0, row["yhat_lower"])
        yhat_upper = max(0, row["yhat_upper"])
        
        # Apply weather adjustment
        if adm4_code:
            weather = _get_weather_data()
        yhat_adj = _apply_weather_adjustment(yhat, weather)
        yhat_lower_adj = _apply_weather_adjustment(yhat_lower, weather)
        yhat_upper_adj = _apply_weather_adjustment(yhat_upper, weather)
        
        predictions.append({
            "date": row["ds"].strftime("%Y-%m-%d"),
            "yhat": round(yhat_adj, 2),
            "yhat_lower": round(yhat_lower_adj, 2),
            "yhat_upper": round(yhat_upper_adj, 2),
            "weather_adjusted": weather is not None,
        })
    
    # Detect seasonality
    seasonality_info = _detect_seasonality(model, df)
    
    return {
        "predictions": predictions,
        "model_info": {
            "ingredient_id": ingredient_id,
            "training_records": len(_prepare_prophet_data(db, ingredient_id)),
            "horizon_days": horizon_days,
            "seasonality": seasonality_info,
            "model_version": "1.0",
        },
        "weather_adjusted": weather is not None,
    }


def _detect_seasonality(model: Prophet, df: pd.DataFrame) -> dict[str, Any]:
    """Detect and describe seasonality patterns."""
    seasonality = {
        "yearly": model.yearly_seasonality,
        "weekly": model.weekly_seasonality,
        "daily": model.daily_seasonality,
    }
    
    # Check if we have enough data for yearly seasonality
    if len(df) >= 365:
        seasonality["has_yearly_data"] = True
    else:
        seasonality["has_yearly_data"] = False
    
    if len(df) >= 14:
        seasonality["has_weekly_data"] = True
    else:
        seasonality["has_weekly_data"] = False
    
    return seasonality


def forecast_30_day(
    db: Session,
    ingredient_id: int,
    adm4_code: str | None = None,
) -> dict[str, Any]:
    """
    Generate 30-day forecast for an ingredient.
    
    This is the main entry point for the 30-day forecast endpoint.
    """
    return forecast_with_prophet(
        db=db,
        ingredient_id=ingredient_id,
        horizon_days=30,
        retrain=False,
        adm4_code=adm4_code,
    )


def forecast_restock_sheet(
    db: Session,
    adm4_code: str | None = None,
    horizon_days: int = 7,
) -> dict[str, Any]:
    """
    Generate restock recommendations for all active ingredients.
    
    Uses Prophet forecasting with weather adjustment.
    """
    from app.models.ingredient import Ingredient
    from app.models.purchase import InventoryPurchase
    
    ingredients = db.query(Ingredient).filter(Ingredient.is_active).all()
    
    items = []
    total_cost = 0.0
    high_priority = 0
    
    for ing in ingredients:
        # Use Prophet for forecasting
        forecast = forecast_with_prophet(
            db=db,
            ingredient_id=ing.id,
            horizon_days=horizon_days,
            retrain=False,
            adm4_code=adm4_code,
        )
        
        # Sum predictions for the horizon
        predicted_consumption = sum(p["yhat"] for p in forecast.get("predictions", []))
        
        # Safety stock calculation
        safety_stock = float(ing.min_stock_threshold) * settings.SAFETY_STOCK_MULTIPLIER
        
        # Lead time demand
        avg_daily = predicted_consumption / horizon_days if horizon_days > 0 else 0
        lead_time_demand = avg_daily * ing.lead_time_days
        
        # Recommended order quantity
        current_stock = float(ing.current_stock)
        total_needed = predicted_consumption + safety_stock + lead_time_demand
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
        
        items.append({
            "ingredient_id": ing.id,
            "ingredient_name": ing.name,
            "unit": ing.unit,
            "current_stock": current_stock,
            "predicted_consumption_7d": round(predicted_consumption, 2),
            "recommended_order_qty": round(recommended_qty, 2),
            "safety_stock": round(safety_stock, 2),
            "estimated_cost": round(estimated_cost, 2),
            "priority": priority,
            "supplier_id": supplier_id,
            "supplier_name": supplier_name,
            "lead_time_days": ing.lead_time_days,
        })
    
    return {
        "items": items,
        "total_estimated_cost": round(total_cost, 2),
        "high_priority_count": high_priority,
        "generated_at": datetime.now(UTC),
    }