"""Unit tests for analytics and report scheduling."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

from app.services.report_scheduler import (
    _calculate_next_run,
    generate_drill_down_report,
    schedule_report,
)


class TestGenerateDrillDownReport:
    def test_sales_drill_down(self) -> None:
        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = []

        result = generate_drill_down_report(
            db=db,
            metric="sales",
            start_date=datetime.now(UTC) - timedelta(days=30),
            end_date=datetime.now(UTC),
            granularity="daily",
        )

        assert result["metric"] == "sales"
        assert result["granularity"] == "daily"
        assert isinstance(result["data"], list)
        assert "total_transactions" in result

    def test_usage_drill_down(self) -> None:
        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = []

        result = generate_drill_down_report(
            db=db,
            metric="usage",
            start_date=datetime.now(UTC) - timedelta(days=30),
            end_date=datetime.now(UTC),
            granularity="daily",
        )

        assert result["metric"] == "usage"
        assert isinstance(result["data"], list)
        assert "total_used" in result

    def test_valuation_drill_down(self) -> None:
        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = []

        result = generate_drill_down_report(
            db=db,
            metric="valuation",
            start_date=datetime.now(UTC),
            end_date=datetime.now(UTC),
        )

        assert result["metric"] == "valuation"
        assert isinstance(result["data"], list)
        assert "total_valuation" in result

    def test_unknown_metric_raises(self) -> None:
        import pytest
        db = MagicMock()

        with pytest.raises(ValueError, match="Unknown metric"):
            generate_drill_down_report(
                db=db,
                metric="invalid",
                start_date=datetime.now(UTC),
                end_date=datetime.now(UTC),
            )


class TestScheduleReport:
    def test_daily_schedule(self) -> None:
        result = schedule_report(
            name="Daily Sales",
            schedule_type="daily",
            report_type="sales",
            email="test@example.com",
            format="csv",
        )

        assert result["name"] == "Daily Sales"
        assert result["schedule_type"] == "daily"
        assert result["status"] == "scheduled"
        assert "next_run" in result

    def test_weekly_schedule(self) -> None:
        result = schedule_report(
            name="Weekly Summary",
            schedule_type="weekly",
            report_type="consolidated",
        )

        assert result["schedule_type"] == "weekly"
        assert result["status"] == "scheduled"

    def test_monthly_schedule(self) -> None:
        result = schedule_report(
            name="Monthly Valuation",
            schedule_type="monthly",
            report_type="valuation",
            format="json",
        )

        assert result["schedule_type"] == "monthly"
        assert result["format"] == "json"


class TestCalculateNextRun:
    def test_daily_returns_future_date(self) -> None:
        result = _calculate_next_run("daily")
        next_run = datetime.fromisoformat(result)
        assert next_run > datetime.now(UTC)

    def test_weekly_returns_future_date(self) -> None:
        result = _calculate_next_run("weekly")
        next_run = datetime.fromisoformat(result)
        assert next_run > datetime.now(UTC)

    def test_monthly_returns_future_date(self) -> None:
        result = _calculate_next_run("monthly")
        next_run = datetime.fromisoformat(result)
        assert next_run > datetime.now(UTC)


class TestAnalyticsAPI:
    def test_analytics_router_registered(self) -> None:
        from app.api.v1.analytics import router
        assert router.prefix == "/analytics"
        assert len(router.routes) > 0
