"""Unit tests for SQLAlchemy models: properties, to_dict, __repr__."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import MagicMock


class TestIngredientModel:
    def _make(self, **kwargs: Any) -> Any:
        from app.models.ingredient import Ingredient

        defaults = dict(
            name="Tepung",
            unit="gram",
            cost_per_unit=8000,
            shelf_life_days=30,
            current_stock=200,
            min_stock_threshold=100,
        )
        defaults.update(kwargs)
        return Ingredient(**defaults)

    def test_stock_ratio_above_threshold(self) -> None:
        ing = self._make(current_stock=200, min_stock_threshold=100)
        assert ing.stock_ratio == 200.0

    def test_stock_ratio_below_threshold(self) -> None:
        ing = self._make(current_stock=50, min_stock_threshold=100)
        assert ing.stock_ratio == 50.0

    def test_stock_ratio_zero_threshold(self) -> None:
        ing = self._make(current_stock=50, min_stock_threshold=0)
        assert ing.stock_ratio == 100.0

    def test_stock_status_safe(self) -> None:
        ing = self._make(current_stock=300, min_stock_threshold=100)
        assert ing.stock_status == "safe"

    def test_stock_status_warning(self) -> None:
        ing = self._make(current_stock=120, min_stock_threshold=100)
        assert ing.stock_status == "warning"

    def test_stock_status_danger(self) -> None:
        ing = self._make(current_stock=50, min_stock_threshold=100)
        assert ing.stock_status == "danger"

    def test_valuation(self) -> None:
        ing = self._make(current_stock=10, cost_per_unit=5000)
        assert ing.valuation == 50000.0

    def test_days_until_expiry(self) -> None:
        ing = self._make(shelf_life_days=30)
        assert ing.days_until_expiry == 30

    def test_to_dict(self) -> None:
        ing = self._make(
            id=1,
            barcode_sku="SKU001",
            name="Tepung",
            unit="gram",
            cost_per_unit=8000,
            shelf_life_days=30,
            current_stock=500,
            min_stock_threshold=100,
            lead_time_days=2,
            is_active=True,
        )
        d = ing.to_dict()
        assert d["id"] == 1
        assert d["barcode_sku"] == "SKU001"
        assert d["name"] == "Tepung"
        assert d["unit"] == "gram"
        assert d["cost_per_unit"] == 8000
        assert d["current_stock"] == 500
        assert d["stock_ratio"] == 500.0
        assert d["stock_status"] == "safe"
        assert d["valuation"] == 4000000.0
        assert d["days_until_expiry"] == 30
        assert d["created_at"] is None
        assert d["updated_at"] is None

    def test_repr(self) -> None:
        ing = self._make(id=1, name="Tepung", current_stock=100)
        r = repr(ing)
        assert "Tepung" in r
        assert "100" in r


class TestSupplierModel:
    def _make(self, **kwargs: Any) -> Any:
        from app.models.supplier import Supplier

        defaults = dict(name="PT ABC", payment_terms_days=0)
        defaults.update(kwargs)
        return Supplier(**defaults)

    def test_is_credit_true(self) -> None:
        s = self._make(payment_terms_days=14)
        assert s.is_credit is True

    def test_is_credit_false(self) -> None:
        s = self._make(payment_terms_days=0)
        assert s.is_credit is False

    def test_to_dict(self) -> None:
        s = self._make(id=1, name="PT ABC", phone_whatsapp="08123", payment_terms_days=7)
        d = s.to_dict()
        assert d["name"] == "PT ABC"
        assert d["phone_whatsapp"] == "08123"
        assert d["is_credit"] is True
        assert d["created_at"] is None

    def test_repr(self) -> None:
        s = self._make(id=1, name="PT ABC", payment_terms_days=7)
        r = repr(s)
        assert "PT ABC" in r
        assert "7" in r


class TestMenuItemModel:
    def _make(self, **kwargs: Any) -> Any:
        from app.models.menu import MenuItem

        defaults = dict(name="Kopi", sale_price=25000)
        defaults.update(kwargs)
        return MenuItem(**defaults)

    def test_to_dict(self) -> None:
        m = self._make(id=1, pos_item_id="POS001", name="Kopi", sale_price=25000, is_active=True)
        d = m.to_dict()
        assert d["id"] == 1
        assert d["pos_item_id"] == "POS001"
        assert d["name"] == "Kopi"
        assert d["sale_price"] == 25000
        assert d["is_active"] is True
        assert d["created_at"] is None

    def test_repr(self) -> None:
        m = self._make(id=1, name="Kopi", sale_price=25000)
        r = repr(m)
        assert "Kopi" in r
        assert "25000" in r


class TestRecipeItemModel:
    def _make(self, **kwargs: Any) -> Any:
        from app.models.menu import RecipeItem

        defaults = dict(menu_item_id=1, ingredient_id=1, quantity_required=50)
        defaults.update(kwargs)
        ri = RecipeItem(**defaults)
        return ri

    def test_cost_per_portion_with_ingredient(self) -> None:
        ri = self._make(quantity_required=50)
        ri.ingredient = MagicMock()
        ri.ingredient.cost_per_unit = 1000
        assert ri.cost_per_portion == 50000.0

    def test_cost_per_portion_without_ingredient(self) -> None:
        ri = self._make(quantity_required=50)
        ri.ingredient = None
        assert ri.cost_per_portion == 0.0

    def test_to_dict(self) -> None:
        ri = self._make(id=1, quantity_required=50)
        ri.menu_item = MagicMock()
        ri.menu_item.name = "Kopi"
        ri.ingredient = MagicMock()
        ri.ingredient.name = "Tepung"
        ri.ingredient.unit = "gram"
        ri.ingredient.cost_per_unit = 1000
        d = ri.to_dict()
        assert d["id"] == 1
        assert d["menu_item_name"] == "Kopi"
        assert d["ingredient_name"] == "Tepung"
        assert d["ingredient_unit"] == "gram"
        assert d["quantity_required"] == 50.0
        assert d["cost_per_portion"] == 50000.0

    def test_to_dict_no_relations(self) -> None:
        ri = self._make(id=1, quantity_required=50)
        ri.menu_item = None
        ri.ingredient = None
        d = ri.to_dict()
        assert d["menu_item_name"] is None
        assert d["ingredient_name"] is None
        assert d["ingredient_unit"] is None

    def test_repr(self) -> None:
        ri = self._make(menu_item_id=1, ingredient_id=1, quantity_required=50)
        r = repr(ri)
        assert "1" in r
        assert "50" in r


class TestSalesTransactionModel:
    def _make(self, **kwargs: Any) -> Any:
        from app.models.transaction import SalesTransaction

        now = datetime.now(UTC)
        defaults = dict(
            transaction_hash="abc123def456",
            quantity=2,
            transaction_time=now,
        )
        defaults.update(kwargs)
        return SalesTransaction(**defaults)

    def test_to_dict(self) -> None:
        tx = self._make(id=1, pos_reference_id="POS-001", quantity=2, menu_item=None)
        d = tx.to_dict()
        assert d["id"] == 1
        assert d["transaction_hash"] == "abc123def456"
        assert d["pos_reference_id"] == "POS-001"
        assert d["quantity"] == 2
        assert d["menu_item_name"] is None

    def test_to_dict_with_menu_item(self) -> None:
        mock_menu = MagicMock()
        mock_menu.name = "Kopi"
        tx = self._make(id=1, pos_reference_id="POS-001", quantity=2, menu_item=mock_menu)
        d = tx.to_dict()
        assert d["menu_item_name"] == "Kopi"

    def test_repr(self) -> None:
        tx = self._make(transaction_hash="abc123def456", quantity=3)
        r = repr(tx)
        assert "abc123d" in r
        assert "3" in r


class TestPosSyncLogModel:
    def _make(self, **kwargs: Any) -> Any:
        from app.models.transaction import PosSyncLog

        defaults = dict(
            file_name="sales.csv",
            total_rows_read=100,
            new_rows_inserted=95,
            duplicate_rows_skipped=5,
            reconciled_stock_items=10,
        )
        defaults.update(kwargs)
        return PosSyncLog(**defaults)

    def test_to_dict(self) -> None:
        log = self._make(id=1)
        d = log.to_dict()
        assert d["id"] == 1
        assert d["file_name"] == "sales.csv"
        assert d["total_rows_read"] == 100
        assert d["new_rows_inserted"] == 95
        assert d["duplicate_rows_skipped"] == 5
        assert d["reconciled_stock_items"] == 10
        assert d["date_range_start"] is None
        assert d["date_range_end"] is None

    def test_repr(self) -> None:
        log = self._make(id=1, file_name="sales.csv", new_rows_inserted=95)
        r = repr(log)
        assert "sales.csv" in r
        assert "95" in r


class TestIngredientDailyUsageModel:
    def test_to_dict(self) -> None:
        from app.models.transaction import IngredientDailyUsage

        now = datetime.now(UTC)
        usage = IngredientDailyUsage(
            usage_date=now,
            ingredient_id=1,
            total_quantity_used=50.5,
        )
        d = usage.to_dict()
        assert d["id"] is None
        assert d["ingredient_id"] == 1
        assert d["total_quantity_used"] == 50.5
        assert d["usage_date"] is not None
        assert d["ingredient_name"] is None

    def test_to_dict_with_ingredient(self) -> None:
        from app.models.transaction import IngredientDailyUsage

        now = datetime.now(UTC)
        usage = IngredientDailyUsage(
            usage_date=now,
            ingredient_id=1,
            total_quantity_used=50.5,
        )
        usage.ingredient = MagicMock()
        usage.ingredient.name = "Tepung"
        d = usage.to_dict()
        assert d["ingredient_name"] == "Tepung"

    def test_repr(self) -> None:
        from app.models.transaction import IngredientDailyUsage

        now = datetime.now(UTC)
        usage = IngredientDailyUsage(
            usage_date=now,
            ingredient_id=1,
            total_quantity_used=50.5,
        )
        r = repr(usage)
        assert "1" in r
        assert "50.5" in r


class TestInventoryPurchaseModel:
    def _make(self, **kwargs: Any) -> Any:
        from app.models.purchase import InventoryPurchase, PaymentMethod, PaymentStatus

        now = datetime.now(UTC)
        defaults = dict(
            purchase_date=now,
            ingredient_id=1,
            supplier_id=1,
            quantity=100,
            total_cost=500000,
            payment_method=PaymentMethod.CASH,
            payment_status=PaymentStatus.PAID,
        )
        defaults.update(kwargs)
        return InventoryPurchase(**defaults)

    def test_is_overdue_unpaid_past_due(self) -> None:
        p = self._make(
            payment_status="UNPAID",
            due_date=datetime.now(UTC) - timedelta(days=1),
        )
        assert p.is_overdue is True

    def test_is_overdue_paid(self) -> None:
        p = self._make(
            payment_status="PAID",
            due_date=datetime.now(UTC) - timedelta(days=1),
        )
        assert p.is_overdue is False

    def test_is_overdue_no_due_date(self) -> None:
        p = self._make(payment_status="UNPAID", due_date=None)
        assert p.is_overdue is False

    def test_is_overdue_unpaid_not_yet_due(self) -> None:
        p = self._make(
            payment_status="UNPAID",
            due_date=datetime.now(UTC) + timedelta(days=5),
        )
        assert p.is_overdue is False

    def test_days_until_due_future(self) -> None:
        p = self._make(
            payment_status="UNPAID",
            due_date=datetime.now(UTC) + timedelta(days=5),
        )
        assert p.days_until_due >= 4

    def test_days_until_due_paid(self) -> None:
        p = self._make(
            payment_status="PAID",
            due_date=datetime.now(UTC) + timedelta(days=5),
        )
        assert p.days_until_due == 0

    def test_days_until_due_past(self) -> None:
        p = self._make(
            payment_status="UNPAID",
            due_date=datetime.now(UTC) - timedelta(days=3),
        )
        assert p.days_until_due == 0

    def test_to_dict(self) -> None:
        from app.models.purchase import PaymentMethod, PaymentStatus

        p = self._make(
            id=1,
            payment_method=PaymentMethod.CASH,
            payment_status=PaymentStatus.PAID,
        )
        p.ingredient = MagicMock()
        p.ingredient.name = "Tepung"
        p.supplier = MagicMock()
        p.supplier.name = "PT ABC"
        d = p.to_dict()
        assert d["id"] == 1
        assert d["total_cost"] == 500000
        assert d["payment_method"] == "CASH"
        assert d["payment_status"] == "PAID"
        assert d["ingredient_name"] == "Tepung"
        assert d["supplier_name"] == "PT ABC"

    def test_repr(self) -> None:
        p = self._make(id=1, ingredient_id=1, total_cost=500000)
        r = repr(p)
        assert "1" in r
        assert "500000" in r


class TestOperationalAuditLogModel:
    def _make(self, **kwargs: Any) -> Any:
        from app.models.purchase import OperationalAuditLog

        defaults = dict(
            action_type="STOCK_OPNAME",
            entity_name="Tepung",
            actor_role="OWNER",
        )
        defaults.update(kwargs)
        return OperationalAuditLog(**defaults)

    def test_to_dict(self) -> None:
        now = datetime.now(UTC)
        log = self._make(id=1, old_value="100", new_value="200", timestamp=now)
        d = log.to_dict()
        assert d["id"] == 1
        assert d["action_type"] == "STOCK_OPNAME"
        assert d["entity_name"] == "Tepung"
        assert d["old_value"] == "100"
        assert d["new_value"] == "200"
        assert d["actor_role"] == "OWNER"
        assert d["timestamp"] is not None

    def test_repr(self) -> None:
        log = self._make(action_type="STOCK_OPNAME", entity_name="Tepung")
        r = repr(log)
        assert "STOCK_OPNAME" in r
        assert "Tepung" in r


class TestSecurityModels:
    def test_security_keyring_repr(self) -> None:
        from app.models.security import SecurityKeyring

        kr = SecurityKeyring(
            encrypted_dek_owner="enc_owner",
            encrypted_dek_developer="enc_dev",
        )
        r = repr(kr)
        assert "SecurityKeyring" in r

    def test_security_audit_clock_repr(self) -> None:
        from app.models.security import SecurityAuditClock

        ac = SecurityAuditClock(last_seen_timestamp=1234567890)
        r = repr(ac)
        assert "1234567890" in r

    def test_app_license_repr(self) -> None:
        from app.models.security import AppLicense

        lic = AppLicense(
            license_key="ABC-123",
            valid_until=datetime(2026, 12, 31, tzinfo=UTC),
            last_verified_at=datetime.now(UTC),
            grace_period_end=datetime(2027, 1, 15, tzinfo=UTC),
        )
        r = repr(lic)
        assert "2026" in r

    def test_security_unlock_audit_repr(self) -> None:
        from app.models.security import SecurityUnlockAudit

        ua = SecurityUnlockAudit(role="OWNER", success=1)
        r = repr(ua)
        assert "OWNER" in r
        assert "1" in r
