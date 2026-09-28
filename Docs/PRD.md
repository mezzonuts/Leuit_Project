Berikut adalah pembaruan menyeluruh **Product Requirement Document (PRD) v1.7** untuk **LEUIT**, yang telah mengintegrasikan seluruh 11 poin kebutuhan baru (visualisasi grafik D3/Recharts, pemindai barcode kamera, valuasi aset, *progress bar*, threshold kustom, hingga *Recipe Scaler*):

---

# Product Requirement Document (PRD)

| Metadata | Rincian |
| :--- | :--- |
| **Nama Produk** | **LEUIT** *(Lumbung Digital & Prediksi Stok Kafe)* |
| **Filosofi Nama** | *Leuit* (Sunda): Lumbung padi tradisional masyarakat Jawa Barat yang dirancang tahan cuaca, anti-busuk, dan menjamin ketahanan pangan keluarga. |
| **Bentuk Distribusi** | **Desktop App Portable (`.exe` / `.dmg`) via PyInstaller** |
| **Arsitektur Data** | **Privacy-First / Local-First Database (SQLite) + Python FastAPI** |
| **Frontend UI Stack** | React / Next.js + Tailwind CSS + **Recharts / D3.js** |
| **Target Pasar** | *Independent Coffee Shops* & Restoran di Kota Bandung & Jawa Barat |
| **Versi Dokumen** | v1.7 (Inventory Intelligence & Scanner Edition) |
| **Status** | Approved for Development |

---

## 1. Analisis Komparasi: LEUIT vs Layanan Stok Moka POS

| Parameter Evaluasi | Layanan Stok Moka POS | **LEUIT (Aplikasi Kita)** |
| :--- | :--- | :--- |
| **Sifat Analisis Stok** | **Reaktif:** Mencatat stok keluar-masuk setelah transaksi terjadi. | **Prediktif & Preskriptif:** Memberi tahu kuantitas belanja 7 hari ke depan. |
| **Sensitivitas Cuaca & Turis Bandung** | **Tidak Ada:** Mengabaikan pola lonjakan akhir pekan dan cuaca. | **Hyperlocal Context:** Terintegrasi data hujan BMKG Bandung dan lonjakan turis Jakarta. |
| **Bahan Segar (*Shelf-Life*)** | **Pukul Rata:** Memperlakukan sirup sama dengan susu murni Lembang. | **Shelf-Life Aware:** Menghitung masa basi bahan dan menampilkan peringatan visual. |
| **Kerahasiaan Data (Privasi)** | **Cloud Pihak Ketiga:** Resep rahasia dan omzet tersimpan di server cloud luar. | **100% Privacy-First:** Data kasir dan resep tersimpan di laptop kafe via SQLite. |
| **Sistem Pembelian Bahan** | Katalog vendor pihak ketiga. | **Cash & Tempo (Kredit):** Pencatatan hutang dagang suplier lokal + jatuh tempo. |
| **Interaktivitas Resep & Scan** | Entri teks manual standar. | **Barcode/QR Scanner via Kamera** + **Recipe Scaler** simulasi porsi instan. |

---

## 2. Arsitektur Teknis & Distribusi Desktop Portable

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1. SERVER CLOUD (Hanya Auth & Billing - Zero Data Kafe)                │
│    - Database: PostgreSQL (Menyimpan Akun & Status Langganan Midtrans) │
│    - Service: Verifikasi Lisensi & Feed Publik Cuaca BMKG Bandung      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Sinkronisasi Token Lisensi & Cuaca)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 2. DESKTOP LOCAL ENVIRONMENT (Laptop Kafe Pengguna)                    │
│                                                                        │
│    [Package Single Executable via PyInstaller]                         │
│    - File: `LeuitApp.exe` (Windows) atau `LeuitApp.dmg` (Mac)          │
│    - Eksekusi: Klik ganda langsung menjalankan backend Python lokal    │
│      dan otomatis membuka browser ke `http://localhost:8000`           │
│                                                                        │
│    [Komponen di Dalam Komputer Lokal]                                  │
│    ├── Database: SQLite (`leuit_store.db`)                             │
│    │   └── Data Transaksi, Resep (BOM), Barcode/SKU, Hutang Suplier    │
│    ├── Backend: Python FastAPI (Engine Analitik & Forecasting)         │
│    └── Frontend: Local Web UI (React + Tailwind + Recharts/D3)         │
│        ├── Integrasi Web Camera API (Pemindai Barcode/QR Fisik)        │
│        └── Engine Visualisasi Data Interaktif                          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Spesifikasi Fitur Utama (Enhanced)

### F1: Data Ingestion & POS Parser (Offline)
* Mendukung impor data penjualan riil kasir offline melalui *drag-and-drop* file CSV/Excel dari kasir Moka, Majoo, atau Olsera.

### F2: Master Bahan Baku & Integrasi Barcode / QR Scanner
* **Field Barcode / SKU:** Penambahan kolom `barcode_sku` pada antarmuka master bahan dan modal "Tambah Bahan".
* **Akses Kamera Fisik (Camera Access Trigger):**
  * Tombol ikon kamera di samping input Barcode pada modal "Tambah Bahan" dan modul "Update Stok".
  * Mengaktifkan kamera web/laptop (menggunakan WebRTC & pustaka JS seperti `html5-qrcode` / `BarcodeDetector API`) untuk memindai kode QR atau barcode fisik kemasan (contoh: dus susu Greenfields/Diamond, kemasan sirup, kantong biji kopi).
  * Nilai hasil pemindaian langsung mengisi *field* Barcode/SKU secara otomatis.

### F3: Recipe / Bill of Materials (BOM) & **Recipe Scaler**
* **Mapping Standar:** 1 Porsi *Iced Latte* = 18g Kopi + 120ml Susu Segar + 1 Cup Plastik.
* **Fitur Baru - Recipe Scaler (Simulasi Porsi):**
  * Di tab **BOM**, pengguna dapat memilih menu dan memasukkan target porsi produksi (misal: pesanan katering atau target *event* 100 cup).
  * Sistem secara otomatis menghitung total kebutuhan bahan mentah:
    $$\text{Total Kebutuhan Bahan} = \text{Target Porsi} \times \text{Gramasi Resep per Porsi}$$
  * Menampilkan perbandingan langsung: **Kebutuhan vs Sisa Stok Saat Ini**, lengkap dengan status apakah stok cukup atau harus beli tambahan.

### F4: Dashboard Analytics, Visualisasi, & Valuasi Aset
* **Grafik Tren Penggunaan Bahan 30 Hari (Recharts / D3.js):**
  * Menampilkan grafik batang interaktif (*bar chart*) tren konsumsi harian bahan baku selama 30 hari ke belakang.
  * Dilengkapi *filter dropdown* untuk memilih bahan baku tertentu (misal: khusus melihat tren susu murni vs biji kopi).
* **Valuasi Aset Stok Gudang (*Inventory Valuation*):**
  * Widget metrik di atas Dashboard yang menghitung total nilai uang (*monetary value*) dari seluruh stok bahan mentah dan kemasan yang tersimpan:
    $$\text{Total Valuasi Aset} = \sum (\text{Stok Saat Ini} \times \text{HPP per Satuan})$$
* **Ekspor Laporan Valuasi (.CSV):**
  * Tombol aksi *"Ekspor Laporan Valuasi (.CSV)"* di Dashboard.
  * Menghasilkan berkas CSV berisi: ID Bahan, Nama Bahan, Barcode/SKU, Sisa Stok, Satuan, HPP, Total Valuasi Aset, Masa Simpan (*Shelf-Life*), dan *Minimum Threshold*.
* **Konfigurasi Custom Minimum Stock Threshold Per Bahan:**
  * Bagian pengaturan di Dashboard untuk menentukan batas aman stok (*buffer*) secara personal per masing-masing bahan baku (misal: batas aman susu = 10 Liter, biji kopi = 2 Kg).
* **Indikator Visual Progress Bar Stok:**
  * Di samping setiap item bahan baku pada tabel Dashboard, terdapat *progress bar* visual yang mengukur rasio stok aktual terhadap threshold minimum:
    $$\text{Rasio Stok} = \left( \frac{\text{Stok Saat Ini}}{\text{Minimum Stock Threshold}} \right) \times 100\%$$
  * Kode warna: **Hijau** (> 150%), **Kuning** (100% – 150%), **Merah** (< 100% / Masuk Zona Bahaya).
* **Notifikasi Kadaluwarsa Berdenyut (*Pulse Animation*):**
  * Baris bahan baku dengan sisa masa simpan (*shelf-life*) kurang dari 3 hari akan disorot warna merah muda (*light red highlight*) dengan **ikon jam berdenyut (*pulsing clock icon* menggunakan animasi CSS `animate-pulse`)**.

### F5: Predictive Restock Engine (Khas Bandung)
* Menghitung rekomendasi pembelian 7 hari ke depan dengan mempertimbangkan tren akhir pekan (*tourist surge*), curah hujan sore BMKG Bandung, dan *shelf-life*.

### F6: Modul Pembelian Stok: Cash vs Kredit (Tempo)
* Pencatatan belanja tunai (Cash) yang memotong kas operasional, serta pembelian kredit/tempo (7, 14, 30 hari) ke suplier lokal lengkap dengan dashboard pengingat jatuh tempo (*Accounts Payable Alert*).

### F7: Analisis Matriks Menu (Kasavana & Smith)
* Klasifikasi menu (*Stars, Plowhorses, Puzzles, Dogs*) untuk mengeliminasi menu mati yang membebani modal bahan baku.

---

## 4. Kebijakan Siklus Langganan Habis (*Subscription Policy*)

* **Data Ownership Guarantee:** Saat masa langganan habis, data lokal (`leuit_store.db`) **tidak dihapus dan tidak disandera**.
* **Grace Period (Hari 1–3):** Berjalan normal dengan banner pengingat tagihan.
* **Expired Mode (Hari 4+):**
  * Fitur Prediksi Restock dan sinkronisasi cuaca dinonaktifkan.
  * Fitur Resep, Scan Barcode, Lihat Hutang Tempo, dan **Ekspor Laporan Valuasi CSV** tetap dapat diakses penuh dalam mode *Read-Only*.
* **Keamanan Lisensi:** Validasi tanda tangan digital (*Signed JWT*) secara lokal tanpa bergantung pada koneksi internet, dilengkapi deteksi anti-manipulasi jam komputer lokal.

---

## 5. Desain Skema Database Lokal (SQLite: `leuit_store.db`)

Pembaruan skema database lokal mencakup kolom Barcode/SKU dan Minimum Threshold:

```sql
-- 1. Master Bahan Baku (Diperbarui dengan SKU & Threshold)
CREATE TABLE ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode_sku TEXT UNIQUE,            -- Barcode kemasan fisik / SKU internal
    name TEXT NOT NULL,                 -- misal: "Susu Segar Lembang 1L"
    unit TEXT NOT NULL,                 -- "ml", "gram", "pcs"
    cost_per_unit REAL NOT NULL,        -- HPP per ml/gram/pcs
    shelf_life_days INTEGER NOT NULL,   -- daya tahan bahan (hari)
    current_stock REAL DEFAULT 0,       -- stok fisik saat ini
    min_stock_threshold REAL DEFAULT 0, -- batas aman personal (Threshold)
    lead_time_days INTEGER DEFAULT 1
);

-- 2. Master Suplier & Ketentuan Pembayaran
CREATE TABLE suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone_whatsapp TEXT,
    payment_terms_days INTEGER DEFAULT 0 -- 0 = Cash, 7/14/30 = Tempo
);

-- 3. Transaksi Pembelian Stok (Cash & Tempo)
CREATE TABLE inventory_purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    purchase_date DATE NOT NULL,
    ingredient_id INTEGER REFERENCES ingredients(id),
    supplier_id INTEGER REFERENCES suppliers(id),
    quantity REAL NOT NULL,
    total_cost REAL NOT NULL,
    payment_method TEXT NOT NULL,       -- 'CASH' atau 'CREDIT'
    payment_status TEXT DEFAULT 'PAID', -- 'PAID', 'UNPAID'
    due_date DATE
);

-- 4. Master Menu Kasir
CREATE TABLE menu_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    sale_price REAL NOT NULL
);

-- 5. Resep / Bill of Materials (BOM)
CREATE TABLE recipe_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_item_id INTEGER REFERENCES menu_items(id),
    ingredient_id INTEGER REFERENCES ingredients(id),
    quantity_required REAL NOT NULL
);

-- 6. Riwayat Transaksi Kasir (POS Import)
CREATE TABLE sales_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_item_id INTEGER REFERENCES menu_items(id),
    quantity INTEGER NOT NULL,
    transaction_time DATETIME NOT NULL
);

-- 7. Riwayat Konsumsi Harian (Untuk Grafik Recharts 30 Hari)
CREATE TABLE ingredient_daily_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usage_date DATE NOT NULL,
    ingredient_id INTEGER REFERENCES ingredients(id),
    total_quantity_used REAL NOT NULL
);

-- 8. Status Lisensi Aplikasi
CREATE TABLE app_license (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    license_key TEXT NOT NULL,
    valid_until DATETIME NOT NULL,
    last_verified_at DATETIME NOT NULL,
    grace_period_end DATETIME NOT NULL
);
```

---

## 6. Detail Antarmuka Komponen Baru

### A. Tampilan Tabel Dashboard (Notifikasi Pulse & Progress Bar)
```
+---------------------------------------------------------------------------------------------------------+
| Nama Bahan            | Stok Saat Ini | Min Threshold | Rasio Stok (Progress) | Status Kadaluwarsa      |
+---------------------------------------------------------------------------------------------------------+
| Susu Segar Lembang 1L | 4 Liter       | 10 Liter      | [==--------] 40% (Merah)| ⏰ (Pulse) Basi dlm 2 hr|
| Biji Kopi House Blend | 8 Kg          | 5 Kg          | [==========] 160%(Hijau)| Aman (25 hari)          |
| Sirup Karamel         | 3 Botol       | 2 Botol       | [========--] 150%(Hijau)| Aman (180 hari)         |
+---------------------------------------------------------------------------------------------------------+
```

### B. Tampilan Komponen Recipe Scaler (Tab BOM)
```
+---------------------------------------------------------------------------------------------------------+
| SIMULASI TARGET PORSI (RECIPE SCALER)                                                                   |
| Menu: Es Kopi Susu Aren   |   Target Produksi: [ 100 ] Cup                                              |
+---------------------------+-----------------------+---------------------+-------------------------------+
| Komponen Bahan            | Resep / Porsi         | Total Kebutuhan     | Status Sisa Stok Gudang       |
+---------------------------+-----------------------+---------------------+-------------------------------+
| Biji Kopi House Blend     | 18 gram               | 1.800 gram (1.8 Kg) | CUKUP (Tersedia 8 Kg)         |
| Susu Segar Lembang        | 120 ml                | 12.000 ml (12 Liter)| KURANG 8 Liter (Stok: 4 Liter)|
| Gula Aren Cair            | 20 ml                 | 2.000 ml (2 Liter)  | CUKUP (Tersedia 5 Liter)      |
| Cup Plastik 16oz          | 1 pcs                 | 100 pcs             | CUKUP (Tersedia 250 pcs)      |
+---------------------------------------------------------------------------------------------------------+
```

---

## 7. Tahapan Pelaksanaan (*Milestones*)

* **Bulan 1 (Core Pipeline & Local Engine):**
  * Parser CSV transaksi kasir ke SQLite lokal.
  * Modul BOM resep dan Recipe Scaler.
  * Integrasi field Barcode/SKU dan library pemindai kamera (`html5-qrcode`).
* **Bulan 2 (Analytics Dashboard, Valuasi, & Packaging):**
  * Pembangunan grafik tren konsumsi 30 hari menggunakan **Recharts / D3.js**.
  * Implementasi widget Valuasi Aset Gudang & fitur Ekspor CSV.
  * Fitur konfigurasi custom threshold, progress bar stok, dan indikator jam berdenyut (*pulse animation*).
  * Pengemasan aplikasi desktop portable via PyInstaller dengan launcher otomatis ke browser.
* **Bulan 3 (Uji Coba Lapangan di Kafe Bandung):**
  * Pilot testing di 3 kafe di kawasan Dago dan Dipatiukur.
  * Pengujian ketepatan pemindaian barcode fisik menggunakan kamera laptop dan akurasi perhitungan Recipe Scaler saat jam sibuk.


  Berikut adalah draf pembaruan **Product Requirement Document (PRD) v1.8** untuk **LEUIT**, yang menambahkan dua modul krusial:
1. **Mesin Rekonsiliasi & Automasi Sinkronisasi CSV Berkala** (agar sistem berjalan berkelanjutan dengan *deduplikasi data otomatis* saat kasir diekspor mingguan/harian).
2. **Database Terenkripsi & Akses Kunci Ganda (*Dual-Key Locked SQLite*)** (menggunakan enkripsi militer AES-256 via SQLCipher yang hanya bisa dibuka oleh Pemilik Resto dan Pengembang Aplikasi untuk mencegah manipulasi data oleh staf/barista).

---

# Product Requirement Document (PRD)

| Metadata | Rincian |
| :--- | :--- |
| **Nama Produk** | **LEUIT** *(Lumbung Digital & Prediksi Stok Kafe)* |
| **Bentuk Distribusi** | **Desktop App Portable (`.exe` / `.dmg`) via PyInstaller** |
| **Arsitektur Keamanan** | **Encrypted Local SQLite (SQLCipher AES-256) with Dual-Key Access** |
| **Backend & Pipeline** | Python FastAPI + Deduplication Sync Engine |
| **Versi Dokumen** | v1.8 (Continuous CRUD & Encrypted Ledger Edition) |
| **Status** | Approved for Development |

---

## 1. Modul Keamanan: Database Terkunci & Kunci Ganda (*Dual-Key Access*)

Untuk mencegah staf/barista mengubah riwayat penjualan, menghapus catatan bahan baku yang dicuri, atau mengintip resep rahasia langsung dari file database, **database lokal SQLite dienkripsi total di level disk menggunakan SQLCipher (AES-256-CBC)**.

```
┌────────────────────────────────────────────────────────────────────────┐
│             DATABASE TERENKRIPSI LOKAL: `leuit_store.enc`              │
│                (SQLCipher 256-bit Transparent Encryption)              │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                    HANYA BISA DIBUKA OLEH 2 KUNCI:
         ┌──────────────────────────┴──────────────────────────┐
         ▼                                                     ▼
┌─────────────────────────────────┐   ┌─────────────────────────────────┐
│ 1. KUNCI PEMILIK RESTO          │   │ 2. KUNCI MASTER PENGEMBANG      │
│    (Owner Passkey / PIN)        │   │    (Developer Recovery Escrow)  │
│                                 │   │                                 │
│ - Diberikan saat aktivasi lisensi│  │ - Disimpan aman di vault Anda   │
│ - Barista di kafe hanya diberi  │   │ - Digunakan untuk audit jarak   │
│   akses operasional tanpa kunci │   │   jauh, pemulihan data rusak,   │
│   master file database          │   │   dan bantuan teknis resmi      │
└─────────────────────────────────┘   └─────────────────────────────────┘
```

### 1.1 Mekanisme Kriptografi Kunci Ganda (*Envelope Encryption Pattern*)
1. Database dienkripsi menggunakan satu kunci acak internal: **Database Encryption Key (DEK)**.
2. Nilai DEK tersebut kemudian dienkripsi dua kali menjadi dua *envelope*:
   * **Envelope A (Owner):** Dienkripsi dengan *Public Key / Password* Pemilik Resto.
   * **Envelope B (Developer):** Dienkripsi dengan *Master Public Key* milik Anda (Pengembang).
3. **Hasil:** Pemilik Resto dapat membuka database menggunakan kata sandi mereka, dan Anda sebagai pengembang memiliki kunci pembuka master (*backdoor recovery*) jika pemilik resto lupa kata sandi atau membutuhkan audit rekonsiliasi data.
4. **Staf Kasir/Barista:** Hanya memiliki hak operasional tingkat permukaan (*Application Session*). Jika file `leuit_store.enc` disalin ke flashdisk oleh pihak luar, file tersebut **sama sekali tidak bisa dibuka menggunakan DB Browser SQLite biasa tanpa kunci**.

---

## 2. Automasi & Rekonsiliasi Sinkronisasi CSV Kasir Berkala

Masalah utama aplikasi pencatat adalah kebosanan jika input hanya 1 kali di awal. Di dunia nyata, kasir mengekspor CSV setiap hari atau setiap minggu, dan sering kali file CSV memiliki data yang **tumpang tindih (*overlapping dates*)**.

### 2.1 Alur Rekonsiliasi Cerdas (*Idempotent Ingestion Pipeline*)

```
[ User Upload CSV Mingguan / Harian ]
                  │
                  ▼
[ Parser Python: Pembersihan & Normalisasi Data ]
                  │
                  ▼
[ Deteksi Hash Transaksi Unik: `sha256(pos_ref_id + timestamp + item_id)` ]
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
 [ Data Sudah Ada? ]   [ Data Transaksi Baru? ]
        │                   │
        ├─ Lewati / Abaikan ├─ Masukkan ke `sales_transactions`
        │  (Cegah Dobel Data)├─ Rekonsiliasi Pengurangan Stok Bahan Mentah
        │                   └─ Update Tabel Tren Penggunaan Harian
        ▼                   ▼
[ Catat Riwayat Sync ke `pos_sync_logs` ]
[ Tampilkan Ringkasan: "150 Baru Ditambahkan, 420 Data Lama Dilewati" ]
```

### 2.2 Aturan Logika Rekonsiliasi:
1. **Deduplikasi Otomatis (*Idempotency*):** Jika pemilik kafe mengunggah file CSV tanggal 1–15, lalu seminggu kemudian mengunggah file tanggal 10–22, sistem secara otomatis hanya memproses transaksi tanggal 16–22. Transaksi tanggal 10–15 diabaikan tanpa membuat data omzet menjadi ganda.
2. **Rekonsiliasi Pengurangan Stok Otomatis:**
   * Setiap kali transaksi baru masuk, sistem memecah menu ke dalam resep BOM, lalu **mengurangi stok bahan mentah terkait secara otomatis**.
   * Jika stok bahan baku di gudang mencapai 0, sistem mencatat status *minus-stock alert* (tanda ada bahan yang belum dicatat pembeliannya).
3. **Log Riwayat Sinkronisasi:** Menyimpan nama file, waktu upload, jumlah baris berhasil, dan jumlah baris terduplikasi untuk transparansi pelaporan.

---

## 3. Sistem CRUD Berkelanjutan (Continuous Operational Lifecycle)

Aplikasi menyediakan modul CRUD lengkap dan terpisah untuk kebutuhan harian:

1. **CRUD Master Bahan Baku (`/inventory`):**
   * *Create:* Tambah bahan baru lengkap dengan barcode kamera scanner.
   * *Read:* Monitoring stok, HPP, masa simpan, dan progress bar threshold.
   * *Update:* Edit biaya satuan (HPP jika harga pasar naik) dan stok fisik (*Stock Opname* harian).
   * *Delete:* Soft-delete (arsip) agar tidak merusak riwayat transaksi lama.
2. **CRUD Resep & Menu (`/bom`):**
   * Modifikasi gramasi resep jika barista mengubah takaran porsi.
   * Simulasi Recipe Scaler untuk pesanan katering.
3. **CRUD Suplier & Pembelian (`/purchases`):**
   * Input faktur belanja baru (Cash vs Kredit/Tempo).
   * Pelunasan hutang suplier saat jatuh tempo.

---

## 4. Pembaruan Skema Database (SQLite Terenkripsi: `leuit_store.enc`)

Skema ditambahkan tabel log audit, pencatatan upload CSV, dan penanda identitas transaksi unik:

```sql
-- 1. Master Bahan Baku
CREATE TABLE ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode_sku TEXT UNIQUE,
    name TEXT NOT NULL,
    unit TEXT NOT NULL,
    cost_per_unit REAL NOT NULL,
    shelf_life_days INTEGER NOT NULL,
    current_stock REAL DEFAULT 0,
    min_stock_threshold REAL DEFAULT 0,
    is_active INTEGER DEFAULT 1 -- 1 = Aktif, 0 = Terarsip (Soft Delete)
);

-- 2. Log Riwayat Sinkronisasi CSV Kasir
CREATE TABLE pos_sync_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name TEXT NOT NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_rows_read INTEGER NOT NULL,
    new_rows_inserted INTEGER NOT NULL,
    duplicate_rows_skipped INTEGER NOT NULL,
    date_range_start DATE,
    date_range_end DATE
);

-- 3. Transaksi Penjualan dengan Hash Unik (Deduplikasi)
CREATE TABLE sales_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_hash TEXT UNIQUE NOT NULL, -- SHA256(pos_ref_id + timestamp + menu_id)
    pos_reference_id TEXT,                 -- ID transaksi asli dari kasir Moka/Majoo
    menu_item_id INTEGER REFERENCES menu_items(id),
    quantity INTEGER NOT NULL,
    transaction_time DATETIME NOT NULL,
    sync_log_id INTEGER REFERENCES pos_sync_logs(id)
);

-- 4. Audit Log Operasional (Terkunci & Anti-Manipulasi)
CREATE TABLE operational_audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_type TEXT NOT NULL,             -- 'STOCK_OPNAME', 'RECIPE_EDIT', 'PURCHASE_PAID'
    entity_name TEXT NOT NULL,             -- 'Susu Segar Lembang'
    old_value TEXT,
    new_value TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    actor_role TEXT NOT NULL               -- 'OWNER' atau 'OPERATOR'
);

-- 5. Tabel Konfigurasi Kunci Enkripsi (Dual-Key Envelope)
CREATE TABLE security_keyring (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    encrypted_dek_owner TEXT NOT NULL,     -- Data Encryption Key terbungkus kunci Owner
    encrypted_dek_developer TEXT NOT NULL, -- Data Encryption Key terbungkus kunci Developer
    last_key_rotation DATETIME
);
```

---

## 5. Implementasi Teknis di Backend Python

### A. Mengaktifkan SQLCipher di Python
Backend Python menggunakan pustaka `sqlcipher3` untuk koneksi database terenkripsi:

```python
from pysqlcipher3 import dbapi2 as sqlite

def get_encrypted_db_connection(encryption_key: str):
    conn = sqlite.connect("leuit_store.enc")
    cursor = conn.cursor()
    # Memasukkan kunci enkripsi sebelum membuka database
    cursor.execute(f"PRAGMA key = '{encryption_key}';")
    cursor.execute("PRAGMA cipher_compatibility = 4;")
    return conn
```

### B. Endpoint Rekonsiliasi CSV Berkala (`ingestion.py`)
```python
from fastapi import APIRouter, UploadFile, File
import pandas as pd
import hashlib

router = APIRouter()

@router.post("/sync-pos-csv")
async def sync_pos_csv(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)
    
    new_records = 0
    duplicate_records = 0
    
    for _, row in df.iterrows():
        # Buat identitas unik baris transaksi
        raw_identity = f"{row['Order_ID']}_{row['Timestamp']}_{row['Item_Name']}"
        tx_hash = hashlib.sha256(raw_identity.encode()).hexdigest()
        
        # Eksekusi Insert dengan logika Skip jika sudah ada
        is_inserted = db.execute(
            """
            INSERT OR IGNORE INTO sales_transactions 
            (transaction_hash, pos_reference_id, menu_item_id, quantity, transaction_time)
            VALUES (?, ?, ?, ?, ?)
            """, (tx_hash, row['Order_ID'], row['Menu_ID'], row['Qty'], row['Timestamp'])
        )
        
        if is_inserted.rowcount > 0:
            new_records += 1
            # Trigger otomatis kurangi stok bahan baku berdasarkan BOM
            reconcile_ingredient_stock(row['Menu_ID'], row['Qty'])
        else:
            duplicate_records += 1
            
    return {
        "status": "success",
        "new_inserted": new_records,
        "duplicates_skipped": duplicate_records
    }
```

---

## 6. Dampak terhadap Desain & Kepercayaan Klien

1. **Jaminan Anti-Manipulasi untuk Pemilik Kafe:** Pemilik kafe yang memiliki banyak cabang atau menyerahkan kasir ke staf tidak perlu khawatir data transaksi diubah oleh pihak luar karena database lokalnya terenkripsi penuh.
2. **Kenyamanan Operasional Berkala:** Pemilik kafe cukup mengekspor CSV dari Moka/kasir kapan saja (harian, mingguan, bulanan) dan langsung mengunggahnya tanpa takut terjadi perhitungan ganda (*zero double-counting error*).
3. **Akses Bantuan Teknis Terjamin:** Anda sebagai pengembang memiliki kunci darurat (*Developer Master Key*) untuk membantu memulihkan data jika komputer kafe rusak atau pemiliknya lupa PIN, tanpa melanggar privasi harian mereka.