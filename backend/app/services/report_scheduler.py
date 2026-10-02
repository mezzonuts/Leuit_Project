"""Report scheduling service for automated report generation and export."""
from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.models.ingredient import Ingredient
from app.models.transaction import IngredientDailyUsage, SalesTransaction

logger = logging.getLogger(__name__)


def generate_drill_down_report(
    db: Session,
    metric: str,
    start_date: datetime,
    end_date: datetime,
    granularity: str = "daily",
    ingredient_id: int | None = None,
) -> dict[str, Any]:
    """
    Generate drill-down report data.

    Metrics: 'sales', 'usage', 'valuation'
    Granularity: 'daily', 'weekly', 'monthly'
    """
    if metric == "sales":
        return _generate_sales_drill_down(db, start_date, end_date, granularity)
    elif metric == "usage":
        return _generate_usage_drill_down(db, start_date, end_date, granularity, ingredient_id)
    elif metric == "valuation":
        return _generate_valuation_drill_down(db)
    else:
        raise ValueError(f"Unknown metric: {metric}")


def _generate_sales_drill_down(
    db: Session,
    start_date: datetime,
    end_date: datetime,
    granularity: str,
) -> dict[str, Any]:
    """Generate sales drill-down report."""
    transactions = db.query(SalesTransaction).filter(
        SalesTransaction.transaction_time >= start_date,
        SalesTransaction.transaction_time <= end_date,
    ).all()

    # Group by period
    buckets: dict[str, dict[str, Any]] = {}

    for tx in transactions:
        if granularity == "daily":
            key = tx.transaction_time.strftime("%Y-%m-%d")
        elif granularity == "weekly":
            key = tx.transaction_time.strftime("%Y-W%W")
        elif granularity == "monthly":
            key = tx.transaction_time.strftime("%Y-%m")
        else:
            key = tx.transaction_time.strftime("%Y-%m-%d")

        if key not in buckets:
            buckets[key] = {
                "period": key,
                "transaction_count": 0,
                "total_quantity": 0,
                "unique_items": set(),
            }

        buckets[key]["transaction_count"] += 1
        buckets[key]["total_quantity"] += tx.quantity
        if tx.menu_item_id:
            buckets[key]["unique_items"].add(tx.menu_item_id)

    # Convert sets to counts
    result = []
    for key in sorted(buckets.keys()):
        bucket = buckets[key]
        bucket["unique_items"] = len(bucket["unique_items"])
        result.append(bucket)

    return {
        "metric": "sales",
        "granularity": granularity,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "data": result,
        "total_transactions": sum(b["transaction_count"] for b in result),
        "generated_at": datetime.now(UTC).isoformat(),
    }


def _generate_usage_drill_down(
    db: Session,
    start_date: datetime,
    end_date: datetime,
    granularity: str,
    ingredient_id: int | None = None,
) -> dict[str, Any]:
    """Generate ingredient usage drill-down report."""
    query = db.query(IngredientDailyUsage).filter(
        IngredientDailyUsage.usage_date >= start_date,
        IngredientDailyUsage.usage_date <= end_date,
    )

    if ingredient_id:
        query = query.filter(IngredientDailyUsage.ingredient_id == ingredient_id)

    records = query.all()

    buckets: dict[str, dict[str, Any]] = {}

    for record in records:
        if granularity == "daily":
            key = record.usage_date.strftime("%Y-%m-%d")
        elif granularity == "weekly":
            key = record.usage_date.strftime("%Y-W%W")
        elif granularity == "monthly":
            key = record.usage_date.strftime("%Y-%m")
        else:
            key = record.usage_date.strftime("%Y-%m-%d")

        if key not in buckets:
            buckets[key] = {
                "period": key,
                "total_used": 0.0,
                "record_count": 0,
            }

        buckets[key]["total_used"] += float(record.total_quantity_used)
        buckets[key]["record_count"] += 1

    result = []
    for key in sorted(buckets.keys()):
        bucket = buckets[key]
        bucket["total_used"] = round(bucket["total_used"], 2)
        result.append(bucket)

    return {
        "metric": "usage",
        "granularity": granularity,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "ingredient_id": ingredient_id,
        "data": result,
        "total_used": round(sum(b["total_used"] for b in result), 2),
        "generated_at": datetime.now(UTC).isoformat(),
    }


def _generate_valuation_drill_down(db: Session) -> dict[str, Any]:
    """Generate current valuation breakdown."""
    ingredients = db.query(Ingredient).filter(Ingredient.is_active).all()

    items = []
    total_valuation = 0.0

    for ing in ingredients:
        valuation = float(ing.current_stock) * float(ing.cost_per_unit)
        total_valuation += valuation
        items.append({
            "ingredient_id": ing.id,
            "name": ing.name,
            "current_stock": float(ing.current_stock),
            "cost_per_unit": float(ing.cost_per_unit),
            "valuation": round(valuation, 2),
        })

    # Sort by valuation descending
    items.sort(key=lambda x: x["valuation"], reverse=True)

    return {
        "metric": "valuation",
        "data": items,
        "total_valuation": round(total_valuation, 2),
        "ingredient_count": len(items),
        "generated_at": datetime.now(UTC).isoformat(),
    }


def schedule_report(
    name: str,
    schedule_type: str,  # 'daily', 'weekly', 'monthly'
    report_type: str,  # 'sales', 'usage', 'valuation', 'consolidated'
    email: str | None = None,
    format: str = "csv",  # 'csv', 'json', 'pdf'
) -> dict[str, Any]:
    """Schedule a recurring report."""
    # In production, this would integrate with a task scheduler like Celery/APScheduler
    # For now, return the schedule configuration
    return {
        "name": name,
        "schedule_type": schedule_type,
        "report_type": report_type,
        "email": email,
        "format": format,
        "status": "scheduled",
        "created_at": datetime.now(UTC).isoformat(),
        "next_run": _calculate_next_run(schedule_type),
    }


def _calculate_next_run(schedule_type: str) -> str:
    """Calculate next run time based on schedule type."""
    now = datetime.now(UTC)

    if schedule_type == "daily":
        next_run = now.replace(hour=6, minute=0, second=0, microsecond=0)
        if next_run <= now:
            next_run += timedelta(days=1)
    elif schedule_type == "weekly":
        days_ahead = (0 - now.weekday()) % 7  # Monday = 0
        next_run = now + timedelta(days=days_ahead)
        next_run = next_run.replace(hour=6, minute=0, second=0, microsecond=0)
    elif schedule_type == "monthly":
        if now.month == 12:
            next_run = now.replace(year=now.year + 1, month=1, day=1, hour=6, minute=0, second=0, microsecond=0)
        else:
            next_run = now.replace(month=now.month + 1, day=1, hour=6, minute=0, second=0, microsecond=0)
    else:
        next_run = now + timedelta(days=1)

    return next_run.isoformat()
