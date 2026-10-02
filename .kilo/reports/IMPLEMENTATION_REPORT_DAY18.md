# Laporan Implementasi — Day 18: Advanced Analytics

**Proyek:** LEUIT (Local-First F&B Demand & Inventory Forecasting)
**Tanggal:** 2026-10-02
**PR:** #19 — `feat(day18): advanced analytics`
**Status:** ✅ Merged ke `staging` (squash, commit `adb47ef2`, branch `feat/day18-analytics` dihapus)

---

## 1. Executive Summary

Day 18 menambahkan lapisan analytics lanjutan ke LEUIT. `backend/app/services/report_scheduler.py` (226 baris) berisi `generate_drill_down_report(db, metric, start_date, end_date, granularity, ingredient_id)` dengan tiga metrik: **sales** (bucket `SalesTransaction` per hari/minggu/bulan → `transaction_count`, `total_quantity`, `unique_items`), **usage** (`IngredientDailyUsage` → `total_used`, `record_count`, filter opsional `ingredient_id`), dan **valuation** (per ingredient `current_stock * cost_per_unit`, sorted descending). `schedule_report()` mengembalikan konfigurasi jadwal (`daily`/`weekly`/`monthly` + `report_type` sales/usage/valuation/consolidated + format csv/json/pdf + email opsional) dengan `next_run` dihitung `_calculate_next_run` (jam 06:00 UTC; weekly Senin; monthly tanggal 1 berikutnya). Endpoint baru di `backend/app/api/v1/analytics.py`: `GET /api/v1/analytics/drill-down` (query `metric` regex `^(sales|usage|valuation)$`, `days` 1–365, `granularity` `^(daily|weekly|monthly)$`, `ingredient_id` opsional) dan `POST /api/v1/analytics/schedule` (validasi `pattern` ketat per field) — keduanya di-guard `verify_license`, router terdaftar di `api/v1/__init__.py` prefix `/analytics`. Di frontend: `DateRangePicker.tsx` (preset 7/30/90/365 hari via dropdown + input tanggal custom, aria-label Indonesia) dan `DrillDownChart.tsx` (recharts BarChart, select metrik Penjualan/Penggunaan, granularitas Harian/Mingguan/Bulanan, DateRangePicker, loading spinner, react-query key per kombinasi filter). Deliverable: 21 test baru (11 backend + 10 frontend), 8 file berubah +709/−1 baris, quality gates hijau (ruff 0, pytest 296 pass, typecheck 0, pnpm test 236 pass / 8 skipped, CI green).

---

## 2. Files Changed

| File | Perubahan |
|------|-----------|
| `backend/app/services/report_scheduler.py` | Baru — 226 baris: `generate_drill_down_report` + helper sales/usage/valuation, `schedule_report`, `_calculate_next_run` |
| `backend/app/api/v1/analytics.py` | Baru — router `prefix="/analytics"`: `GET /analytics/drill-down`, `POST /analytics/schedule` |
| `backend/app/api/v1/__init__.py` | Tambah import `analytics` + `api_router.include_router(analytics.router)` |
| `backend/tests/test_analytics.py` | Baru — 11 test (lihat bagian 3) |
| `frontend/src/components/ui/DateRangePicker.tsx` | Baru — 78 baris: preset dropdown + custom start/end, controlled props |
| `frontend/src/components/ui/__tests__/DateRangePicker.test.tsx` | Baru — 5 test |
| `frontend/src/components/dashboard/DrillDownChart.tsx` | Baru — 102 baris: filter metrik/granularitas/date-range + BarChart |
| `frontend/src/components/dashboard/__tests__/DrillDownChart.test.tsx` | Baru — 5 test |

**Statistik:** 8 file, +709 / −1 baris.

---

## 3. Test Coverage

**Total: 21 test baru** — 11 backend + 10 frontend. Semua lulus.

### Backend — `backend/tests/test_analytics.py` (11 test)

| Kelas Test | Jumlah | Cakupan |
|------------|--------|---------|
| `TestGenerateDrillDownReport` | 4 | sales drill-down struktur (`metric`, `granularity`, `data` list, `total_transactions`); usage (`total_used`); valuation (`total_valuation`); metric invalid → `ValueError` "Unknown metric" |
| `TestScheduleReport` | 3 | daily (status `scheduled`, `next_run` ada); weekly; monthly (`format=json`) |
| `TestCalculateNextRun` | 3 | daily/weekly/monthly semua menghasilkan tanggal ISO di masa depan |
| `TestAnalyticsAPI` | 1 | router `prefix="/analytics"` terdaftar + routes > 0 |

### Frontend (10 test)

| File | Test | Cakupan |
|------|------|---------|
| `DateRangePicker.test.tsx` | 5 | render input tanggal (mulai/selesai); nilai prop dirender; dropdown preset terbuka (7/30 Hari); preset memanggil `onChange`; perubahan input memanggil `onChange` dengan tanggal baru |
| `DrillDownChart.test.tsx` | 5 | judul "Drill-Down Analytics"; select Metrik; select Granularitas; DateRangePicker dirender (mock); chart muncul setelah data loaded (recharts + api di-mock) |

**Total suite: pytest 296 pass · pnpm test 236 pass, 8 skipped**

---

## 4. Quality Gates

| Gate | Tool | Hasil |
|------|------|-------|
| Backend lint | `uv run ruff check .` | ✅ 0 errors |
| Backend test | `uv run pytest` | ✅ 296 pass |
| Frontend typecheck | `pnpm typecheck` | ✅ 0 errors |
| Frontend test | `pnpm test` | ✅ 236 pass, 8 skipped |
| CI | GitHub Actions | ✅ Green |

---

## 5. Architecture Compliance

Sesuai Backend Architecture v1.0, Frontend Architecture v1.8, dan PRD v1.8:

| Aspek | Implementasi |
|------|----------------|
| **API pattern** | Prefix `/api/v1/analytics`, guard `verify_license`, validasi `Query(pattern=...)` ketat, response dict berisi `metric`, `data`, `generated_at` — konsisten dengan pattern Day 16 |
| **Local-first** | Semua agregasi di SQLite lokal via SQLAlchemy; schedule bersifat konfigurasi in-process |
| **Reuse** | Bucketing mengikuti pola laporan konsolidasi Day 16; model `SalesTransaction`/`IngredientDailyUsage`/`Ingredient` dipakai ulang tanpa skema baru |
| **Frontend pattern** | Komponen presentasi + react-query + controlled state; aria-label Indonesia; mock recharts/api di test mengikuti konvensi test eksisting |
| **YAGNI** | Belum pakai Celery/APScheduler; belum ada persistence schedule ke DB; belum ada email SMTP/eksekusi job; belum ada DashboardBuilder drag-drop |
| **Known gap** | (1) `schedule_report` hanya mengembalikan dict konfigurasi — tidak ada tabel `report_schedules` dan tidak ada worker yang mengeksekusi; restart membatalkan jadwal secara efektif. (2) Rencana plan minta `GET/POST /api/v1/exports/schedule`; aktual hanya `POST /analytics/schedule` — belum ada endpoint list schedule. (3) Backend `/analytics/drill-down` hanya menerima `days`; frontend mengirim `start_date`/`end_date` juga (diabaikan backend; `days` state dihitung ulang dari picker). (4) `DrillDownChart`/`DateRangePicker` belum di-mount ke halaman mana pun (Dashboard/reports) dan `frontend/src/services/api.ts` belum punya section `analytics` — komponen siap pakai tapi belum terintegrasi routing. (5) `valuation` drill-down ada di backend; select metrik frontend baru sales/usage. (6) Tidak ada `DashboardBuilder.tsx`/`ReportScheduler.tsx` UI — scope custom dashboards di-scope-out |

---

## 6. CI Iterations

**Jumlah iterasi: 1** (quality gates hijau sebelum PR dibuat).

---

## 7. Commands to Resume

```bash
cd D:\Project\Leuit
git checkout staging && git pull origin staging

# Test Day 18
python -m pytest backend/tests/test_analytics.py -v
cd frontend
pnpm test DateRangePicker DrillDownChart
pnpm typecheck && pnpm lint

# Endpoint analytics (server lokal jalan dulu)
cd ../backend
uvicorn app.main:app --reload
#   GET  http://localhost:8000/api/v1/analytics/drill-down?metric=sales&days=30&granularity=daily
#   GET  http://localhost:8000/api/v1/analytics/drill-down?metric=usage&granularity=weekly&ingredient_id=1
#   GET  http://localhost:8000/api/v1/analytics/drill-down?metric=valuation
#   POST http://localhost:8000/api/v1/analytics/schedule?name=Daily&schedule_type=daily&report_type=sales&email=a@b.c&format=csv

# Riwayat PR #19
gh pr view 19
git show adb47ef2 --stat
```

---

*Laporan ini mengikuti format laporan harian proyek LEUIT (Bahasa Indonesia).*
