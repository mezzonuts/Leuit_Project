# Plan: Hari 3 — Backend: Auth API & Models

> **Status:** Partially done (carried from Day 2). Focus: harden auth API, verify all models, add missing validation.

---

## Context

Day 3 deliverables from PLAN.md:
- `/api/v1/auth/unlock` — ✅ Done (Day 2)
- `/api/v1/auth/status` — ✅ Done (Day 2)
- All 8 security/business models — ✅ Done (Day 2)

Remaining work: model hardening, API edge cases, response schema completeness.

---

## Tasks

### Task 1: Verify all models have complete `to_dict()` + `__repr__`
**Files:** All 6 model files in `backend/app/models/`

Audit each model:
- `Ingredient` — has `to_dict()`, `__repr__`, `stock_ratio`, `stock_status`, `valuation` ✅
- `Supplier` — has `to_dict()`, `__repr__`, `is_credit` ✅
- `MenuItem` — has `to_dict()`, `__repr__` ✅
- `RecipeItem` — has `to_dict()`, `__repr__`, `cost_per_portion` ✅
- `SalesTransaction` — has `to_dict()`, `__repr__` ✅
- `PosSyncLog` — has `to_dict()`, `__repr__` ✅
- `IngredientDailyUsage` — has `to_dict()`, `__repr__` ✅
- `InventoryPurchase` — has `to_dict()`, `__repr__`, `is_overdue`, `days_until_due` ✅
- `OperationalAuditLog` — has `to_dict()`, `__repr__` ✅
- `SecurityKeyring` — has `__repr__` ✅
- `SecurityAuditClock` — has `__repr__` ✅
- `AppLicense` — has `__repr__` ✅
- `SecurityUnlockAudit` — has `__repr__` ✅

**Action:** No code changes needed — all models complete. Mark as verified.

### Task 2: Add model factory for tests
**File:** `backend/tests/factories.py` (new)

Create test factories for quick test setup:
```python
"""Test factories for creating model instances."""
from datetime import datetime, timezone
from app.models.ingredient import Ingredient
from app.models.supplier import Supplier
from app.models.menu import MenuItem, RecipeItem
from app.models.transaction import SalesTransaction, PosSyncLog, IngredientDailyUsage
from app.models.purchase import InventoryPurchase, PaymentMethod, PaymentStatus, OperationalAuditLog


def make_ingredient(**kwargs) -> dict:
    defaults = {
        "name": "Test Ingredient",
        "unit": "gram",
        "cost_per_unit": 10000,
        "shelf_life_days": 7,
        "current_stock": 100,
        "min_stock_threshold": 50,
    }
    defaults.update(kwargs)
    return defaults


def make_supplier(**kwargs) -> dict:
    defaults = {
        "name": "Test Supplier",
        "phone_whatsapp": "08123456789",
        "payment_terms_days": 0,
    }
    defaults.update(kwargs)
    return defaults


def make_menu_item(**kwargs) -> dict:
    defaults = {
        "name": "Test Menu",
        "sale_price": 25000,
    }
    defaults.update(kwargs)
    return defaults


def make_recipe_item(**kwargs) -> dict:
    defaults = {
        "quantity_required": 50.0,
    }
    defaults.update(kwargs)
    return defaults
```

### Task 3: Add model unit tests
**File:** `backend/tests/test_models.py` (new)

Test all model properties and methods:
```python
"""Unit tests for SQLAlchemy models: properties, to_dict, __repr__."""
import pytest
from app.models.ingredient import Ingredient
from app.models.supplier import Supplier
from app.models.menu import MenuItem, RecipeItem
from app.models.transaction import SalesTransaction, PosSyncLog, IngredientDailyUsage
from app.models.purchase import InventoryPurchase, PaymentMethod, PaymentStatus, OperationalAuditLog
from app.models.security import SecurityKeyring, SecurityAuditClock, AppLicense, SecurityUnlockAudit


class TestIngredientModel:
    def test_stock_ratio_above_threshold(self):
        ing = Ingredient.__new__(Ingredient)
        ing.current_stock = 200
        ing.min_stock_threshold = 100
        assert ing.stock_ratio == 200.0

    def test_stock_ratio_below_threshold(self):
        ing = Ingredient.__new__(Ingredient)
        ing.current_stock = 50
        ing.min_stock_threshold = 100
        assert ing.stock_ratio == 50.0

    def test_stock_ratio_zero_threshold(self):
        ing = Ingredient.__new__(Ingredient)
        ing.current_stock = 50
        ing.min_stock_threshold = 0
        assert ing.stock_ratio == 100.0

    def test_stock_status_safe(self):
        ing = Ingredient.__new__(Ingredient)
        ing.current_stock = 300
        ing.min_stock_threshold = 100
        assert ing.stock_status == "safe"

    def test_stock_status_warning(self):
        ing = Ingredient.__new__(Ingredient)
        ing.current_stock = 120
        ing.min_stock_threshold = 100
        assert ing.stock_status == "warning"

    def test_stock_status_danger(self):
        ing = Ingredient.__new__(Ingredient)
        ing.current_stock = 50
        ing.min_stock_threshold = 100
        assert ing.stock_status == "danger"

    def test_valuation(self):
        ing = Ingredient.__new__(Ingredient)
        ing.current_stock = 10
        ing.cost_per_unit = 5000
        assert ing.valuation == 50000.0

    def test_to_dict_keys(self):
        ing = Ingredient.__new__(Ingredient)
        ing.id = 1
        ing.barcode_sku = "SKU001"
        ing.name = "Gula"
        ing.unit = "gram"
        ing.cost_per_unit = 8000
        ing.shelf_life_days = 30
        ing.current_stock = 500
        ing.min_stock_threshold = 100
        ing.lead_time_days = 2
        ing.is_active = True
        ing.stock_ratio = 500.0
        ing.stock_status = "safe"
        ing.valuation = 4000000.0
        ing.days_until_expiry = 30
        ing.created_at = None
        ing.updated_at = None
        d = ing.to_dict()
        assert d["name"] == "Gula"
        assert d["unit"] == "gram"
        assert d["cost_per_unit"] == 8000
        assert d["current_stock"] == 500


class TestSupplierModel:
    def test_is_credit_true(self):
        s = Supplier.__new__(Supplier)
        s.payment_terms_days = 14
        assert s.is_credit is True

    def test_is_credit_false(self):
        s = Supplier.__new__(Supplier)
        s.payment_terms_days = 0
        assert s.is_credit is False

    def test_repr(self):
        s = Supplier.__new__(Supplier)
        s.id = 1
        s.name = "PT ABC"
        s.payment_terms_days = 7
        r = repr(s)
        assert "PT ABC" in r
        assert "7" in r


class TestMenuItemModel:
    def test_repr(self):
        m = MenuItem.__new__(MenuItem)
        m.id = 1
        m.name = "Kopi"
        m.sale_price = 25000
        assert "Kopi" in repr(m)


class TestRecipeItemModel:
    def test_cost_per_portion_with_ingredient(self):
        from unittest.mock import MagicMock
        ri = RecipeItem.__new__(RecipeItem)
        ri.quantity_required = 50
        ri.ingredient = MagicMock()
        ri.ingredient.cost_per_unit = 1000
        assert ri.cost_per_portion == 50000.0

    def test_cost_per_portion_without_ingredient(self):
        ri = RecipeItem.__new__(RecipeItem)
        ri.quantity_required = 50
        ri.ingredient = None
        assert ri.cost_per_portion == 0.0


class TestPurchaseModel:
    def test_is_overdue_unpaid_past_due(self):
        from datetime import datetime, timezone, timedelta
        p = InventoryPurchase.__new__(InventoryPurchase)
        p.payment_status = PaymentStatus.UNPAID
        p.due_date = datetime.now(timezone.utc) - timedelta(days=1)
        assert p.is_overdue is True

    def test_is_overdue_paid(self):
        from datetime import datetime, timezone, timedelta
        p = InventoryPurchase.__new__(InventoryPurchase)
        p.payment_status = PaymentStatus.PAID
        p.due_date = datetime.now(timezone.utc) - timedelta(days=1)
        assert p.is_overdue is False

    def test_is_overdue_no_due_date(self):
        p = InventoryPurchase.__new__(InventoryPurchase)
        p.payment_status = PaymentStatus.UNPAID
        p.due_date = None
        assert p.is_overdue is False


class TestSecurityModels:
    def test_keyring_repr(self):
        kr = SecurityKeyring.__new__(SecurityKeyring)
        kr.last_key_rotation = None
        assert "SecurityKeyring" in repr(kr)

    def test_audit_clock_repr(self):
        ac = SecurityAuditClock.__new__(SecurityAuditClock)
        ac.last_seen_timestamp = 1234567890
        assert "1234567890" in repr(ac)

    def test_unlock_audit_repr(self):
        ua = SecurityUnlockAudit.__new__(SecurityUnlockAudit)
        ua.role = "OWNER"
        ua.success = 1
        assert "OWNER" in repr(ua)
```

### Task 4: Verify auth endpoints return correct schemas
**File:** `backend/tests/test_auth_schemas.py` (new)

```python
"""Verify auth API response schemas are correct."""
from datetime import datetime
from app.schemas.auth_schema import (
    UnlockRequest, UnlockResponse, AuthStatusResponse,
    InitializeRequest, InitializeResponse,
)


class TestUnlockRequest:
    def test_minimal(self):
        req = UnlockRequest(passkey="123456")
        assert req.passkey == "123456"
        assert req.is_developer is False

    def test_developer_mode(self):
        req = UnlockRequest(passkey="dev-key", is_developer=True)
        assert req.is_developer is True


class TestUnlockResponse:
    def test_success(self):
        resp = UnlockResponse(
            success=True, role="OWNER",
            message="Unlocked", license_status="ACTIVE", grace_days=0,
        )
        assert resp.success is True
        assert resp.role == "OWNER"


class TestInitializeRequest:
    def test_valid(self):
        req = InitializeRequest(owner_passkey="secure-pin-123")
        assert req.owner_passkey == "secure-pin-123"
        assert req.license_id == "DEV-LOCAL-001"

    def test_custom_license_id(self):
        req = InitializeRequest(owner_passkey="pin", license_id="CUSTOM-001")
        assert req.license_id == "CUSTOM-001"


class TestInitializeResponse:
    def test_success(self):
        resp = InitializeResponse(
            success=True, message="Done", hardware_id="abc123",
        )
        assert resp.hardware_id == "abc123"
```

---

## File Changes Summary

| File | Action | Task |
|------|--------|------|
| `tests/test_models.py` | Create | T3 |
| `tests/test_auth_schemas.py` | Create | T4 |
| `tests/factories.py` | Create | T2 |

---

## Execution Order

1. T1 (verify models) — no code, just audit
2. T2 (factories) — new file
3. T3 (model tests) — new file, depends on models
4. T4 (auth schema tests) — new file, independent

---

## Validation

- `uv run ruff check .` — 0 errors
- `uv run pytest tests/ -v` — all pass (existing 57 + new ~25)
