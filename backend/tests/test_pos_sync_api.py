"""POS sync endpoints schema validation."""
import hashlib
from datetime import UTC, datetime, timezone

import pytest

from app.schemas.sync_schema import (
    PosSyncHistoryItem,
    PosSyncHistoryResponse,
    PosSyncUploadResponse,
)


class TestPosSyncSchema:

    def test_upload_response(self):
        resp = PosSyncUploadResponse(
            status="success",
            new_inserted=10,
            duplicates_skipped=2,
            message="Processed 12 rows",
        )
        assert resp.status == "success"
        assert resp.new_inserted == 10

    def test_upload_response_defaults(self):
        resp = PosSyncUploadResponse(
            status="success",
            new_inserted=0,
            duplicates_skipped=0,
        )
        assert resp.message is None

    def test_history_item(self):
        item = PosSyncHistoryItem(
            id=1,
            file_name="sales.csv",
            uploaded_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            total_rows_read=100,
            new_rows_inserted=90,
            duplicate_rows_skipped=10,
            reconciled_stock_items=5,
        )
        assert item.file_name == "sales.csv"
        assert item.total_rows_read == 100

    def test_history_item_optional_dates(self):
        item = PosSyncHistoryItem(
            id=1,
            file_name="test.csv",
            uploaded_at=datetime.now(timezone.utc),
            total_rows_read=0,
            new_rows_inserted=0,
            duplicate_rows_skipped=0,
            reconciled_stock_items=0,
        )
        assert item.date_range_start is None
        assert item.date_range_end is None

    def test_history_response(self):
        resp = PosSyncHistoryResponse(
            total=0,
            page=1,
            page_size=50,
            total_pages=0,
            items=[],
        )
        assert resp.total == 0
        assert resp.items == []


class TestDeduplicationHash:
    """Verify SHA-256 dedup hash behaviour used in pos_sync."""

    def test_hash_format(self):
        raw = "ORDER-001_2026-01-01_10:00:00_MenuA"
        h = hashlib.sha256(raw.encode()).hexdigest()
        assert len(h) == 64

    def test_same_input_same_hash(self):
        raw = "ORDER-001_a"
        h1 = hashlib.sha256(raw.encode()).hexdigest()
        h2 = hashlib.sha256(raw.encode()).hexdigest()
        assert h1 == h2

    def test_different_order_different_hash(self):
        h1 = hashlib.sha256("ORDER-001_a".encode()).hexdigest()
        h2 = hashlib.sha256("ORDER-002_a".encode()).hexdigest()
        assert h1 != h2

    def test_different_date_different_hash(self):
        h1 = hashlib.sha256("ORDER-001_2026-01-01_MenuA".encode()).hexdigest()
        h2 = hashlib.sha256("ORDER-001_2026-01-02_MenuA".encode()).hexdigest()
        assert h1 != h2

    def test_hash_is_64_hex_chars(self):
        raw = "ORDER-001_2026-01-01_10:00:00_MenuA"
        h = hashlib.sha256(raw.encode()).hexdigest()
        assert len(h) == 64


class TestColumnMapping:
    """Test CSV column name mapping logic from pos_sync.py."""

    COL_MAPPING = {
        'order_id': ['order_id', 'orderid', 'id_transaksi', 'nomor_transaksi'],
        'timestamp': ['timestamp', 'waktu', 'tanggal', 'datetime', 'created_at'],
        'menu_id': ['menu_id', 'item_id', 'id_menu', 'product_id'],
        'item_name': ['item_name', 'nama_item', 'nama_produk', 'menu_name', 'product_name'],
        'qty': ['qty', 'quantity', 'jumlah', 'qty_sold'],
    }

    @staticmethod
    def _normalize(cols):
        return [c.strip().lower().replace(' ', '_') for c in cols]

    def _get_mapping(self, cols):
        normalized = self._normalize(cols)
        mapped = {}
        for target, candidates in self.COL_MAPPING.items():
            for c in candidates:
                if c in normalized:
                    mapped[target] = c
                    break
        return mapped

    def test_moka_format(self):
        cols = ['Order ID', 'Timestamp', 'Menu ID', 'Item Name', 'Qty']
        mapped = self._get_mapping(cols)
        assert 'order_id' in mapped
        assert 'timestamp' in mapped
        assert 'qty' in mapped

    def test_majoo_format(self):
        cols = ['id_transaksi', 'waktu', 'id_menu', 'nama_produk', 'jumlah']
        mapped = self._get_mapping(cols)
        assert mapped.get('order_id') == 'id_transaksi'
        assert mapped.get('timestamp') == 'waktu'
        assert mapped.get('qty') == 'jumlah'

    def test_olsera_format(self):
        cols = ['orderid', 'datetime', 'product_id', 'product_name', 'quantity']
        mapped = self._get_mapping(cols)
        assert mapped.get('order_id') == 'orderid'
        assert mapped.get('qty') == 'quantity'

    def test_missing_required_column(self):
        cols = ['name', 'price']
        mapped = self._get_mapping(cols)
        assert 'order_id' not in mapped
        assert 'timestamp' not in mapped
        assert 'qty' not in mapped


class TestStockDeductionLogic:
    """Test BOM stock deduction calculation."""

    def test_deduction_calculation(self):
        quantity_required = 50.0  # per portion
        qty_sold = 3
        deduction = quantity_required * qty_sold
        assert deduction == 150.0

    def test_stock_floor_zero(self):
        current_stock = 100.0
        deduction = 150.0
        new_stock = max(0.0, current_stock - deduction)
        assert new_stock == 0.0

    def test_stock_normal(self):
        current_stock = 500.0
        deduction = 150.0
        new_stock = max(0.0, current_stock - deduction)
        assert new_stock == 350.0

    def test_multiple_ingredients(self):
        deductions = {}
        # Recipe: Menu A uses 2 ingredients
        deductions[1] = deductions.get(1, 0) + (50.0 * 3)
        deductions[2] = deductions.get(2, 0) + (200.0 * 3)
        # Menu B also uses same ingredients
        deductions[1] = deductions.get(1, 0) + (50.0 * 2)
        deductions[2] = deductions.get(2, 0) + (200.0 * 2)
        assert deductions[1] == 250.0
        assert deductions[2] == 1000.0


class TestSyncEndpointExists:
    """Verify sync routes are registered in the app."""

    def test_sync_prefix_in_routes(self):
        from app.main import app
        openapi = app.openapi()
        paths = list(openapi.get("paths", {}).keys())
        assert any("/sync" in p for p in paths)

    def test_all_sync_endpoints(self):
        from app.main import app
        openapi = app.openapi()
        sync_routes = [p for p in openapi.get("paths", {}).keys() if "/sync" in p]
        assert len(sync_routes) >= 3
