# Plan: Hari 9 — Frontend: BOM + Recipe Scaler

> **Scope:** `frontend/src/components/bom/`
> **Status:** Components may not exist yet. Create from scratch.

---

## Tasks

### Task 1: Create RecipeList.tsx
- List of recipes/BOM items
- Search/filter functionality
- Click to view/edit recipe

### Task 2: Create RecipeDrawer.tsx
- Slide-over drawer for recipe details
- View/edit recipe ingredients
- Add/remove ingredients

### Task 3: Create RecipeScalerTool.tsx
- Simulasi porsi vs stok real-time
- Scale recipe quantities
- Show available portions based on stock

### Task 4: BOM Tests
- Component unit tests
- Integration tests

---

## Execution
1. T1 (RecipeList) → independent
2. T2 (RecipeDrawer) → depends on T1
3. T3 (RecipeScalerTool) → independent
4. T4 (tests) → after all components

## Validation
- pnpm lint: 0 errors
- pnpm typecheck: 0 errors
- pnpm test: all pass
