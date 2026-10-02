"""Audit trail service with hash chaining."""
from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


def _get_prev_hash(db: Session) -> str | None:
    """Get the hash of the most recent audit log entry."""
    last_entry = db.query(AuditLog).order_by(AuditLog.id.desc()).first()
    return last_entry.entry_hash if last_entry else None


def log_action(
    db: Session,
    action: str,
    entity_type: str | None = None,
    entity_id: str | None = None,
    before_state: dict[str, Any] | None = None,
    after_state: dict[str, Any] | None = None,
    user_id: str | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    """Log an action to the audit trail with hash chaining."""
    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else None,
        before_state=json.dumps(before_state) if before_state else None,
        after_state=json.dumps(after_state) if after_state else None,
        prev_hash=_get_prev_hash(db),
        ip_address=ip_address,
    )

    entry.entry_hash = entry.compute_hash()

    db.add(entry)
    db.commit()
    db.refresh(entry)

    logger.info(f"Audit: {action} on {entity_type}:{entity_id} (hash={entry.entry_hash[:16]}...)")

    return entry


def verify_chain_integrity(db: Session) -> dict[str, Any]:
    """Verify the entire audit log chain for tampering."""
    entries = db.query(AuditLog).order_by(AuditLog.id.asc()).all()

    if not entries:
        return {"valid": True, "entries_checked": 0, "message": "No audit entries"}

    prev_hash = None
    errors = []

    for entry in entries:
        # Check hash chain
        if entry.prev_hash != prev_hash:
            errors.append({
                "entry_id": entry.id,
                "error": "prev_hash mismatch",
                "expected": prev_hash,
                "actual": entry.prev_hash,
            })

        # Check entry hash integrity
        expected_hash = entry.compute_hash()
        if entry.entry_hash != expected_hash:
            errors.append({
                "entry_id": entry.id,
                "error": "entry_hash mismatch",
                "expected": expected_hash[:16] + "...",
                "actual": entry.entry_hash[:16] + "...",
            })

        prev_hash = entry.entry_hash

    return {
        "valid": len(errors) == 0,
        "entries_checked": len(entries),
        "errors": errors,
        "message": "Chain integrity verified" if len(errors) == 0 else f"{len(errors)} integrity errors found",
    }


def export_audit_log(
    db: Session,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    action: str | None = None,
    entity_type: str | None = None,
) -> list[dict[str, Any]]:
    """Export audit log entries as a list of dicts."""
    query = db.query(AuditLog).order_by(AuditLog.id.desc())

    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    if action:
        query = query.filter(AuditLog.action == action)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)

    entries = query.all()

    result = []
    for entry in entries:
        result.append({
            "id": entry.id,
            "timestamp": entry.timestamp.isoformat() if entry.timestamp else None,
            "user_id": entry.user_id,
            "action": entry.action,
            "entity_type": entry.entity_type,
            "entity_id": entry.entity_id,
            "before_state": json.loads(entry.before_state) if entry.before_state else None,
            "after_state": json.loads(entry.after_state) if entry.after_state else None,
            "prev_hash": entry.prev_hash,
            "entry_hash": entry.entry_hash,
            "ip_address": entry.ip_address,
        })

    return result
