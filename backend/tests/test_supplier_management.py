"""Tests for supplier management enhancements."""
from __future__ import annotations


class TestSupplierStats:
    def test_supplier_stats_response_schema(self) -> None:
        from app.schemas.purchase_schema import SupplierStatsResponse
        stats = SupplierStatsResponse(
            supplier_id=1,
            supplier_name="PT ABC",
            total_purchases=1000000.0,
            unpaid_total=500000.0,
            avg_order_value=250000.0,
            purchase_count=4,
            period_days=30,
        )
        assert stats.supplier_name == "PT ABC"
        assert stats.purchase_count == 4
        assert stats.total_purchases == 1000000.0

    def test_supplier_stats_endpoint_registered(self) -> None:
        from app.api.v1.purchases import router
        paths = [route.path for route in router.routes]
        assert any("/suppliers/{supplier_id}/stats" in p for p in paths)
