"""Advanced tests for forecasting services: Prophet integration, seasonality, holidays, weather."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from prophet import Prophet

from app.models.ingredient import Ingredient
from app.services.forecaster import (
    INDONESIAN_HOLIDAYS,
    _apply_weather_adjustment,
    _create_prophet_model,
    _detect_seasonality,
    _get_weather_data,
    _prepare_prophet_data,
    calculate_avg_daily_usage,
    calculate_priority,
    calculate_recommended_order_qty,
    calculate_safety_stock,
    forecast_30_day,
    forecast_restock_sheet,
    load_model,
    predict_consumption,
    save_model,
)
from app.services.weather_client import (
    _cache,
    _parse_bmkg_response,
)
from app.services.weather_client import (
    clear_cache as clear_weather_cache,
)

# ── Test Avg Daily Usage ──

class TestCalculateAvgDailyUsage:
    def test_no_records_returns_zero(self) -> None:
        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = []
        assert calculate_avg_daily_usage(db, 1) == 0.0

    def test_single_record(self) -> None:
        record = MagicMock()
        record.total_quantity_used = 100.0
        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = [record]
        assert calculate_avg_daily_usage(db, 1) == 100.0

    def test_multiple_records(self) -> None:
        records = []
        for qty in [50.0, 100.0, 150.0]:
            r = MagicMock()
            r.total_quantity_used = qty
            records.append(r)
        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = records
        assert calculate_avg_daily_usage(db, 1) == 100.0  # (50+100+150)/3


# ── Test Predict Consumption ──

class TestPredictConsumption:
    def test_basic_prediction(self) -> None:
        assert predict_consumption(10.0, 7) == 70.0

    def test_zero_usage(self) -> None:
        assert predict_consumption(0.0, 7) == 0.0

    def test_default_horizon(self) -> None:
        assert predict_consumption(10.0) == 70.0  # default 7 days

    def test_custom_days(self) -> None:
        assert predict_consumption(5.0, 30) == 150.0


# ── Test Safety Stock ──

class TestCalculateSafetyStock:
    def test_basic_calculation(self) -> None:
        assert calculate_safety_stock(100.0) == 120.0  # 100 * 1.2

    def test_custom_multiplier(self) -> None:
        assert calculate_safety_stock(100.0, 1.5) == 150.0

    def test_zero_threshold(self) -> None:
        assert calculate_safety_stock(0.0) == 0.0


# ── Test Recommended Order Qty ──

class TestCalculateRecommendedOrderQty:
    def test_needs_ordering(self) -> None:
        result = calculate_recommended_order_qty(
            current_stock=50.0,
            predicted_7d=200.0,
            safety_stock=60.0,
            lead_time_demand=30.0,
        )
        assert result == 240.0  # (200+60+30) - 50

    def test_no_ordering_needed(self) -> None:
        result = calculate_recommended_order_qty(
            current_stock=500.0,
            predicted_7d=200.0,
            safety_stock=60.0,
            lead_time_demand=30.0,
        )
        assert result == 0.0  # (200+60+30) - 500 = -210 → max(0, -210) = 0

    def test_exact_stock(self) -> None:
        result = calculate_recommended_order_qty(
            current_stock=290.0,
            predicted_7d=200.0,
            safety_stock=60.0,
            lead_time_demand=30.0,
        )
        assert result == 0.0  # 290 == 290


# ── Test Priority ──

class TestCalculatePriority:
    def test_high_priority(self) -> None:
        assert calculate_priority(50.0, 100.0) == "high"

    def test_medium_priority(self) -> None:
        assert calculate_priority(120.0, 100.0) == "medium"

    def test_low_priority(self) -> None:
        assert calculate_priority(200.0, 100.0) == "low"

    def test_zero_threshold(self) -> None:
        assert calculate_priority(100.0, 0.0) == "low"

    def test_exact_100_ratio(self) -> None:
        assert calculate_priority(100.0, 100.0) == "medium"

    def test_exact_150_ratio(self) -> None:
        assert calculate_priority(150.0, 100.0) == "low"


# ── Test Prophet Data Preparation ──

class TestPrepareProphetData:
    def test_no_records_returns_empty_df(self) -> None:
        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = []
        df = _prepare_prophet_data(db, 1)
        assert df.empty
        assert list(df.columns) == ["ds", "y"]

    def test_multiple_records(self) -> None:
        records = []
        # Create records in correct order (oldest first with ascending qty)
        for i, qty in enumerate([10.0, 20.0, 30.0]):
            r = MagicMock()
            r.usage_date = datetime.now(UTC) - timedelta(days=2 - i)  # oldest to newest
            r.total_quantity_used = qty
            records.append(r)
        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = records
        df = _prepare_prophet_data(db, 1)
        assert len(df) == 3
        assert list(df.columns) == ["ds", "y"]
        assert df["y"].tolist() == [10.0, 20.0, 30.0]


# ── Test Prophet Model Creation ──

class TestCreateProphetModel:
    def test_creates_model_with_holidays(self) -> None:
        model = _create_prophet_model()
        assert model is not None
        assert model.yearly_seasonality is True
        assert model.weekly_seasonality is True

    def test_model_has_indonesian_holidays(self) -> None:
        model = _create_prophet_model()
        # Check holidays were added - holidays passed to constructor
        assert model.holidays is not None
        assert len(model.holidays) > 0


# ── Test Weather Adjustment ──

class TestWeatherAdjustment:
    def test_rain_reduces_prediction(self) -> None:
        base = 100.0
        weather = {"rainfall_prob": 100, "temperature_avg": 27, "humidity": 75}
        adjusted = _apply_weather_adjustment(base, weather)
        # Rain 100% → rain_factor = 1 - 1.0 * 0.15 = 0.85
        assert adjusted < 100.0
        assert adjusted == pytest.approx(85.0, rel=0.01)

    def test_high_temp_increases(self) -> None:
        base = 100.0
        # 30°C = 3 degrees above 27 → 3 * 0.02 = 0.06
        weather = {"rainfall_prob": 0, "temperature_avg": 30, "humidity": 75}
        adjusted = _apply_weather_adjustment(base, weather)
        assert adjusted > 100.0

    def test_no_weather_returns_same(self) -> None:
        assert _apply_weather_adjustment(100.0, None) == 100.0

    def test_high_humidity_reduces(self) -> None:
        base = 100.0
        # humidity 90% → 10% above 80 → 10 * 0.005 = 0.05 reduction
        weather = {"rainfall_prob": 0, "temperature_avg": 27, "humidity": 90}
        adjusted = _apply_weather_adjustment(base, weather)
        assert adjusted < 100.0


# ── Test Indonesian Holidays ──

class TestIndonesianHolidays:
    def test_has_holidays(self) -> None:
        assert len(INDONESIAN_HOLIDAYS) > 0

    def test_has_2024_holidays(self) -> None:
        assert any(h.startswith("2024-") for h in INDONESIAN_HOLIDAYS)

    def test_has_2025_holidays(self) -> None:
        assert any(h.startswith("2025-") for h in INDONESIAN_HOLIDAYS)

    def test_has_2026_holidays(self) -> None:
        assert any(h.startswith("2026-") for h in INDONESIAN_HOLIDAYS)


# ── Test Seasonality Detection ──

class TestSeasonalityDetection:
    def test_detects_seasonality(self) -> None:
        model = _create_prophet_model()
        df = pd.DataFrame({
            "ds": pd.date_range("2024-01-01", periods=400),
            "y": [10.0] * 400,
        })
        model.fit(df)

        result = _detect_seasonality(model, df)

        assert "yearly" in result
        assert "weekly" in result
        assert "has_yearly_data" in result
        assert "has_weekly_data" in result


# ── Test Weather Adjustment Integration ──

class TestWeatherIntegration:
    def test_get_weather_data_success(self) -> None:
        # Mock the async function in weather_client
        async def mock_get_weather(adm4_code=None):
            return [
                MagicMock(
                    temperature_min=22.0,
                    temperature_max=30.0,
                    humidity=75.0,
                    rainfall_probability=30.0,
                    weather_description="Cerah",
                )
            ]

        with patch("app.services.weather_client.get_weather_forecast", side_effect=mock_get_weather):
            # _get_weather_data creates its own event loop
            result = _get_weather_data()

            assert result is not None
            assert "temperature_avg" in result
            assert result["temperature_avg"] == 26.0  # (22+30)/2

    def test_apply_weather_to_forecast(self) -> None:
        # Rain reduces consumption
        assert _apply_weather_adjustment(100.0, {"rainfall_prob": 100, "temperature_avg": 27, "humidity": 75}) < 100
        # Hot weather increases
        assert _apply_weather_adjustment(100.0, {"rainfall_prob": 0, "temperature_avg": 35, "humidity": 75}) > 100


# ── Test Model Persistence ──

class TestModelPersistence:
    def test_save_and_load_model(self, tmp_path) -> None:
        model = Prophet()
        model.fit(pd.DataFrame({
            "ds": pd.date_range("2024-01-01", periods=100),
            "y": [10.0] * 100,
        }))

        # Mock MODEL_DIR to use tmp_path
        import app.services.forecaster as forecaster_module
        original_dir = forecaster_module.MODEL_DIR
        forecaster_module.MODEL_DIR = Path(tmp_path)

        try:
            path = save_model(1, model)
            assert path.exists()

            loaded = load_model(1)
            assert loaded is not None
        finally:
            forecaster_module.MODEL_DIR = original_dir


# ── Test Weather Data Parsing ──

class TestWeatherParsing:
    def test_parse_bmkg_response(self) -> None:
        raw = {
            "data": [
                {
                    "date": "2026-01-01",
                    "temp_min": 22.0,
                    "temp_max": 30.0,
                    "humidity": 75.0,
                    "rain_prob": 30.0,
                    "weather_desc": "Cerah",
                }
            ]
        }
        result = _parse_bmkg_response(raw)
        assert len(result) == 1
        assert result[0]["temperature_min"] == 22.0
        assert result[0]["temperature_max"] == 30.0

    def test_parse_empty_response(self) -> None:
        assert _parse_bmkg_response({}) == []
        assert _parse_bmkg_response({"data": []}) == []


# ── Test Cache ──

class TestCache:
    def test_clear_cache(self) -> None:
        _cache["test"] = ([], datetime.now(UTC))
        clear_weather_cache()
        assert len(_cache) == 0


# ── Test 30-Day Forecast Endpoint (Integration) ──

class TestForecast30DayEndpoint:
    def test_forecast_30_day_returns_structure(self) -> None:
        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = []

        result = forecast_30_day(db, 1)

        assert "predictions" in result
        assert "model_info" in result
        assert "weather_adjusted" in result
        assert isinstance(result["predictions"], list)


# ── Test Restock Sheet with Prophet ──

class TestRestockSheetWithProphet:
    def test_forecast_restock_sheet_structure(self) -> None:
        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = []

        result = forecast_restock_sheet(db=db)

        assert "items" in result
        assert "total_estimated_cost" in result
        assert "high_priority_count" in result
        assert "generated_at" in result

    def test_with_ingredients(self) -> None:
        db = MagicMock()
        mock_ing = MagicMock(spec=Ingredient)
        mock_ing.id = 1
        mock_ing.name = "Test"
        mock_ing.unit = "gram"
        mock_ing.current_stock = 100
        mock_ing.min_stock_threshold = 20
        mock_ing.lead_time_days = 2
        mock_ing.cost_per_unit = 10000
        mock_ing.is_active = True

        db.query.return_value.filter.return_value.all.return_value = [mock_ing]

        # Mock the forecast call
        with patch("app.services.forecaster.forecast_with_prophet") as mock_forecast:
            mock_forecast.return_value = {
                "predictions": [{"yhat": 100.0} for _ in range(7)],
            }

            result = forecast_restock_sheet(db=MagicMock())
            assert "items" in result
