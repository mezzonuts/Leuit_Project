# Laporan Implementasi — Day 20: Customer Facing

**Proyek:** LEUIT (Local-First F&B Demand & Inventory Forecasting)
**Tanggal:** 2026-10-02
**PR:** #21 — `feat(day20): customer facing features`
**Status:** ✅ Merged ke `staging` (squash, commit `b510a44e`, branch `feat/day20-customer` dihapus)

---

## 1. Executive Summary

Day 20 menambahkan lapisan customer-facing: menu public yang aman untuk ditampilkan ke pelanggan + komponen UI QR code, struk digital, dan tampilan menu. Backend: router baru `backend/app/api/v1/public_menu.py` (prefix `/public`, tags Public) dengan endpoint `GET /public/menu` — query `MenuItem.is_active` saja, serialize **field aman saja** (`id`, `name`, `sale_price`, `ingredient_count`, `is_active`): tanpa cost, tanpa recipe/`pos_item_id`. **Keputusan guard:** endpoint public sengaja TANPA `verify_license` (read-only, field whitelist) — beda dari endpoint internal; dicatat eksplisit di sini. Router di-register di `backend/app/api/v1/__init__.py` (`api_router.include_router(public_menu.router)`). Frontend: `frontend/src/utils/qrcode.ts` — `generateMenuQRUrl(menuUrl)` (QR via `api.qrserver.com`, ter-encode) + `getMenuUrlForOutlet(outletId, baseUrl)` (`/menu` atau `/menu?outlet=<id>`); `MenuQRPage.tsx` — kartu QR (img dari `generateMenuQRUrl`), input URL readonly + tombol Salin (clipboard + feedback Check 2s), tombol Cetak (`window.print()`), outlet dari `useOutletStore`; `PublicMenuPage.tsx` — list menu via react-query `GET /public/menu`, nama + `ingredient_count` + harga `formatRupiah`, empty state "Menu belum tersedia"; `ReceiptView.tsx` — struk monospace (brand LEUIT, no. transaksi, tanggal `id-ID`, line items, total `formatRupiah`), tombol Cetak + Share (clipboard teks struk). Deliverable aktual: 17 test baru (2 backend + 15 frontend), 10 file berubah +455/−1 baris, quality gates hijau (ruff 0, pytest 300 pass, typecheck 0, pnpm test 255 pass / 8 skipped, CI green).

---

## 2. Files Changed

| File | Perubahan |
|------|-----------|
| `backend/app/api/v1/public_menu.py` | Baru — 34 baris: router `/public`, `GET /menu` → `{items, total}`; item = `id`, `name`, `sale_price` (float), `ingredient_count` (jumlah `RecipeItem`), `is_active`; filter `MenuItem.is_active`; tanpa guard `verify_license` (keputusan eksplisit public-read) |
| `backend/app/api/v1/__init__.py` | Tambah import `public_menu` + `include_router(public_menu.router)` |
| `backend/tests/test_public_menu.py` | Baru — 2 test (lihat bagian 3) |
| `frontend/src/utils/qrcode.ts` | Baru — 14 baris: `generateMenuQRUrl` (URL QR `api.qrserver.com` size 300x300, data ter-`encodeURIComponent`) + `getMenuUrlForOutlet` (`outletId ? base+'/menu?outlet='+id : base+'/menu'`, fallback `window.location.origin`) |
| `frontend/src/components/customer/MenuQRPage.tsx` | Baru — 68 baris: kartu QR + URL readonly + Salin + Cetak; `useOutletStore().current_outlet_id` |
| `frontend/src/components/customer/PublicMenuPage.tsx` | Baru — 46 baris: react-query `['public-menu']` → `GET /public/menu`; render nama/bahan/harga; empty state |
| `frontend/src/components/customer/ReceiptView.tsx` | Baru — 92 baris: react-query `['receipt', transactionId]` → `GET /sales/{id}/receipt`; struk monospace LEUIT; tombol Cetak + Share |
| `frontend/src/components/customer/__tests__/MenuQRPage.test.tsx` | Baru — 5 test |
| `frontend/src/components/customer/__tests__/PublicMenuPage.test.tsx` | Baru — 4 test |
| `frontend/src/components/customer/__tests__/ReceiptView.test.tsx` | Baru — 6 test |

**Statistik:** 10 file, +455 / −1 baris.

---

## 3. Test Coverage

**Total: 17 test baru** — 2 backend + 15 frontend. Semua lulus.

### Backend — `backend/tests/test_public_menu.py` (2 test)

| Kelas Test | Cakupan |
|------------|---------|
| `TestPublicMenu.test_public_menu_endpoint_registered` | Router prefix `/public`, route path mengandung `/menu` |
| `TestPublicMenu.test_public_menu_returns_structure` | `get_public_menu(db=MagicMock)` kosong → `{"items": [], "total": 0}`; `items` list |

### Frontend (15 test)

| File | Test |
|------|------|
| `MenuQRPage.test.tsx` (5) | render title "QR Code Menu"; QR img (`alt`); URL input (`aria-label` "URL menu"); copy button ("Salin link"); print button ("Cetak QR") |
| `PublicMenuPage.test.tsx` (4) | title "Menu Kami"; menu items (Kopi Susu, Teh Manis); harga "Rp 25.000"; loading state "Memuat menu" |
| `ReceiptView.test.tsx` (6) | loading "Memuat struk"; content "LEUIT"; item "Kopi Susu"; "Total"; print "Cetak"; share "Share" |

**Total suite: pytest 300 pass · pnpm test 255 pass, 8 skipped**

---

## 4. Quality Gates

| Gate | Tool | Hasil |
|------|------|-------|
| Backend lint | `uv run ruff check .` | ✅ 0 errors |
| Backend test | `uv run pytest` | ✅ 300 pass |
| Frontend typecheck | `pnpm typecheck` | ✅ 0 errors |
| Frontend test | `pnpm test` | ✅ 255 pass, 8 skipped |
| CI | GitHub Actions | ✅ Green |

---

## 5. Architecture Compliance

| Aspek | Implementasi |
|------|----------------|
| **API pattern** | Router baru prefix `/public` terpisah dari `/bom`/`/sales` (endpoint public memang beda domain); response dict polos (bukan Pydantic) — mengikuti pola ringan endpoint lain |
| **Local-first** | Menu + struk dirender dari data lokal SQLite; QR link dibangun dari `window.location.origin` — tidak perlu backend eksternal |
| **Frontend pattern** | react-query + `api.get` polos (tanpa section baru di `services/api.ts`); `formatRupiah` dari `formatters.ts` (satu-satunya sumber); outlet dari `useOutletStore` (Day 16) |
| **Security** | Public menu whitelist field — `MenuItem.to_dict()` mentah TIDAK dipakai; tidak ada cost/recipe/`pos_item_id` di response; endpoint public tanpa `verify_license` (keputusan eksplisit: read-only + field aman; konsisten dengan akses pelanggan) |
| **YAGNI** | Belum ada Pydantic schema (`MenuPublicResponse`/`ReceiptResponse`), belum ada endpoint `/sales/{id}/receipt` di backend (ReceiptView siap konsumsi tapi backend receipt belum ada), belum ada PDF engine, belum ada category/gambar/promo menu, belum ada kategori per-outlet |
| **Known gap** | (1) **Endpoint receipt backend belum ada** — `ReceiptView` memanggil `GET /api/v1/sales/{transactionId}/receipt` tapi tidak ada handler di backend (plan Day 20 bagian 2 belum ter-implement). (2) QR memakai layanan eksternal `api.qrserver.com` — butuh internet saat render; plan alternatif (library lokal `qrcode`/`qrcode.react` di lockfile) tidak dipakai. (3) `MenuQRPage` hanya menampilkan QR + URL — belum ada grid menu + filter nama + "Generate QR per item" seperti rencana. (4) `PublicMenuPage`/`MenuQRPage`/`ReceiptView` belum di-mount ke router/App (tidak ada route/nav entry; komponen + test siap pakai). (5) `public_menu.py` menghitung `ingredient_count` dengan N+1 query (loop `db.query(RecipeItem)` per item) — acceptable untuk skala kecil, belum dioptimasi. (6) Response `{items, total}` tanpa `outlet_name`/`generated_at` seperti rencana dict response. (7) `qrcode.ts` memakai `api.qrserver.com` — QR data menu URL publik terkirim ke layanan pihak ketiga (catatan privasi). (8) Tidak ada test untuk `qrcode.ts` util (plan minta test util QR) — semua 15 frontend test fokus komponen. (9) `ReceiptView` share hanya menyalin ringkasan teks (no + total), bukan salinan penuh line items. |

---

## 6. CI Iterations

**Jumlah iterasi: 1** (quality gates hijau sebelum PR dibuat).

---

## 7. Commands to Resume

```bash
cd D:\Project\Leuit
git checkout staging && git pull origin staging

# Test Day 20
uv run pytest backend/tests/test_public_menu.py -v
cd frontend
pnpm test customer
pnpm typecheck && pnpm lint

# Endpoint public menu (server lokal jalan dulu)
cd ../backend
uvicorn app.main:app --reload
#   GET http://localhost:8000/api/v1/public/menu     # public, tanpa auth

# Smoke frontend (setelah route di-mount)
cd ../frontend
pnpm dev

# Riwayat PR #21
gh pr view 21
git show b510a44e --stat
```

---

*Laporan ini mengikuti format laporan harian proyek LEUIT (Bahasa Indonesia).*
