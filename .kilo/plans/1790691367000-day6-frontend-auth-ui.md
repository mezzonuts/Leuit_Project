# Plan: Hari 6 Frontend: Vite + React + Tailwind + Auth UI

**Scope:** `frontend/src/components/auth/`, `frontend/src/components/layout/`

> **Status:** Frontend components exist. Verify completeness + add tests.

---

## Existing State

- `DatabaseUnlockModal.tsx` (173 lines) — unlock screen
- `KeyStatusIndicator.tsx` (34 lines) — license status badge
- `Layout.tsx` (150 lines) + `Sidebar.tsx` (81 lines) + `Header.tsx` (47 lines)
- `LicenseGraceBanner.tsx` (48 lines)
- TanStack Query setup, routing, Zustand stores

---

## Tasks

### Task 1: Verify auth UI completeness

Audit frontend auth components:
- DatabaseUnlockModal — PIN input, submit, loading state, error display
- KeyStatusIndicator — status badge (active/grace/locked)
- LicenseGraceBanner — warning banner countdown
- Layout + Sidebar — navigation structure

### Task 2: auth component unit tests

Create `frontend/src/components/auth/__tests__/` tests:
- DatabaseUnlockModal renders correctly
- Form validation (min length)
- Loading state toggle
- Error message display

### Task 3: layout component tests

Create `frontend/src/components/layout/__tests__/` tests:
- Sidebar renders navigation items
- Header displays app title
- Layout wraps children

---

## Execution

1. T1 (audit) → verify components
2. T2 (auth tests) → new files
3. T3 (layout tests) → new files

---

## Validation

- pnpm lint: 0 errors
- pnpm typecheck: 0 errors
- pnpm test: all pass
