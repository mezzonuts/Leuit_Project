# Day 23 Implementation Report: Accessibility Audit (WCAG 2.1 AA)

**PR:** [#24 feat(day23): accessibility audit (WCAG 2.1 AA)](https://github.com/mezzonuts/Leuit_Project/pull/24)
**Merge commit:** `c25865cace0c37a65a3a7cb7e68d490804f7f580`
**Merged:** 2026-10-02T03:00:46Z
**Branch:** `feat/day23-a11y` → `staging`
**CI run:** `36957896562` — success

---

## Summary

Focus trap hook, accessible modal component, skip-navigation link, dan peningkatan ARIA pada layout (banner/navigation). 17 test a11y baru (modal 9, skipnav 3, datepicker 5).

---

## Changes

### Frontend

**`frontend/src/hooks/useFocusTrap.ts`** (new, 58 lines)
- `useFocusTrap(isOpen)` — return `containerRef` untuk container modal/drawer
- Saat open: simpan `document.activeElement`, focus ke focusable pertama
- Tab key: cycle first ↔ last (prevent default di batas)
- Cleanup: restore focus ke trigger element

**`frontend/src/components/ui/AccessibleModal.tsx`** (new, 51 lines)
- Props: `isOpen`, `onClose`, `title`, `children`
- `role="dialog"`, `aria-modal="true"`, `aria-label={title}`
- Close button: `aria-label="Tutup dialog"`
- Escape key → `onClose()`
- Focus trap via `useFocusTrap`

**`frontend/src/components/ui/SkipNav.tsx`** (new, 10 lines)
- `<a href="#main-content">Lewati ke konten utama</a>`
- `sr-only` sampai focus → `focus:not-sr-only` visible

**`frontend/src/components/layout/Sidebar.tsx`**
- `<nav role="navigation" aria-label="Menu navigasi">`

**`frontend/src/components/layout/Header.tsx`**
- `<header role="banner">`
- `<h1 aria-label={title}>`

**`frontend/src/components/ui/__tests__/AccessibleModal.test.tsx`** (new, 60 lines, 9 tests)
- renders when open / not when closed
- `role=dialog`, `aria-modal`, `aria-label`
- close button `aria-label` + click → `onClose`
- Escape → `onClose`
- renders children

**`frontend/src/components/ui/__tests__/SkipNav.test.tsx`** (new, 22 lines, 3 tests)
- skip link text, `href="#main-content"`, `sr-only` class

**`frontend/src/components/ui/__tests__/DateRangePicker.test.tsx`** (5 tests, pre-existing, counted in a11y gate)

---

## Quality Gates

| Gate | Result |
|------|--------|
| `pnpm typecheck` | 0 errors |
| `pnpm test` | 269 pass, 8 skipped (34 files) |
| CI | green (run 36957896562) |

---

## Diff Stat

```
frontend/src/components/layout/Header.tsx            |  4 +-
frontend/src/components/layout/Sidebar.tsx           |  2 +-
frontend/src/components/ui/AccessibleModal.tsx       | 51 +++++++++++++++++++
frontend/src/components/ui/SkipNav.tsx               | 10 ++++
frontend/src/components/ui/__tests__/AccessibleModal.test.tsx | 60 +++++++++++++++++++++
frontend/src/components/ui/__tests__/SkipNav.test.tsx | 22 +++++++
frontend/src/hooks/useFocusTrap.ts                   | 58 +++++++++++++++++++++
7 files changed, 204 insertions(+), 3 deletions(-)
```

---

## Notes

- Existing modals/drawers (`DatabaseUnlockModal`, `IngredientDrawer`, `PurchaseEntryDrawer`, `PosSyncDrawer`, `StockOpnameModal`) belum migrate ke `AccessibleModal`; plan Day 23 item 2 (focus trap di semua drawer) menyusul.
- SkipNav belum di-mount di `Layout.tsx`; perlu `<main id="main-content">` sebagai target.
- `aria-labelledby` belum dipakai — modal pakai `aria-label`; upgrade path: `useId` + `aria-labelledby` bila judul kompleks.
- Contrast, live region, `prefers-reduced-motion`, form error ARIA belum di-scope hari ini.
