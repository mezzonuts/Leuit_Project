Berikut adalah draf pembaruan **Frontend Architecture & Implementation Blueprint (v1.8)** yang telah diselaraskan dengan pembaruan PRD terbaru:
1. **Sistem Autentikasi Kunci Ganda (*Owner Passkey & Developer Unlock Screen*)** untuk database terenkripsi.
2. **Modul Rekonsiliasi & Sinkronisasi CSV Kasir Berkala** (antarmuka upload berkala dengan laporan deduplikasi data).
3. **Pemisahan Tegas Dashboard vs Data Entry CRUD** (menggunakan pola *Slide-Over Drawer*).
4. **Seluruh Fitur Visual:** Grafik Recharts 30 hari, pemindai barcode kamera, valuasi aset, *pulse icon*, *progress bar*, dan *Recipe Scaler*.

---

# Frontend Architecture Blueprint: LEUIT Desktop App (v1.8)

| Dokumen | Rincian |
| :--- | :--- |
| **Aplikasi** | **LEUIT** (Local-First F&B Demand & Inventory Forecasting) |
| **Arsitektur Frontend** | Single Page Application (SPA) - Client-Side Rendering |
| **Target Build** | Static Export (`dist/`) yang di-*mount* langsung oleh backend FastAPI |
| **Security Layer** | **Owner PIN / Passkey Prompt** (Membuka database SQLite terenkripsi) |
| **Versi Dokumen** | v1.8 (Encrypted Ledger & Continuous CRUD Edition) |

---

## 1. Peta Navigasi & Pemisahan UI/UX

Aplikasi menggunakan layout **Sidebar Tetap di Kiri** dengan pemisahan tegas antara area monitoring (*Read*) dan area manajemen (*Write/CRUD*):

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           NAVIGASI UTAMA (SIDEBAR)                              │
├───────────────────┬─────────────────────────────────────────────────────────────┤
│ 1. DASHBOARD      │ [READ-ONLY] Metrik Valuasi Aset, Grafik Konsumsi 30 Hari,   │
│    (Pusat Pantau) │ Bahan Kritis (< Threshold / Basi < 3 Hari), Alert Tempo     │
├───────────────────┼─────────────────────────────────────────────────────────────┤
│ 2. KELOLA STOK    │ [CRUD DATA] Master Bahan, Barcode Kamera, Stock Opname,     │
│    (Inventaris)   │ Pengaturan Threshold Minimum (Via Slide-over Drawer)        │
├───────────────────┼─────────────────────────────────────────────────────────────┤
│ 3. RESEP & MENU   │ [CRUD & TOOL] Pemetaan BOM Resep + Recipe Scaler Porsi      │
├───────────────────┼─────────────────────────────────────────────────────────────┤
│ 4. PEMBELIAN      │ [TRANSAKSI] Catat Belanja Cash vs Tempo + Alert Hutang      │
├───────────────────┼─────────────────────────────────────────────────────────────┤
│ 5. SINKRONISASI   │ [REKONSILIASI] Upload CSV Kasir Berkala + Log Deduplikasi   │
└───────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 2. Struktur Direktori Proyek Terbaru (`/src`)

```text
src/
├── assets/                  # Logo LEUIT, icon, sound beep
├── components/
│   ├── auth/                # MODUL KEAMANAN DATABASE TERENKRIPSI
│   │   ├── DatabaseUnlockModal.tsx  # Input PIN Owner / Developer Key
│   │   └── KeyStatusIndicator.tsx   # Status gembok database aktif
│   ├── layout/
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   └── LicenseGraceBanner.tsx   # Banner kuning jika tagihan habis
│   ├── dashboard/           # AREA MONITORING MURNI (READ-ONLY)
│   │   ├── ValuationMetricCard.tsx  # Total aset + Tombol Ekspor CSV
│   │   ├── UsageTrendBarChart.tsx   # Grafik Recharts 30 hari + filter
│   │   ├── CriticalAlertsSection.tsx# Ikon jam berdenyut (< 3 hari expired)
│   │   └── StockHealthTable.tsx     # Tabel ringkas + progress bar rasio
│   ├── inventory/           # MODUL CRUD BAHAN (SLIDE-OVER DRAWER)
│   │   ├── IngredientTable.tsx      # Tabel master + tombol aksi Edit/Hapus
│   │   ├── IngredientDrawer.tsx     # Form Tambah/Edit (Slide-over kanan)
│   │   ├── StockOpnameModal.tsx     # Form cepat penyesuaian stok fisik
│   │   └── BarcodeCameraModal.tsx   # Pemindai barcode via kamera (html5-qrcode)
│   ├── bom/                 # MODUL RESEP & SCALER
│   │   ├── RecipeList.tsx           # Daftar menu dan komposisi bahan
│   │   ├── RecipeDrawer.tsx         # Form buat/edit gramasi resep
│   │   └── RecipeScalerTool.tsx     # Simulasi kebutuhan bahan target porsi
│   ├── purchases/           # MODUL PEMBELIAN CASH VS TEMPO
│   │   ├── PurchaseEntryDrawer.tsx  # Form faktur belanja baru
│   │   ├── RestockSheetView.tsx     # Rekomendasi belanja mingguan
│   │   └── AccountsPayableAlert.tsx # Peringatan jatuh tempo vendor
│   └── sync/                # MODUL REKONSILIASI CSV KASIR BERKALA
│       ├── PosSyncDrawer.tsx        # Drag-and-drop CSV + progress upload
│       ├── SyncResultSummary.tsx    # Card hasil: [X] Baru, [Y] Terduplikasi
│       └── SyncHistoryTable.tsx     # Riwayat riil upload sebelumnya
├── hooks/
│   ├── useDatabaseAuth.ts   # Cek apakah database terenkripsi sudah terbuka
│   ├── useInventory.ts      # Query & Mutation bahan baku (TanStack Query)
│   ├── usePosSync.ts        # Mutasi upload CSV rekonsiliasi
│   └── useCameraScanner.ts  # Controller akses kamera fisik
├── services/
│   ├── api.ts               # Axios instance (mengirim header auth/passkey)
│   ├── inventoryService.ts
│   ├── syncService.ts
│   └── exportService.ts     # Helper ekspor CSV valuasi
├── stores/
│   ├── useSecurityStore.ts  # State gembok database (isUnlocked: boolean)
│   └── useUIStore.ts        # State aktif Drawer & Modal
├── types/
│   └── index.ts             # TypeScript interfaces
├── utils/
│   ├── formatters.ts        # Format Rupiah & satuan
│   └── exportCsv.ts
├── App.tsx
└── main.tsx
```

---

## 3. Core TypeScript Interfaces (`src/types/index.ts`)

```typescript
// 1. Status Enkripsi Database
export interface DatabaseSecurityState {
  is_locked: boolean;
  role: 'OWNER' | 'DEVELOPER' | 'UNAUTHENTICATED';
  last_unlocked_at?: string;
}

// 2. Master Bahan Baku
export interface Ingredient {
  id: number;
  barcode_sku: string | null;
  name: string;
  unit: 'ml' | 'gram' | 'pcs';
  cost_per_unit: number;         // HPP
  shelf_life_days: number;       // Masa kedaluwarsa (hari)
  current_stock: number;
  min_stock_threshold: number;   // Batas aman
  is_active: boolean;            // Soft delete indicator
}

// 3. Rekonsiliasi & Log Sinkronisasi POS
export interface PosSyncResult {
  sync_id: number;
  file_name: string;
  uploaded_at: string;
  total_rows_read: number;
  new_rows_inserted: number;     // Transaksi baru masuk
  duplicate_rows_skipped: number;// Dilewati agar tidak dobel omzet
  date_range_start: string;
  date_range_end: string;
  reconciled_stock_items: number;// Jumlah bahan mentah yang otomatis berkurang
}

// 4. Pembelian Stok (Cash vs Tempo)
export interface InventoryPurchase {
  id: number;
  purchase_date: string;
  ingredient_id: number;
  ingredient_name: string;
  supplier_id: number;
  supplier_name: string;
  quantity: number;
  total_cost: number;
  payment_method: 'CASH' | 'CREDIT';
  payment_status: 'PAID' | 'UNPAID';
  due_date?: string;             // Tanggal jatuh tempo tempo
}
```

---

## 4. Alur & Spesifikasi Komponen Kritis

### A. Layar Pembuka: Gembok Database (`DatabaseUnlockModal.tsx`)
* Saat aplikasi pertama kali dibuka (atau dipanggil setelah *idle*), periksa `useSecurityStore.is_locked`.
* Jika `is_locked === true`:
  * Tampilkan modal terisolasi (tidak bisa di-*close* sebelum memasukkan kunci).
  * Input 1: **Owner Passkey / PIN** (untuk pemilik resto).
  * Opsi Tautan Kecil: *"Gunakan Developer Recovery Key"* (khusus audit teknis pengembang).
  * Setelah PIN benar, kunci dikirim ke FastAPI untuk mendekripsi `leuit_store.enc` via SQLCipher. Aplikasi terbuka normal.

### B. Modul Rekonsiliasi CSV Berkala (`PosSyncDrawer.tsx`)
* Dibuka dari menu navigasi "Sinkronisasi" atau tombol aksi cepat di header.
* **Area Drag & Drop:** Menerima berkas `.csv` ekspor kasir Moka / Majoo.
* **Status Saat Memproses:** Menampilkan bar animasi *loading* ("Sedang memindai hash duplikasi & menghitung pengurangan stok...").
* **Komponen Hasil Rekonsiliasi (`SyncResultSummary.tsx`):**
  * Kartu Hijau: `+ 152 Transaksi Baru Ditambahkan`
  * Kartu Abu-abu: `340 Transaksi Lama Dilewati (Otomatis Dideduplikasi)`
  * Kartu Biru: `14 Bahan Mentah Berhasil Disesuaikan Stoknya`
  * Data tabel di Dashboard otomatis ter-*refresh* secara instan.

### C. Dashboard Monitoring (`src/components/dashboard/`)
* **Strict Rule:** Bersih dari tombol form tambah data panjang.
* **Metrik Valuasi:** Menghitung total nilai moneter seluruh bahan + Tombol unduh laporan `.csv`.
* **Recharts 30 Hari:** Menampilkan *bar chart* tren konsumsi bahan harian dengan dropdown filter pemilihan bahan.
* **Indikator Visual:**
  * Ikon jam berdenyut (`animate-pulse`) jika `shelf_life_days < 3`.
  * Progress bar rasio stok terhadap threshold minimum (Merah jika $< 100\%$, Kuning $100-150\%$, Hijau $> 150\%$).

### D. CRUD Master & Slide-over Drawer (`IngredientDrawer.tsx`)
* Form penambahan/edit data berada di **Panel Samping Kanan (Slide-over)** selebar `450px`, bukan modal tengah.
* Tombol kamera di samping input Barcode membuka modal kamera (`html5-qrcode`). Saat kode terdeteksi, berbunyi *beep* dan teks barcode langsung terisi ke input form.
* Menggunakan React Hook Form dengan tombol simpan yang memicu invalidasi cache React Query.

### E. Recipe Scaler (`RecipeScalerTool.tsx` di Tab BOM)
* Input: Dropdown Menu POS + Input Angka Target Porsi (misal: 100 cup).
* Sistem mengalikan komposisi resep dengan porsi dan membandingkannya langsung dengan sisa stok aktual di SQLite.
* Menampilkan badge: **CUKUP** (stok aman) atau **KURANG [X] Satuan** (stok tidak mencukupi).

---

## 5. Rencana Prompt Bertahap untuk Coding Agent

Agent harus mengeksekusi instruksi dalam 6 tahapan berikut:

1. **Sprint 1 (Pondasi & Security Gembok):**
   * Setup Vite React TS + Tailwind CSS.
   * Buat `DatabaseUnlockModal.tsx` dan integrasikan dengan endpoint login/passkey backend.
   * Setup layout Sidebar dan navigasi halaman.

2. **Sprint 2 (Data Entry CRUD & Slide-Over Drawer):**
   * Bangun antarmuka tabel master bahan (`IngredientTable.tsx`).
   * Buat `IngredientDrawer.tsx` untuk input/edit data rapi di sisi kanan.
   * Integrasikan modul pemindai barcode kamera via `html5-qrcode`.

3. **Sprint 3 (Dashboard Monitoring & Recharts):**
   * Terapkan kartu Valuasi Aset Gudang & utilitas Ekspor CSV.
   * Implementasikan grafik batang tren konsumsi 30 hari menggunakan Recharts.
   * Tambahkan progress bar threshold dan animasi jam berdenyut (*pulse*) pada bahan yang mendekati kedaluwarsa.

4. **Sprint 4 (Rekonsiliasi CSV Kasir Berkala):**
   * Buat antarmuka `PosSyncDrawer.tsx` untuk upload CSV.
   * Tampilkan kartu ringkasan rekonsiliasi (*new inserted* vs *duplicates skipped*).
   * Tampilkan tabel riwayat riil sinkronisasi kasir.

5. **Sprint 5 (Resep BOM, Scaler, & Pembelian):**
   * Bangun form pembuatan resep menu kasir.
   * Implementasikan fitur **Recipe Scaler** simulasi porsi.
   * Buat modul transaksi belanja: Cash vs Kredit/Tempo lengkap dengan pengingat tanggal jatuh tempo suplier.

6. **Sprint 6 (Testing & Polishing):**
   * Pastikan dashboard bersih tanpa form input panjang.
   * Uji alur pembukaan database terenkripsi (Owner PIN).
   * Uji fungsionalitas offline 100%.