# Plan: Hari 8 Frontend: Dashboard Monitoring

**Scope:** `frontend/src/components/dashboard/`

**Status:** New components — ValuationMetricCard, UsageTrendBarChart, CriticalAlertsSection, StockHealthTable

---

## Tasks

### Task 1: Create dashboard components

Create in `frontend/src/components/dashboard/`:
- `ValuationMetricCard.tsx` — metric card with CSV export button, shows total stock value, unit count, avg margin
- `UsageTrendBarChart.tsx` — Recharts bar chart 30-day usage trend with date range filter (7d/30d/90d)
- `CriticalAlertsSection.tsx` — alerts for ingredients expiring <3 days, pulsing icon, dismissible
- `StockHealthTable.tsx` — table with progress bar threshold (green/yellow/red), sortable columns

### Task 2: Add dashboard component tests

Create `frontend/src/components/dashboard/__tests__/`:
- `ValuationMetricCard.test.tsx` — renders metrics, CSV export triggers download
- `UsageTrendBarChart.test.tsx` — renders chart, filter changes data, tooltip works
- `CriticalAlertsSection.test.tsx` — shows alerts for expiring items, dismiss works
- `StockHealthTable.test.tsx` — renders table, progress bar colors match thresholds, sorting works

### Task 3: Integrate dashboard into layout

- Add dashboard route in `App.tsx`
- Update sidebar navigation with Dashboard link
- Wire components into `DashboardPage.tsx` (new)

---

## Execution

1. T1 (create components) → new files in `frontend/src/components/dashboard/`
2. T2 (tests) → new test files
3. T3 (integration) → routing + navigation

## Validation

- pnpm lint: 0 errors
- pnpm typecheck: 0 errors
- pnpm test: all pass
- Recharts renders without console errors