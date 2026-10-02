from datetime import UTC, datetime, timedelta

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, verify_license
from app.core.config import settings
from app.schemas.forecast_schema import (
    Forecast30DayResponse,
    ForecastItemResponse,
    RestockSheetResponse,
    WeatherForecastResponse,
)
from app.services.forecaster import forecast_30_day, forecast_restock_sheet

router = APIRouter(prefix="/forecast", tags=["Forecast & Weather"])

@router.get("/weather", response_model=list[WeatherForecastResponse])
async def get_weather_forecast(
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
    adm4: str | None = Query(None),
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
                date=item.get("date", datetime.now(UTC)),
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
                date=datetime.now(UTC) + timedelta(days=i),
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
    adm4: str | None = Query(None),
    horizon_days: int = Query(7, ge=1, le=30),
):
    """
    Generate restock recommendations for next N days (default 7, max 30).
    Uses Prophet forecasting with weather adjustment.
    """
    try:
        result = forecast_restock_sheet(
            db=db,
            adm4_code=adm4,
            horizon_days=horizon_days,
        )
        return RestockSheetResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate restock sheet: {str(e)}")


@router.get("/30-day", response_model=Forecast30DayResponse)
def get_30_day_forecast(
    ingredient_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
    adm4: str | None = Query(None),
):
    """
    Get 30-day demand forecast for a specific ingredient.
    Uses Prophet forecasting with weather adjustment and Indonesian holidays.
    """
    try:
        result = forecast_30_day(
            db=db,
            ingredient_id=ingredient_id,
            adm4_code=adm4,
        )
        
        # Convert predictions to schema
        predictions = [
            ForecastItemResponse(
                date=p["date"],
                yhat=p["yhat"],
                yhat_lower=p["yhat_lower"],
                yhat_upper=p["yhat_upper"],
                weather_adjusted=p.get("weather_adjusted", False),
            )
            for p in result.get("predictions", [])
        ]
        
        return Forecast30DayResponse(
            ingredient_id=ingredient_id,
            predictions=predictions,
            model_info=result.get("model_info", {}),
            weather_adjusted=result.get("weather_adjusted", False),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate forecast: {str(e)}")