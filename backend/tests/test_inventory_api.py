"""Integration inventory API endpoints."""

from collections.abc import Generator
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.v1.deps import get_db, verify_license
from app.core import database as db_module
from app.main import app


@pytest.fixture()
def mock_db() -> MagicMock:
    """Create mock DB session."""
    return MagicMock()


@pytest.fixture()
def client(mock_db: MagicMock) -> Generator[TestClient, None, None]:
    """Test client with mocked dependencies."""
    original_engine = db_module._engine
    fake_engine = MagicMock()
    db_module._engine = fake_engine
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[verify_license] = lambda: {"status": "ACTIVE", "role": "OWNER"}

    import app.main as main_mod
    original_main_engine = main_mod._engine
    main_mod._engine = fake_engine

    c = TestClient(app, raise_server_exceptions=False)
    yield c

    db_module._engine = original_engine
    main_mod._engine = original_main_engine
    app.dependency_overrides.clear()


def _make_ingredient(**overrides: object) -> MagicMock:
    """Build a mock Ingredient ORM object with computed properties."""
    defaults: dict[str, object] = dict(
        id=1,
        barcode_sku="SKU001",
        name="Tepung Terigu",
        unit="gram",
        cost_per_unit=8000,
        shelf_life_days=30,
        current_stock=500,
        min_stock_threshold=100,
        lead_time_days=1,
        is_active=True,
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        updated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    defaults.update(overrides)
    m = MagicMock()
    for k, v in defaults.items():
        setattr(m, k, v)
    cur = float(defaults["current_stock"])  # type: ignore[arg-type]
    thresh = float(defaults["min_stock_threshold"])  # type: ignore[arg-type]
    m.stock_ratio = round((cur / thresh) * 100, 1) if thresh > 0 else 100.0
    ratio: float = m.stock_ratio
    m.stock_status = "safe" if ratio >= 150 else "warning" if ratio >= 100 else "danger"
    m.valuation = round(cur * float(defaults["cost_per_unit"]), 2)  # type: ignore[arg-type]
    m.days_until_expiry = int(defaults["shelf_life_days"])  # type: ignore[call-overload]
    return m


class TestGetIngredients:
    def test_list_empty(self, client: TestClient, mock_db: MagicMock) -> None:
        mock_db.query.return_value.filter.return_value.count.return_value = 0
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        response = client.get("/api/v1/inventory")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_list_with_data(self, client: TestClient, mock_db: MagicMock) -> None:
        ing = _make_ingredient()
        mock_db.query.return_value.filter.return_value.count.return_value = 1
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [ing]
        response = client.get("/api/v1/inventory")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Tepung Terigu"

    def test_list_search(self, client: TestClient, mock_db: MagicMock) -> None:
        mock_db.query.return_value.filter.return_value.count.return_value = 0
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        response = client.get("/api/v1/inventory?search=tepung")
        assert response.status_code == 200

    def test_list_active_only(self, client: TestClient, mock_db: MagicMock) -> None:
        mock_db.query.return_value.filter.return_value.count.return_value = 0
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        response = client.get("/api/v1/inventory?active_only=true")
        assert response.status_code == 200


class TestGetIngredientDetail:
    def test_get_by_id(self, client: TestClient, mock_db: MagicMock) -> None:
        ing = _make_ingredient()
        mock_db.query.return_value.filter.return_value.first.return_value = ing
        response = client.get("/api/v1/inventory/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Tepung Terigu"

    def test_get_not_found(self, client: TestClient, mock_db: MagicMock) -> None:
        mock_db.query.return_value.filter.return_value.first.return_value = None
        response = client.get("/api/v1/inventory/999")
        assert response.status_code == 404


class TestCreateIngredient:
    def test_create_success(self, client: TestClient, mock_db: MagicMock) -> None:
        mock_db.query.return_value.filter.return_value.first.return_value = None
        ing = _make_ingredient()
        mock_db.refresh.side_effect = lambda x: None

        with patch("app.api.v1.inventory.Ingredient", return_value=ing):
            response = client.post(
                "/api/v1/inventory",
                json={
                    "name": "Tepung Terigu",
                    "unit": "gram",
                    "cost_per_unit": 8000,
                    "shelf_life_days": 30,
                    "current_stock": 500,
                    "min_stock_threshold": 100,
                },
            )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Tepung Terigu"

    def test_create_duplicate_barcode(self, client: TestClient, mock_db: MagicMock) -> None:
        existing = _make_ingredient()
        mock_db.query.return_value.filter.return_value.first.return_value = existing
        response = client.post(
            "/api/v1/inventory",
            json={
                "name": "Gula",
                "unit": "gram",
                "barcode_sku": "SKU001",
                "cost_per_unit": 10000,
                "shelf_life_days": 60,
            },
        )
        assert response.status_code == 400


class TestUpdateIngredient:
    def test_update_success(self, client: TestClient, mock_db: MagicMock) -> None:
        ing = _make_ingredient()
        mock_db.query.return_value.filter.return_value.first.return_value = ing
        mock_db.refresh.side_effect = lambda x: None
        response = client.put(
            "/api/v1/inventory/1",
            json={"name": "Updated Name"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"

    def test_update_not_found(self, client: TestClient, mock_db: MagicMock) -> None:
        mock_db.query.return_value.filter.return_value.first.return_value = None
        response = client.put(
            "/api/v1/inventory/999",
            json={"name": "Test"},
        )
        assert response.status_code == 404

    def test_update_duplicate_barcode(self, client: TestClient, mock_db: MagicMock) -> None:
        ing = _make_ingredient(barcode_sku="SKU001")
        conflict = _make_ingredient(id=2, barcode_sku="SKU002")
        mock_db.query.return_value.filter.return_value.first.side_effect = [ing, conflict]
        mock_db.refresh.side_effect = lambda x: None
        response = client.put(
            "/api/v1/inventory/1",
            json={"barcode_sku": "SKU002"},
        )
        assert response.status_code == 400


class TestDeleteIngredient:
    def test_soft_delete(self, client: TestClient, mock_db: MagicMock) -> None:
        ing = _make_ingredient()
        mock_db.query.return_value.filter.return_value.first.return_value = ing
        response = client.delete("/api/v1/inventory/1")
        assert response.status_code == 204

    def test_delete_not_found(self, client: TestClient, mock_db: MagicMock) -> None:
        mock_db.query.return_value.filter.return_value.first.return_value = None
        response = client.delete("/api/v1/inventory/999")
        assert response.status_code == 404


class TestStockOpname:
    def test_stock_opname_success(self, client: TestClient, mock_db: MagicMock) -> None:
        from datetime import datetime as dt

        ing = _make_ingredient(current_stock=500)
        mock_db.query.return_value.filter.return_value.first.return_value = ing
        with patch("app.api.v1.inventory.func") as mock_func:
            mock_func.now.return_value = dt(2026, 9, 30, tzinfo=UTC)
            response = client.post(
                "/api/v1/inventory/1/stock-opname",
                json={"quantity": 600},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["previous_stock"] == 500
        assert data["new_stock"] == 600
        assert data["difference"] == 100

    def test_stock_opname_not_found(self, client: TestClient, mock_db: MagicMock) -> None:
        mock_db.query.return_value.filter.return_value.first.return_value = None
        response = client.post(
            "/api/v1/inventory/999/stock-opname",
            json={"quantity": 100},
        )
        assert response.status_code == 404


class TestValuationEndpoints:
    def test_valuation_summary(self, client: TestClient, mock_db: MagicMock) -> None:
        ing = _make_ingredient(current_stock=500, cost_per_unit=8000, min_stock_threshold=100, shelf_life_days=30)
        mock_db.query.return_value.filter.return_value.all.return_value = [ing]
        response = client.get("/api/v1/inventory/valuation/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_valuation" in data
        assert "total_ingredients" in data
        assert "low_stock_count" in data
        assert "expired_soon_count" in data

    def test_valuation_summary_low_stock(self, client: TestClient, mock_db: MagicMock) -> None:
        ing = _make_ingredient(current_stock=50, cost_per_unit=8000, min_stock_threshold=100, shelf_life_days=30)
        mock_db.query.return_value.filter.return_value.all.return_value = [ing]
        response = client.get("/api/v1/inventory/valuation/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["low_stock_count"] == 1

    def test_valuation_summary_expired_soon(self, client: TestClient, mock_db: MagicMock) -> None:
        ing = _make_ingredient(shelf_life_days=2)
        mock_db.query.return_value.filter.return_value.all.return_value = [ing]
        response = client.get("/api/v1/inventory/valuation/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["expired_soon_count"] == 1

    def test_valuation_items(self, client: TestClient, mock_db: MagicMock) -> None:
        ing = _make_ingredient()
        mock_db.query.return_value.filter.return_value.all.return_value = [ing]
        response = client.get("/api/v1/inventory/valuation/items")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == 1
        assert data[0]["barcode_sku"] == "SKU001"
        assert data[0]["total_valuation"] == 8000 * 500

    def test_valuation_export_csv(self, client: TestClient, mock_db: MagicMock) -> None:
        ing = _make_ingredient()
        mock_db.query.return_value.filter.return_value.all.return_value = [ing]
        response = client.get("/api/v1/inventory/valuation/export-csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
        assert "valuasi-aset.csv" in response.headers.get("content-disposition", "")
        body = response.text
        assert "Nama Bahan" in body
        assert "Tepung Terigu" in body


class TestUsageTrend:
    def test_usage_trend_empty(self, client: TestClient, mock_db: MagicMock) -> None:
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        response = client.get("/api/v1/inventory/usage-trend")
        assert response.status_code == 200
        assert response.json() == []

    def test_usage_trend_with_data(self, client: TestClient, mock_db: MagicMock) -> None:
        usage = MagicMock()
        usage.usage_date = datetime(2026, 9, 1, tzinfo=UTC)
        usage.ingredient_id = 1
        usage.ingredient = MagicMock()
        usage.ingredient.name = "Tepung"
        usage.total_quantity_used = 50.5
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [usage]
        response = client.get("/api/v1/inventory/usage-trend")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["ingredient_id"] == 1
        assert data[0]["total_quantity_used"] == 50.5


class TestCriticalAlerts:
    def test_alerts_empty(self, client: TestClient, mock_db: MagicMock) -> None:
        mock_db.query.return_value.filter.return_value.all.return_value = []
        response = client.get("/api/v1/inventory/alerts")
        assert response.status_code == 200
        assert response.json() == []

    def test_alerts_low_stock(self, client: TestClient, mock_db: MagicMock) -> None:
        ing = _make_ingredient(current_stock=50, min_stock_threshold=100)
        mock_db.query.return_value.filter.return_value.all.return_value = [ing]
        response = client.get("/api/v1/inventory/alerts")
        assert response.status_code == 200
        data = response.json()
        assert any(a["type"] == "stock_low" for a in data)
        stock_alert = [a for a in data if a["type"] == "stock_low"][0]
        assert stock_alert["severity"] == "medium"

    def test_alerts_critical_low_stock(self, client: TestClient, mock_db: MagicMock) -> None:
        ing = _make_ingredient(current_stock=10, min_stock_threshold=100)
        mock_db.query.return_value.filter.return_value.all.return_value = [ing]
        response = client.get("/api/v1/inventory/alerts")
        assert response.status_code == 200
        data = response.json()
        stock_alert = [a for a in data if a["type"] == "stock_low"][0]
        assert stock_alert["severity"] == "high"

    def test_alerts_expiry(self, client: TestClient, mock_db: MagicMock) -> None:
        ing = _make_ingredient(shelf_life_days=2)
        mock_db.query.return_value.filter.return_value.all.return_value = [ing]
        response = client.get("/api/v1/inventory/alerts")
        assert response.status_code == 200
        data = response.json()
        expiry_alerts = [a for a in data if a["type"] == "expiry"]
        assert len(expiry_alerts) >= 1

    def test_alerts_critical_expiry(self, client: TestClient, mock_db: MagicMock) -> None:
        ing = _make_ingredient(shelf_life_days=1)
        mock_db.query.return_value.filter.return_value.all.return_value = [ing]
        response = client.get("/api/v1/inventory/alerts")
        assert response.status_code == 200
        data = response.json()
        expiry_alerts = [a for a in data if a["type"] == "expiry"]
        assert expiry_alerts[0]["severity"] == "high"


class TestIngredientSchemaValidation:
    def test_create_valid(self) -> None:
        from app.schemas.ingredient_schema import IngredientCreate

        data = IngredientCreate(
            name="Test Ingredient",
            unit="gram",
            cost_per_unit=8000,
            shelf_life_days=30,
            current_stock=500,
            min_stock_threshold=100,
        )
        assert data.name == "Test Ingredient"
        assert data.unit == "gram"
        assert data.cost_per_unit == 8000
        assert data.shelf_life_days == 30

    def test_invalid_unit_rejected(self) -> None:
        from pydantic import ValidationError

        from app.schemas.ingredient_schema import IngredientCreate

        with pytest.raises(ValidationError):
            IngredientCreate(name="Test", unit="kg", cost_per_unit=1000, shelf_life_days=7,
                             barcode_sku=None, current_stock=0, min_stock_threshold=0, lead_time_days=1)

    def test_valid_units_accepted(self) -> None:
        from app.schemas.ingredient_schema import IngredientCreate

        for unit in ["ml", "gram", "pcs"]:
            data = IngredientCreate(name="Test", unit=unit, cost_per_unit=1000, shelf_life_days=7,
                                    barcode_sku=None, current_stock=0, min_stock_threshold=0, lead_time_days=1)
            assert data.unit == unit

    def test_negative_cost_rejected(self) -> None:
        from pydantic import ValidationError

        from app.schemas.ingredient_schema import IngredientCreate

        with pytest.raises(ValidationError):
            IngredientCreate(name="Test", unit="gram", cost_per_unit=-100, shelf_life_days=7,
                             barcode_sku=None, current_stock=0, min_stock_threshold=0, lead_time_days=1)

    def test_zero_shelf_life_rejected(self) -> None:
        from pydantic import ValidationError

        from app.schemas.ingredient_schema import IngredientCreate

        with pytest.raises(ValidationError):
            IngredientCreate(name="Test", unit="gram", cost_per_unit=1000, shelf_life_days=0,
                             barcode_sku=None, current_stock=0, min_stock_threshold=0, lead_time_days=1)

    def test_negative_stock_rejected(self) -> None:
        from pydantic import ValidationError

        from app.schemas.ingredient_schema import IngredientCreate

        with pytest.raises(ValidationError):
            IngredientCreate(name="Test", unit="gram", cost_per_unit=1000, shelf_life_days=7,
                             current_stock=-10, barcode_sku=None, min_stock_threshold=0, lead_time_days=1)

    def test_empty_name_rejected(self) -> None:
        from pydantic import ValidationError

        from app.schemas.ingredient_schema import IngredientCreate

        with pytest.raises(ValidationError):
            IngredientCreate(name="", unit="gram", cost_per_unit=1000, shelf_life_days=7,
                             barcode_sku=None, current_stock=0, min_stock_threshold=0, lead_time_days=1)

    def test_update_partial(self) -> None:
        from app.schemas.ingredient_schema import IngredientUpdate

        data = IngredientUpdate(
            name="New Name",
            barcode_sku=None, unit=None, cost_per_unit=None,
            shelf_life_days=None, current_stock=None, min_stock_threshold=None, lead_time_days=None,
        )
        assert data.name == "New Name"
        assert data.unit is None
        assert data.cost_per_unit is None

    def test_create_missing_unit(self) -> None:
        from pydantic import ValidationError

        from app.schemas.ingredient_schema import IngredientCreate

        with pytest.raises(ValidationError):
            IngredientCreate(name="Test", cost_per_unit=1000, shelf_life_days=7)  # type: ignore[call-arg]


class TestStockOpnameSchemaValidation:
    def test_valid_quantity(self) -> None:
        from app.schemas.ingredient_schema import StockOpnameRequest

        data = StockOpnameRequest(quantity=100.5)
        assert data.quantity == 100.5

    def test_negative_quantity_rejected(self) -> None:
        from pydantic import ValidationError

        from app.schemas.ingredient_schema import StockOpnameRequest

        with pytest.raises(ValidationError):
            StockOpnameRequest(quantity=-10)


class TestValuationSchema:
    def test_summary_schema(self) -> None:
        from app.schemas.ingredient_schema import ValuationSummary

        v = ValuationSummary(
            total_valuation=5000000,
            total_ingredients=20,
            low_stock_count=3,
            expired_soon_count=1,
        )
        assert v.total_valuation == 5000000
        assert v.total_ingredients == 20
        assert v.low_stock_count == 3
        assert v.expired_soon_count == 1

    def test_item_schema(self) -> None:
        from app.schemas.ingredient_schema import ValuationItem

        v = ValuationItem(
            id=1,
            name="Tepung",
            barcode_sku="SKU001",
            current_stock=100,
            unit="gram",
            cost_per_unit=8000,
            total_valuation=800000,
            shelf_life_days=30,
            min_stock_threshold=50,
        )
        assert v.total_valuation == 800000
        assert v.current_stock == 100
        assert v.cost_per_unit == 8000
