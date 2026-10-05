# Plan: Hari 8 Frontend: Dashboard Monitoring — Bug Fix & Enhancement

**Scope:** `frontend/src/components/dashboard/`, `frontend/src/components/bom/RecipeScalerTool.tsx`, `frontend/public/`

**Status:** Existing components need fixes — 8 issues found during testing

---

## Issues Found During Testing

### Critical Bugs

| # | Error | File | Root Cause |
|---|-------|------|------------|
| **B1** | `Cannot read properties of undefined (reading 'map')` at `RecipeScalerTool.tsx:133` | `RecipeScalerTool.tsx` | `result.items` is undefined — API response shape mismatch. Mutation returns data but `items` array not accessed correctly. |
| **B2** | `GET /icons/icon-192.png 404 (Not Found)` + `manifest error: resource isn't a valid image` | `manifest.json` | PWA icons reference `/icons/icon-192.png` but SVG files exist, not PNG. Browser can't render SVG as manifest icon. |
| **B3** | Dashboard shows `Rp 0` for all metrics | `Dashboard.tsx:13` | Wrong API endpoint: calls `/valuation` but backend is `/inventory/valuation/summary` |
| **B4** | "Stok Rendah" and "Segera Kadaluwarsa" show `Rp 0` | `ValuationMetricCard.tsx:24` | Component always uses `formatRupiah()` — counts should display as numbers, not currency |

### Data/UX Issues

| # | Issue | File | Expected Behavior |
|---|-------|------|-------------------|
| **B5** | "Trend 30 Hari" shows inventory count, not usage trend | `Dashboard.tsx:78` | Should show count of ingredients with usage history, or total usage quantity |
| **B6** | Progress bar shows `400%` for `20 pcs Min: 5` | `StockHealthTable.tsx` / `formatters.ts` | Progress should cap at 100% or normalize (20/5 = 400% is mathematically correct but UI should cap display at 100%) |
| **B7** | Usage Trend chart is bar-per-day, not per-category | `UsageTrendBarChart.tsx` | User wants bar chart grouped by ingredient category, with user-addable categories |
| **B8** | Missing ingredient categories entirely | Backend + Frontend | Need `IngredientCategory` model + CRUD + category field on Ingredient |

---

## Fix Tasks

### Fix 1 (B1): RecipeScalerTool crash — undefined items

**File:** `frontend/src/components/bom/RecipeScalerTool.tsx`

```tsx
// Line ~133: Change from:
{result?.items?.map((item) => (...))}

// To:
const items = Array.isArray(result?.items) ? result.items : []
{items.map((item) => (...))}
```

Also check the mutation response shape — the backend `/bom/scaler` endpoint returns `RecipeScalerResponse` with `items` field. Verify the API returns `{ items: [...] }` not `{ data: { items: [...] } }`.

---

### Fix 2 (B2): PWA icon 404 — SVG not supported as manifest icons

**Files:** `frontend/public/manifest.json`, `frontend/public/icons/`

Browser manifest requires PNG icons. Current files are SVG. Fix:

1. Create PNG versions from SVG (or use canvas-generated PNGs)
2. Update `manifest.json` to reference PNG files
3. Add SVG fallback for non-PWA browsers

---

### Fix 3 (B3): Wrong valuation endpoint

**File:** `frontend/src/components/dashboard/Dashboard.tsx`

```tsx
// Line 13: Change from:
queryFn: () => api.get('/valuation').then(res => res.data),

// To:
queryFn: () => api.get('/inventory/valuation/summary').then(res => res.data),
```

---

### Fix 4 (B4): ValuationMetricCard — support count format

**File:** `frontend/src/components/dashboard/ValuationMetricCard.tsx`

Add `format` prop to support both currency and count display:

```tsx
interface ValuationMetricCardProps {
  title: string
  value: number
  icon: React.ReactNode
  iconColor?: string
  bgColor?: string
  subtitle?: string
  format?: 'currency' | 'count'  // NEW
}

// In render:
{format === 'count' 
  ? value.toLocaleString('id-ID') 
  : formatRupiah(value)}
```

**Dashboard.tsx** — update cards:
```tsx
<ValuationMetricCard title="Stok Rendah" value={...} format="count" ... />
<ValuationMetricCard title="Segera Kadaluwarsa" value={...} format="count" ... />
<ValuationMetricCard title="Trend 30 Hari" value={...} format="count" ... />
```

---

### Fix 5 (B5): Trend 30 Hari — show correct metric

**File:** `frontend/src/components/dashboard/Dashboard.tsx`

The 4th metric card shows `stockHealth?.items?.length` (total inventory). Change to show actual trend data:

```tsx
// Option A: Show total usage in 30 days
<ValuationMetricCard
  title="Trend 30 Hari"
  value={usageTrend?.reduce((sum, item) => sum + item.total_quantity_used, 0) || 0}
  format="count"
  subtitle="Total qty terpakai 30 hari"
/>

// Option B: Show count of ingredients with usage
<ValuationMetricCard
  title="Trend 30 Hari"
  value={new Set(usageTrend?.map(item => item.ingredient_id)).size || 0}
  format="count"
  subtitle="Bahan dengan data historis"
/>
```

---

### Fix 6 (B6): Progress bar cap at 100%

**File:** `frontend/src/utils/formatters.ts`

```ts
export function getStockRatio(current: number, min: number): number {
  if (min <= 0) return 100
  return Math.min(Math.round((current / min) * 100), 100)  // Cap at 100
}

// Or add a separate display function:
export function getProgressDisplay(ratio: number): { display: string; capped: boolean } {
  const display = Math.min(ratio, 100)
  return { display: `${display}%`, capped: ratio > 100 }
}
```

Also update `StockHealthTable.tsx` to show "400% → 100%+" or similar indicator.

---

### Fix 7 (B7+B8): Usage Trend — per-category bar chart + ingredient categories

**Backend:**

1. Create `IngredientCategory` model:
```python
class IngredientCategory(Base):
    __tablename__ = "ingredient_categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    color = Column(String(7), default="#16a34a")  # hex color
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

2. Add `category_id` to `Ingredient` model (FK to categories)

3. Create `/api/v1/inventory/categories` CRUD endpoint

4. Modify `/inventory/usage-trend` to return category grouping:
```python
# Group usage by category
result = db.execute(text("""
    SELECT 
        c.name as category_name,
        c.color as category_color,
        SUM(du.total_quantity_used) as total_used,
        COUNT(DISTINCT du.ingredient_id) as ingredient_count
    FROM ingredient_daily_usage du
    JOIN ingredients i ON du.ingredient_id = i.id
    JOIN ingredient_categories c ON i.category_id = c.id
    WHERE du.usage_date >= :start_date
    GROUP BY c.id, c.name, c.color
    ORDER BY total_used DESC
"""), {"start_date": start_date}).fetchall()
```

**Frontend:**

1. Create `CategoryManager.tsx` — modal to add/edit/delete categories
2. Modify `UsageTrendBarChart.tsx`:
   - Group by category instead of per-day
   - Show stacked bar chart per category
   - Add "Manage Categories" button
3. Add category selector to ingredient drawer

---

### Fix 8: Category seed data (default)

```python
DEFAULT_CATEGORIES = [
    {"name": "Susu & Dairy", "color": "#3b82f6"},
    {"name": "Kopi & Teh", "color": "#8b5cf6"},
    {"name": "Gula & Pemanis", "color": "#f59e0b"},
    {"name": "Coklat & Powder", "color": "#78350f"},
    {"name": "Tepung & Bahan Kering", "color": "#a16207"},
    {"name": "Telur", "color": "#ca8a04"},
    {"name": "Mentega & Lemak", "color": "#eab308"},
    {"name": "Sirup & Flavoring", "color": "#06b6d4"},
    {"name": "Air & Minuman", "color": "#0ea5e9"},
    {"name": "Es & Pendingin", "color": "#67e8f9"},
]
```

---

## Execution Order

1. **B3** (wrong endpoint) — 1 line fix, immediate impact
2. **B4** (format prop) — small component change
3. **B1** (RecipeScaler crash) — critical crash fix
4. **B2** (PWA icons) — generate PNGs + update manifest
5. **B6** (progress cap) — formatter fix
6. **B5** (trend metric) — dashboard data fix
7. **B7+B8** (categories) — new model + CRUD + chart rework

## Validation

- All dashboard metrics show correct values
- No console errors
- RecipeScalerTool works without crash
- Progress bars cap at 100%
- Category bar chart renders with grouped data
- PWA icons load without 404