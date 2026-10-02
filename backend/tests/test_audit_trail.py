"""Tests for audit trail service."""
from __future__ import annotations

from unittest.mock import MagicMock

from app.models.audit_log import AuditLog
from app.services.audit_trail import (
    _get_prev_hash,
    export_audit_log,
    verify_chain_integrity,
)


class TestAuditLogModel:
    def test_repr(self) -> None:
        entry = AuditLog(id=1, action="UPDATE", entity_type="ingredient")
        assert "UPDATE" in repr(entry)

    def test_compute_hash_deterministic(self) -> None:
        entry = AuditLog(
            user_id="test",
            action="CREATE",
            entity_type="ingredient",
            entity_id="1",
            prev_hash=None,
        )
        h1 = entry.compute_hash()
        h2 = entry.compute_hash()
        assert h1 == h2
        assert len(h1) == 64

    def test_compute_hash_changes_with_data(self) -> None:
        entry1 = AuditLog(action="CREATE", entity_type="ingredient", entity_id="1")
        entry2 = AuditLog(action="DELETE", entity_type="ingredient", entity_id="1")
        assert entry1.compute_hash() != entry2.compute_hash()


class TestVerifyChainIntegrity:
    def test_empty_chain_valid(self) -> None:
        db = MagicMock()
        db.query.return_value.order_by.return_value.all.return_value = []

        result = verify_chain_integrity(db)

        assert result["valid"] is True
        assert result["entries_checked"] == 0

    def test_valid_chain(self) -> None:
        entry1 = AuditLog(
            id=1, action="CREATE", entity_type="ingredient", entity_id="1",
            prev_hash=None,
        )
        entry1.entry_hash = entry1.compute_hash()

        entry2 = AuditLog(
            id=2, action="UPDATE", entity_type="ingredient", entity_id="1",
            prev_hash=entry1.entry_hash,
        )
        entry2.entry_hash = entry2.compute_hash()

        db = MagicMock()
        db.query.return_value.order_by.return_value.all.return_value = [entry1, entry2]

        result = verify_chain_integrity(db)

        assert result["valid"] is True
        assert result["entries_checked"] == 2

    def test_tampered_chain_detected(self) -> None:
        entry1 = AuditLog(
            id=1, action="CREATE", entity_type="ingredient", entity_id="1",
            prev_hash=None,
        )
        entry1.entry_hash = entry1.compute_hash()

        # entry2 has wrong prev_hash (simulating tampering)
        entry2 = AuditLog(
            id=2, action="UPDATE", entity_type="ingredient", entity_id="1",
            prev_hash="wrong_hash_value",
        )
        entry2.entry_hash = entry2.compute_hash()

        db = MagicMock()
        db.query.return_value.order_by.return_value.all.return_value = [entry1, entry2]

        result = verify_chain_integrity(db)

        assert result["valid"] is False
        assert len(result["errors"]) > 0


class TestExportAuditLog:
    def test_export_empty(self) -> None:
        db = MagicMock()
        db.query.return_value.order_by.return_value.all.return_value = []

        result = export_audit_log(db=db)

        assert result == []

    def test_export_returns_entries(self) -> None:
        entry = AuditLog(
            id=1, action="CREATE", entity_type="ingredient", entity_id="1",
            prev_hash=None,
        )
        entry.entry_hash = entry.compute_hash()
        entry.timestamp = None

        db = MagicMock()
        db.query.return_value.order_by.return_value.all.return_value = [entry]

        result = export_audit_log(db=db)

        assert len(result) == 1
        assert result[0]["action"] == "CREATE"


class TestGetPrevHash:
    def test_no_entries_returns_none(self) -> None:
        db = MagicMock()
        db.query.return_value.order_by.return_value.first.return_value = None
        assert _get_prev_hash(db) is None

    def test_returns_last_hash(self) -> None:
        entry = MagicMock()
        entry.entry_hash = "abc123"
        db = MagicMock()
        db.query.return_value.order_by.return_value.first.return_value = entry
        assert _get_prev_hash(db) == "abc123"


class TestAuditAPI:
    def test_audit_router_registered(self) -> None:
        from app.api.v1.audit import router
        assert router.prefix == "/audit"
        paths = [route.path for route in router.routes]
        assert any("/verify" in p for p in paths)
        assert any("/export" in p for p in paths)
