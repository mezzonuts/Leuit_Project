"""Audit trail API endpoints."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, verify_license
from app.services.audit_trail import (
    export_audit_log,
    verify_chain_integrity,
)

router = APIRouter(prefix="/audit", tags=["Audit Trail"])


@router.get("/verify")
def verify_audit_chain(
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
) -> dict:
    """Verify audit log chain integrity."""
    return verify_chain_integrity(db)


@router.get("/export")
def export_audit(
    days: int = Query(30, ge=1, le=365),
    action: str | None = Query(None),
    entity_type: str | None = Query(None),
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
) -> dict:
    """Export audit log entries."""
    from datetime import UTC, timedelta

    end_date = datetime.now(UTC)
    start_date = end_date - timedelta(days=days)

    entries = export_audit_log(
        db=db,
        start_date=start_date,
        end_date=end_date,
        action=action,
        entity_type=entity_type,
    )

    return {
        "entries": entries,
        "total": len(entries),
        "period_days": days,
    }
