"""Immutable audit log with hash chaining for tamper detection."""
from __future__ import annotations

import hashlib
import json

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.core.database import Base


class AuditLog(Base):
    """Append-only audit log with SHA256 hash chaining."""
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    user_id = Column(String(100), nullable=True)
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(100), nullable=True, index=True)
    entity_id = Column(String(100), nullable=True)
    before_state = Column(Text, nullable=True)
    after_state = Column(Text, nullable=True)
    prev_hash = Column(String(64), nullable=True)
    entry_hash = Column(String(64), nullable=False, unique=True)
    ip_address = Column(String(45), nullable=True)

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action}, entity={self.entity_type})>"

    def compute_hash(self) -> str:
        """Compute SHA256 hash for this log entry."""
        data = json.dumps({
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "user_id": self.user_id,
            "action": self.action,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "before_state": self.before_state,
            "after_state": self.after_state,
            "prev_hash": self.prev_hash,
        }, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()
