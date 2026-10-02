"""Analytics API endpoints for drill-down reports and scheduling."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, verify_license
from app.services.report_scheduler import (
    generate_drill_down_report,
    schedule_report,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/drill-down")
def get_drill_down_report(
    metric: str = Query(..., pattern="^(sales|usage|valuation)$"),
    days: int = Query(30, ge=1, le=365),
    granularity: str = Query("daily", pattern="^(daily|weekly|monthly)$"),
    ingredient_id: int | None = Query(None),
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
) -> dict:
    """Get drill-down report for specified metric."""
    end_date = datetime.now(UTC)
    start_date = end_date - timedelta(days=days)

    return generate_drill_down_report(
        db=db,
        metric=metric,
        start_date=start_date,
        end_date=end_date,
        granularity=granularity,
        ingredient_id=ingredient_id,
    )


@router.post("/schedule")
def create_report_schedule(
    name: str = Query(...),
    schedule_type: str = Query(..., pattern="^(daily|weekly|monthly)$"),
    report_type: str = Query(..., pattern="^(sales|usage|valuation|consolidated)$"),
    email: str | None = Query(None),
    format: str = Query("csv", pattern="^(csv|json|pdf)$"),
    license_info: dict = Depends(verify_license),
) -> dict:
    """Schedule a recurring report."""
    return schedule_report(
        name=name,
        schedule_type=schedule_type,
        report_type=report_type,
        email=email,
        format=format,
    )
