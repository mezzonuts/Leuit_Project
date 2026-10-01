# Plan: Hari 8 — Frontend: Dashboard Monitoring

> **Scope:** `frontend/src/components/dashboard/`
> **Status:** Components may not exist yet. Create from scratch.

---

## Tasks

### Task 1: Create ValuationMetricCard.tsx
- Metric card showing total valuation
- CSV export button
- Uses Recharts or simple display

### Task 2: Create UsageTrendBarChart.tsx
- Bar chart showing 30-day usage trend
- Recharts integration
- Date range filter

### Task 3: Create CriticalAlertsSection.tsx
- Low stock alerts (pulse icon <3 days)
- Expiry warnings
- Link to relevant pages

### Task 4: Create StockHealthTable.tsx
- Table showing stock health per ingredient
- Progress bar with threshold indicators
- Color coding (safe/warning/danger)

### Task 5: Dashboard Integration
- Assemble all components in Dashboard page
- API data fetching
- Loading and error states

### Task 6: Dashboard Tests
- Component unit tests
- Integration tests

---

## Execution
1. T1-T4 (parallel) → individual components
2. T5 (integration) → assemble dashboard
3. T6 (tests) → test all components

## Validation
- pnpm lint: 0 errors
- pnpm typecheck: 0 errors
- pnpm test: all pass
