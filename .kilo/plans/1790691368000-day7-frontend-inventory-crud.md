# Plan: Hari 7 Frontend: Inventory CRUD + Slide-Over Drawer

**Scope:** `frontend/src/components/inventory/`, `frontend/src/components/auth/BarcodeCameraModal.tsx`

**Status:** Inventory components exist (232 lines). Verify completeness + tests.

---

## Existing State

- `Inventory.tsx` (232 lines) table, search, pagination, actions
- `IngredientDrawer.tsx` (230 lines) slide-over CRUD form RHF + Zod
- `StockOpnameModal.tsx` (91 lines) stock adjustment modal
- `BarcodeCameraModal.tsx` (163 lines) — BarcodeDetector API

---

## Tasks

### Task 1: Verify inventory CRUD completeness

Audit components:
- Inventory table search, pagination, actions (edit, delete, stock-opname)
- IngredientDrawer 450px slide-over RHF + Zod validation
- StockOpnameModal — quantity input + previous/new/difference
- BarcodeCameraModal — BarcodeDetector API, fallback manual input

### Task 2: Add inventory component tests

Create `frontend/src/components/inventory/__tests__/`:
- Inventory table renders, search filters, pagination works
- IngredientDrawer opens on edit/create, validation works
- StockOpnameModal calculates difference correctly
- BarcodeCameraModal handles camera permission + fallback

### Task 3: Add barcode camera tests

Create `frontend/src/components/auth/__tests__/BarcodeCameraModal.test.tsx`:
- Camera permission request
- Barcode detection callback
- Manual fallback input
- Cleanup on unmount

---

## Execution

1. T1 (audit) → verify components
2. T2 (inventory tests) → new files
3. T3 (barcode tests) → new file

## Validation

- pnpm lint: 0 errors
- pnpm typecheck: 0 errors
- pnpm test: all pass