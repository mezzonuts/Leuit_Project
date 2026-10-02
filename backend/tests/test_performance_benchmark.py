"""Performance benchmarks using pytest-benchmark."""

from unittest.mock import MagicMock

import pytest

from app.core.security.key_envelope import KeyEnvelope, derive_sqlcipher_key
from app.services.forecaster import (
    _apply_weather_adjustment,
    calculate_avg_daily_usage,
    calculate_priority,
    calculate_recommended_order_qty,
    calculate_safety_stock,
    predict_consumption,
)


class TestForecasterBenchmarks:
    @pytest.mark.benchmark(group="forecaster")
    def test_calculate_avg_daily_usage(self, benchmark):
        db = MagicMock()
        records = [MagicMock(total_quantity_used=100.0) for _ in range(100)]
        db.query.return_value.filter.return_value.all.return_value = records

        result = benchmark(calculate_avg_daily_usage, db, 1)
        assert result == 100.0

    @pytest.mark.benchmark(group="forecaster")
    def test_predict_consumption(self, benchmark):
        result = benchmark(predict_consumption, 100.0, 30)
        assert result == 3000.0

    @pytest.mark.benchmark(group="forecaster")
    def test_calculate_safety_stock(self, benchmark):
        result = benchmark(calculate_safety_stock, 100.0)
        assert result == 120.0

    @pytest.mark.benchmark(group="forecaster")
    def test_calculate_recommended_order_qty(self, benchmark):
        result = benchmark(calculate_recommended_order_qty, 50.0, 700.0, 120.0, 140.0)
        assert result == 910.0

    @pytest.mark.benchmark(group="forecaster")
    def test_calculate_priority(self, benchmark):
        result = benchmark(calculate_priority, 50.0, 100.0)
        assert result == "high"


class TestWeatherBenchmarks:
    @pytest.mark.benchmark(group="weather")
    def test_apply_weather_adjustment(self, benchmark):
        result = benchmark(
            _apply_weather_adjustment, 100.0, {"rainfall_prob": 100, "temperature_avg": 27, "humidity": 75}
        )
        assert result < 100.0


class TestSecurityBenchmarks:
    @pytest.mark.benchmark(group="security")
    def test_key_envelope_generate(self, benchmark):
        result = benchmark(KeyEnvelope.generate_dek)
        assert len(result) == 32

    @pytest.mark.benchmark(group="security")
    def test_derive_sqlcipher_key(self, benchmark):
        dek = b'\x00' * 32
        result = benchmark(derive_sqlcipher_key, dek)
        assert len(result) == 64


class TestDatabaseBenchmarks:
    @pytest.mark.benchmark(group="database")
    def test_ingredient_creation(self, benchmark):
        from app.models.ingredient import Ingredient

        mock_db = MagicMock()

        def create_ingredient():
            ing = Ingredient(
                name="Test",
                unit="gram",
                cost_per_unit=1000,
                shelf_life_days=7,
                current_stock=100,
                min_stock_threshold=20,
            )
            mock_db.add(ing)
            mock_db.flush()
            ing.id = 1
            return ing

        result = benchmark(create_ingredient)
        assert result.id is not None