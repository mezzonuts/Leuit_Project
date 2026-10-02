# Laporan Implementasi — Day 19: Supplier Management

**Proyek:** LEUIT (Local-First F&B Demand & Inventory Forecasting)
**Tanggal:** 2026-10-02
**PR:** #20 — `feat(day19): supplier management`
**Status:** ✅ Merged ke `staging` (squash, commit `8befec2f`, branch `feat/day19-supplier` dihapus)

---

## 1. Executive Summary

Day 19 menambahkan lapisan manajemen supplier di atas baseline CRUD yang sudah ada. Endpoint baru `GET /api/v1/purchases/suppliers/{supplier_id}/stats` (`backend/app/api/v1/purchases.py`) mengagregasi `InventoryPurchase` per supplier dalam rentang `days` (default 30, batas 1–365) → `total_purchases`, `unpaid_total` (hanya `PaymentStatus.UNPAID`), `avg_order_value` (`total / purchase_count` atau 0), `purchase_count`, `period_days`; 404 bila supplier tidak ada; guard `verify_license`; response via skema Pydantic baru `SupplierStatsResponse` di `purchase_schema.py`. Frontend: `frontend/src/utils/whatsapp.ts` berisi `createWhatsAppReminderLink(phone, supplierName, totalUnpaid, daysUntilDue)` — normalisasi nomor (strip non-digit, buang leading `0`, prefix `62` bila belum), pesan Bahasa Indonesia ter-encode (`encodeURIComponent`) dengan baris "Jatuh tempo: N hari lagi" hanya bila `daysUntilDue !== null` → `https://wa.me/<digits>?text=...`; plus helper `formatRupiah`. `AccountsPayableAlert.tsx` mendapat kolom Aksi dengan tombol `WhatsApp` (`target="_blank"`, `rel="noopener noreferrer"`) yang tampil bila `alert.phone_whatsapp` ada. `SupplierDrawer.tsx` (98 baris) — slide-over create/edit: `name` (required, submit disabled bila kosong), `phone_whatsapp`, `payment_terms_days` (number, `0 = Cash`); memakai `useMutation` + `queryClient.invalidateQueries({ queryKey: ['suppliers'] })`. Deliverable aktual: 6 test baru (2 backend + 4 frontend), 7 file berubah +252/−2 baris, quality gates hijau (ruff 0, pytest 298 pass, typecheck 0, pnpm test 240 pass / 8 skipped, CI green).

---

## 2. Files Changed

| File | Perubahan |
|------|-----------|
| `backend/app/api/v1/purchases.py` | Tambah import `SupplierStatsResponse` + endpoint `GET /suppliers/{supplier_id}/stats` (~40 baris): 404 guard, agregasi `InventoryPurchase` window `days`, response `SupplierStatsResponse` |
| `backend/app/schemas/purchase_schema.py` | Tambah `SupplierStatsResponse` (7 field: `supplier_id`, `supplier_name`, `total_purchases`, `unpaid_total`, `avg_order_value`, `purchase_count`, `period_days`) |
| `backend/tests/test_supplier_management.py` | Baru — 2 test (lihat bagian 3) |
| `frontend/src/components/purchases/SupplierDrawer.tsx` | Baru — 98 baris: slide-over create/edit supplier, `useMutation`, invalidate `['suppliers']` |
| `frontend/src/utils/whatsapp.ts` | Baru — 31 baris: `createWhatsAppReminderLink` (normalisasi + pesan ter-encode) + `formatRupiah` |
| `frontend/src/utils/__tests__/whatsapp.test.ts` | Baru — 4 test |
| `frontend/src/components/purchases/AccountsPayableAlert.tsx` | Tambah import `MessageCircle` + `createWhatsAppReminderLink`; kolom Aksi tombol WhatsApp per alert bila `phone_whatsapp` ada |

**Statistik:** 7 file, +252 / −2 baris.

---

## 3. Test Coverage

**Total: 6 test baru** — 2 backend + 4 frontend. Semua lulus.

### Backend — `backend/tests/test_supplier_management.py` (2 test)

| Kelas Test | Cakupan |
|------------|---------|
| `TestSupplierStats.test_supplier_stats_response_schema` | Instansiasi `SupplierStatsResponse` valid; field `supplier_name`, `purchase_count`, `total_purchases` terisi sesuai input |
| `TestSupplierStats.test_supplier_stats_endpoint_registered` | Router purchases memiliki route path mengandung `/suppliers/{supplier_id}/stats` |

### Frontend — `whatsapp.test.ts` (4 test)

| Test | Cakupan |
|------|---------|
| creates wa.me link with formatted message | `08123456789` → `https://wa.me/628123456789` + `text=` |
| handles phone with country code | `628123456789` tidak di-prefix ganda |
| omits due date when null | pesan decode tidak mengandung "Jatuh tempo" |
| includes due date when present | pesan decode mengandung "Jatuh tempo: 5 hari lagi" |

**Total suite: pytest 298 pass · pnpm test 240 pass, 8 skipped**

---

## 4. Quality Gates

| Gate | Tool | Hasil |
|------|------|-------|
| Backend lint | `uv run ruff check .` | ✅ 0 errors |
| Backend test | `uv run pytest` | ✅ 298 pass |
| Frontend typecheck | `pnpm typecheck` | ✅ 0 errors |
| Frontend test | `pnpm test` | ✅ 240 pass, 8 skipped |
| CI | GitHub Actions | ✅ Green |

---

## 5. Architecture Compliance

| Aspek | Implementasi |
|------|----------------|
| **API pattern** | Endpoint di bawah prefix `/purchases/suppliers/...` (konsisten CRUD eksisting), guard `verify_license`, `Query(30, ge=1, le=365)`, response Pydantic — mengikuti pola Day 16/18 |
| **Local-first** | Agregasi langsung di SQLite lokal via SQLAlchemy; tanpa dependensi baru |
| **Frontend pattern** | Drawer slide-over mengikuti `IngredientDrawer`; react-query invalidate setelah mutasi; tombol WhatsApp deep-link `wa.me` (bukan WhatsApp Business API) |
| **YAGNI** | Belum ada WhatsApp auto-blast/Business API, belum ada endpoint riwayat purchase per supplier, belum ada halaman Suppliers, belum ada tabel baru |
| **Known gap** | (1) `SupplierDrawer.tsx` belum di-mount ke halaman mana pun (Purchases/BOM) dan belum ada `Suppliers.tsx` list — komponen siap pakai tapi belum terintegrasi routing/menu. (2) `frontend/src/services/api.ts` belum punya section `suppliers.stats` — drawer memanggil `api.post/put` polos, stats belum dikonsumsi frontend. (3) Rencana plan minta `GET /suppliers/{id}/purchases` (riwayat) — aktual tidak ada. (4) Tombol WhatsApp di `AccountsPayableAlert` tampil untuk semua alert dengan `phone_whatsapp`, tanpa gate `days_until_due <= 3` seperti rencana plan. (5) Signature util aktual `createWhatsAppReminderLink(phone, supplierName, totalUnpaid, daysUntilDue)` — berbeda dari rencana `buildWaLink(phone, message)` (message di-build di dalam util). (6) Tidak ada test untuk `SupplierDrawer` (submit create/edit) maupun delete-with-purchases 400. (7) `formatRupiah` di `whatsapp.ts` duplikat helper `formatters.ts` |

---

## 6. CI Iterations

**Jumlah iterasi: 1** (quality gates hijau sebelum PR dibuat).

---

## 7. Commands to Resume

```bash
cd D:\Project\Leuit
git checkout staging && git pull origin staging

# Test Day 19
python -m pytest backend/tests/test_supplier_management.py -v
cd frontend
pnpm test whatsapp
pnpm typecheck && pnpm lint

# Endpoint supplier stats (server lokal jalan dulu)
cd ../backend
uvicorn app.main:app --reload
#   GET http://localhost:8000/api/v1/purchases/suppliers/1/stats
#   GET http://localhost:8000/api/v1/purchases/suppliers/1/stats?days=90
#   GET http://localhost:8000/api/v1/purchases/payables   # kolom Aksi WhatsApp

# Riwayat PR #20
gh pr view 20
git show 8befec2f --stat
```

---

*Laporan ini mengikuti format laporan harian proyek LEUIT (Bahasa Indonesia).*
