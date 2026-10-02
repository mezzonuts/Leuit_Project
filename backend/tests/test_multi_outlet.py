"""Unit tests for multi-outlet support."""
from __future__ import annotations

from unittest.mock import MagicMock

from app.models.outlet import Outlet
from app.schemas.outlet_schema import OutletCreate, OutletListResponse, OutletResponse, OutletUpdate


class TestOutletModel:
    def test_repr(self) -> None:
        outlet = Outlet(name="Cafe A", is_active=True)
        outlet.id = 1
        assert "Cafe A" in repr(outlet)

    def test_to_dict(self) -> None:
        outlet = Outlet(
            name="Cafe A",
            address="Bandung",
            phone="0812",
            is_active=True,
            settings=None,
        )
        outlet.id = 1
        outlet.created_at = None
        outlet.updated_at = None
        d = outlet.to_dict()
        assert d["name"] == "Cafe A"
        assert d["is_active"] is True


class TestOutletSchemas:
    def test_outlet_create(self) -> None:
        data = OutletCreate(name="Cafe B", address="Jakarta", phone="0813")
        assert data.name == "Cafe B"
        assert data.is_active is True

    def test_outlet_update_partial(self) -> None:
        data = OutletUpdate(name="New Name")
        assert data.name == "New Name"
        assert data.address is None

    def test_outlet_response(self) -> None:
        resp = OutletResponse(
            id=1, name="Cafe C", address=None, phone=None,
            is_active=True, settings=None, created_at=None, updated_at=None,
        )
        assert resp.id == 1
        assert resp.name == "Cafe C"

    def test_outlet_list_response(self) -> None:
        lst = OutletListResponse(items=[], total=0)
        assert lst.total == 0
        assert lst.items == []


class TestConsolidatedReport:
    def test_report_structure(self) -> None:
        from app.api.v1.reports import get_consolidated_report
        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = []
        db.query.return_value.filter.return_value.count.return_value = 0

        result = get_consolidated_report(days=30, db=db)

        assert "reports" in result
        assert "summary" in result
        assert "generated_at" in result
        assert "total_valuation" in result["summary"]
        assert "outlet_count" in result["summary"]


class TestOutletAPI:
    def test_outlet_router_registered(self) -> None:
        from app.api.v1.outlets import router
        assert router.prefix == "/outlets"
        assert len(router.routes) > 0

    def test_reports_router_registered(self) -> None:
        from app.api.v1.reports import router
        assert router.prefix == "/reports"
        assert len(router.routes) > 0
