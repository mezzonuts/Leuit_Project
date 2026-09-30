# Plan: Hari 4 Backend: Inventory CRUD + Valuation

**Scope:** `backend/app/api/v1/inventory.py`, `backend/app/schemas/ingredient_schema.py`

**Status:** Inventory router exists (318 lines). Audit completeness + missing validation.

---

## Existing State

- `inventory.py` router: 318 lines CRUD, stock-opname, valuation, CSV export
- `ingredient_schema.py`: IngredientCreate, IngredientUpdate, IngredientResponse, StockOpnameRequest, ValuationSummary
- Tests: model tests (44) cover Ingredient properties

---

## Tasks

Task 1: Verify inventory CRUD completeness
Audit `backend/app/api/v1/inventory.py`:
- GET /inventory (list pagination, search)
- POST /inventory (create)
- GET /inventory/{id} (detail)
- PUT /inventory/{id} (update)
- DELETE /inventory/{id} (soft delete via is_active)
- POST /inventory/stock-opname (stock adjustment)
- GET /valuation (valuation summary)
- GET /valuation/export-csv (CSV download)

Task 2: Add inventory API integration tests
Create `backend/tests/test_inventory_api.py`:
- Test endpoint mocked DB
- Test pagination, search, threshold alerts
- Test stock-opname flow
- Test valuation calculation

Task 3: input validation hardening
- Barcode SKU format validation (alphanumeric + dash)
- Unit enum validation (ml, gram, pcs)
- Cost per unit > 0
- Shelf life days > 0
- Stock cannot be negative

---

## Execution

1. T1 (audit) → no code, just verify
2. T2 (tests) → new file
3. T3 (validation) → edit schemas

## Validation

- ruff: 0 errors
- mypy: 0 errors
- pytest: all pass
