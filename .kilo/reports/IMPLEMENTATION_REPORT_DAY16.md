# Laporan Implementasi — Day 16: Multi-Outlet Support

**Proyek:** LEUIT (Local-First F&B Demand & Inventory Forecasting)
**Tanggal:** 2026-10-02
**PR:** #17 — `feat(day16): multi-outlet support`
**Status:** ✅ Merged ke `staging` (commit `19e8fb2f`)

---

## 1. Executive Summary

Day 16 menambahkan dukungan multi-outlet ke LEUIT. Model `Outlet` baru (tabel `outlets`) beserta Pydantic schemas (`OutletCreate`/`OutletUpdate`/`OutletResponse`/`OutletListResponse`) dan router CRUD `GET/POST/PUT /api/v1/outlets` (4 endpoint, semua di-guard `verify_license`). Kolom `outlet_id` nullable ditambahkan ke `Ingredient` dan `InventoryPurchase` sehingga skema lama tetap backward compatible. Endpoint baru `GET /api/v1/reports/consolidated` mengembalikan laporan per-outlet (valuation, purchases, sales_count, ingredient_count) plus summary lintas outlet; bila `outlet_id` diberikan, filter per outlet; bila tidak, agregasi gabungan outlet aktif termasuk baris legacy `outlet_id IS NULL`. Di frontend, komponen `OutletSwitcher` (dropdown header dengan opsi "Semua Outlet") dan zustand slice `useOutletStore` dengan persist manual ke `localStorage` key `leuit_current_outlet`; `Header` sekarang merender switcher. Deliverable utama: 9 test backend (`test_multi_outlet.py`) + 4 test frontend (`OutletSwitcher.test.tsx`), 518 baris ditambah, quality gates hijau (ruff 0, pytest 285 pass, typecheck 0, pnpm test 222 pass / 8 skipped), CI green.

---

## 2. Files Changed

| File | Perubahan |
|------|-----------|
| `backend/app/models/outlet.py` | Model baru `Outlet` — kolom `id`, `name`, `address`, `phone`, `is_active`, `settings` (JSON string), `created_at`, `updated_at`; `__repr__` + `to_dict` |
| `backend/app/models/ingredient.py` | Tambah kolom `outlet_id` (nullable) |
| `backend/app/models/purchase.py` | Tambah kolom `outlet_id` (nullable) pada `InventoryPurchase` |
| `backend/app/models/__init__.py` | Export `Outlet` |
| `backend/app/schemas/outlet_schema.py` | Skema baru: `OutletBase`, `OutletCreate`, `OutletUpdate` (partial update), `OutletResponse`, `OutletListResponse` |
| `backend/app/api/v1/outlets.py` | Router baru `prefix="/outlets"`: `GET /outlets`, `POST /outlets`, `GET /outlets/{outlet_id}` (404 bila tidak ada), `PUT /outlets/{outlet_id}` (partial update via `exclude_unset`) |
| `backend/app/api/v1/reports.py` | Router baru `prefix="/reports"`: `GET /reports/consolidated` — breakdown per outlet + summary (`total_valuation`, `total_purchases`, `total_sales_count`, `outlet_count`, `period_days`), filter opsional `outlet_id`, rentang `days` (1–365) |
| `backend/app/api/v1/__init__.py` | Register router `outlets` + `reports` |
| `backend/tests/test_multi_outlet.py` | File test baru — 9 test (lihat bagian 3) |
| `frontend/src/components/layout/OutletSwitcher.tsx` | Komponen baru: fetch `/outlets` via react-query, dropdown `<select>` aria-label "Pilih outlet", opsi "Semua Outlet", persist ke localStorage |
| `frontend/src/components/layout/Header.tsx` | Header merender `OutletSwitcher` |
| `frontend/src/components/layout/__tests__/OutletSwitcher.test.tsx` | File test baru — 4 test |
| `frontend/src/components/layout/__tests__/Header.test.tsx` | Mock OutletSwitcher (null) agar test header eksisting tetap stabil |
| `frontend/src/stores/index.ts` | Slice baru `useOutletStore`: `current_outlet_id`, `outlets`, `setCurrentOutlet` (persist `leuit_current_outlet`), `setOutlets` |

**Statistik:** 14 file, +518 / −2 baris.

---

## 3. Test Coverage

**Total: 13 test baru** — 9 backend + 4 frontend. Semua lulus.

### Backend — `backend/tests/test_multi_outlet.py` (9 test)

| Kelas Test | Jumlah | Cakupan |
|------------|--------|---------|
| `TestOutletModel` | 2 | `__repr` berisi nama outlet; `to_dict` mengembalikan field benar |
| `TestOutletSchemas` | 4 | `OutletCreate` default `is_active=True`; `OutletUpdate` partial (field lain `None`); `OutletResponse` struktur; `OutletListResponse` kosong `total=0` |
| `TestConsolidatedReport` | 1 | Struktur respons: `reports`, `summary` (`total_valuation`, `outlet_count`), `generated_at` |
| `TestOutletAPI` | 2 | Router terdaftar `prefix="/outlets"` + routes > 0; router `prefix="/reports"` + routes > 0 |

### Frontend — `OutletSwitcher.test.tsx` (4 test)

| Test | Cakupan |
|------|---------|
| renders outlet select dropdown | `getByLabelText('Pilih outlet')` ada |
| shows "Semua Outlet" option | opsi default ada |
| shows outlet names in dropdown | nama outlet (Cafe A, Cafe B) tampil |
| renders Store icon | ikon SVG `lucide-react` dirender |

**Total suite: pytest 285 pass · pnpm test 222 pass, 8 skipped**

---

## 4. Quality Gates

| Gate | Tool | Hasil |
|------|------|-------|
| Backend lint | `uv run ruff check .` | ✅ 0 errors |
| Backend test | `uv run pytest` | ✅ 285 pass |
| Frontend typecheck | `pnpm typecheck` | ✅ 0 errors |
| Frontend test | `pnpm test` | ✅ 222 pass, 8 skipped |
| CI | GitHub Actions | ✅ Green |

---

## 5. Architecture Compliance

Sesuai Backend Architecture v1.0, Frontend Architecture v1.8, dan PRD v1.8:

| Aspek | Implementasi |
|------|----------------|
| **Local-first** | Tabel `outlets` di SQLite lokal; tidak ada multi-tenant cloud |
| **Backward compatible** | `outlet_id` nullable pada `Ingredient`/`InventoryPurchase` — data lama tanpa outlet tetap valid; query consolidated menangkap `outlet_id IS NULL` |
| **API pattern** | Query param `outlet_id` konsisten dengan endpoint forecast Day 15; semua endpoint di-guard `verify_license` |
| **Response shape** | `outlets` memakai `OutletListResponse`/`OutletResponse`; consolidated report berstruktur dict `reports` + `summary` + `generated_at` |
| **UI pattern** | Switcher di `Header` mengikuti konvensi komponen layout PR #7–#12; state via zustand + localStorage seperti store eksisting |
| **YAGNI** | Belum ada role/permission per outlet, belum ada hierarchy cabang induk/anak |

---

## 6. CI Iterations

**Jumlah iterasi: 1** (quality gates hijau sejak awal — ruff, pytest, typecheck, pnpm test, CI semua hijau sebelum PR dibuat).

---

## 7. Commands to Resume

```bash
cd D:\Project\Leuit
git checkout staging && git pull origin staging

# Test Day 16
python -m pytest backend/tests/test_multi_outlet.py -v

# Lint & typecheck
cd backend
python -m ruff check app tests
python -m mypy app

# Endpoint outlets + consolidated (server lokal jalan dulu)
uvicorn app.main:app --reload
# lalu:
#   GET http://localhost:8000/api/v1/outlets
#   GET http://localhost:8000/api/v1/reports/consolidated
#   GET http://localhost:8000/api/v1/reports/consolidated?outlet_id=1&days=30

# Frontend test OutletSwitcher
cd ../frontend
pnpm test OutletSwitcher

# Riwayat PR #17
gh pr view 17
git show 19e8fb2f --stat
```

---

*Laporan ini mengikuti format laporan harian proyek LEUIT (Bahasa Indonesia).*
