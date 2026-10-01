"""Unit tests for forecasting services."""
from unittest.mock import MagicMock


class TestCalculateAvgDailyUsage:
    def test_no_records_returns_zero(self):
        from app.services.forecaster import calculate_avg_daily_usage
        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = []
        assert calculate_avg_daily_usage(db, 1) == 0.0

    def test_single_record(self):
        from app.services.forecaster import calculate_avg_daily_usage
        record = MagicMock()
        record.total_quantity_used = 100.0
        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = [record]
        assert calculate_avg_daily_usage(db, 1) == 100.0

    def test_multiple_records(self):
        from app.services.forecaster import calculate_avg_daily_usage
        records = []
        for qty in [50.0, 100.0, 150.0]:
            r = MagicMock()
            r.total_quantity_used = qty
            records.append(r)
        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = records
        assert calculate_avg_daily_usage(db, 1) == 100.0  # (50+100+150)/3


class TestPredictConsumption:
    def test_basic_prediction(self):
        from app.services.forecaster import predict_consumption
        assert predict_consumption(10.0, 7) == 70.0

    def test_zero_usage(self):
        from app.services.forecaster import predict_consumption
        assert predict_consumption(0.0, 7) == 0.0

    def test_default_horizon(self):
        from app.services.forecaster import predict_consumption
        assert predict_consumption(10.0) == 70.0  # default 7 days


class TestCalculateSafetyStock:
    def test_basic_calculation(self):
        from app.services.forecaster import calculate_safety_stock
        assert calculate_safety_stock(100.0) == 120.0  # 100 * 1.2

    def test_custom_multiplier(self):
        from app.services.forecaster import calculate_safety_stock
        assert calculate_safety_stock(100.0, 1.5) == 150.0

    def test_zero_threshold(self):
        from app.services.forecaster import calculate_safety_stock
        assert calculate_safety_stock(0.0) == 0.0


class TestCalculateRecommendedOrderQty:
    def test_needs_ordering(self):
        from app.services.forecaster import calculate_recommended_order_qty
        result = calculate_recommended_order_qty(
            current_stock=50.0,
            predicted_7d=200.0,
            safety_stock=60.0,
            lead_time_demand=30.0,
        )
        assert result == 240.0  # (200+60+30) - 50

    def test_no_ordering_needed(self):
        from app.services.forecaster import calculate_recommended_order_qty
        result = calculate_recommended_order_qty(
            current_stock=500.0,
            predicted_7d=200.0,
            safety_stock=60.0,
            lead_time_demand=30.0,
        )
        assert result == 0.0  # (200+60+30) - 500 = -210 → max(0, -210) = 0

    def test_exact_stock(self):
        from app.services.forecaster import calculate_recommended_order_qty
        result = calculate_recommended_order_qty(
            current_stock=290.0,
            predicted_7d=200.0,
            safety_stock=60.0,
            lead_time_demand=30.0,
        )
        assert result == 0.0  # 290 == 290


class TestCalculatePriority:
    def test_high_priority(self):
        from app.services.forecaster import calculate_priority
        assert calculate_priority(50.0, 100.0) == "high"

    def test_medium_priority(self):
        from app.services.forecaster import calculate_priority
        assert calculate_priority(120.0, 100.0) == "medium"

    def test_low_priority(self):
        from app.services.forecaster import calculate_priority
        assert calculate_priority(200.0, 100.0) == "low"

    def test_zero_threshold(self):
        from app.services.forecaster import calculate_priority
        assert calculate_priority(100.0, 0.0) == "low"

    def test_exact_100_ratio(self):
        from app.services.forecaster import calculate_priority
        assert calculate_priority(100.0, 100.0) == "medium"

    def test_exact_150_ratio(self):
        from app.services.forecaster import calculate_priority
        assert calculate_priority(150.0, 100.0) == "low"


class TestWeatherClient:
    def test_mock_forecast_returns_3_days(self):
        from app.services.weather_client import _mock_forecast
        result = _mock_forecast()
        assert len(result) == 3

    def test_mock_forecast_fields(self):
        from app.services.weather_client import _mock_forecast
        result = _mock_forecast()
        assert "date" in result[0]
        assert "temperature_min" in result[0]
        assert "temperature_max" in result[0]
        assert "humidity" in result[0]
        assert "rainfall_probability" in result[0]
        assert "weather_description" in result[0]

    def test_parse_bmkg_response(self):
        from app.services.weather_client import _parse_bmkg_response
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

    def test_parse_empty_response(self):
        from app.services.weather_client import _parse_bmkg_response
        assert _parse_bmkg_response({}) == []
        assert _parse_bmkg_response({"data": []}) == []

    def test_clear_cache(self):
        from app.services.weather_client import _cache, clear_cache
        _cache["test"] = ([], datetime_now())
        clear_cache()
        assert len(_cache) == 0


def datetime_now():
    from datetime import UTC, datetime
    return datetime.now(UTC)
