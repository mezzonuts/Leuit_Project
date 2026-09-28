Berikut adalah dokumen **Backend Architecture & Security Implementation Blueprint** untuk **LEUIT**, dirancang secara komprehensif, modular, dan siap digunakan oleh **Coding Agent** maupun tim pengembang backend:

---

# Backend Architecture & Security Blueprint: LEUIT Desktop App

| Metadata | Rincian |
| :--- | :--- |
| **Aplikasi** | **LEUIT** (Local-First F&B Demand & Inventory Forecasting) |
| **Core Runtime** | Python 3.11+ (FastAPI + Asynchronous ASGI) |
| **Penyimpanan Lokal** | Encrypted SQLite via **SQLCipher (AES-256-CBC)** |
| **Sistem Keamanan** | Dual-Key Envelope + Ed25519 Asymmetric Licensing + Hardware Binding |
| **Target Distribusi** | Single Portable Executable (`.exe` / `.dmg`) via PyInstaller + PyArmor |
| **Versi Dokumen** | v1.0 (Production-Ready Architecture) |

---

## 1. Topologi Sistem & Arsitektur Lapisan (Layered Architecture)

Backend dibangun dengan prinsip **Clean Architecture** berlapis untuk memisahkan antara proteksi keamanan biner, pemrosesan data, dan *endpoint* API:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Vite React SPA)                       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (JSON REST API via Localhost:8000)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   BACKEND PYTHON FASTAPI (LEUIT CORE)                  │
│                                                                        │
│  [Layer 1: Security & Anti-Crack Guard (Compiled via PyArmor/Cython)]  │
│   ├── Hardware Fingerprint Validator (Motherboard + CPU UUID)          │
│   ├── Asymmetric License Verifier (Ed25519 Signature + Expired Check)  │
│   ├── Monotonic Clock Guard (Anti-Time Travel / Mundurin Jam)          │
│   └── SQLCipher Dual-Key Derivation (Owner PIN vs Dev Master Key)      │
│                                                                        │
│  [Layer 2: API Gateway & Middleware (FastAPI)]                         │
│   ├── Security Middleware (Memastikan Database Terbuka & Lisensi Valid)│
│   ├── Exception Handlers (Grace Period & Lock Enforcer)                │
│   └── Routers (/inventory, /bom, /purchases, /sync, /forecast)         │
│                                                                        │
│  [Layer 3: Domain Services & Analytics Engines]                        │
│   ├── Idempotent POS Ingestion Engine (Deduplikasi Hash SHA-256)       │
│   ├── Recipe Scaler & Inventory Reconciliation Engine                  │
│   ├── Hyperlocal Forecasting Engine (Prophet + Cuaca BMKG Bandung)     │
│   └── Accounts Payable & Cash Ledger Engine                            │
│                                                                        │
│  [Layer 4: Data Access Layer (DAL)]                                    │
│   └── SQLCipher Connection Factory (`PRAGMA key = :dek`)               │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│     ENCRYPTED DATABASE FILE: `leuit_store.enc` (AES-256 on Disk)       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Struktur Direktori Proyek Backend (`/backend`)

```text
backend/
├── app/
│   ├── api/                     # REST API ROUTERS
│   │   ├── v1/
│   │   │   ├── auth_security.py # Unlock DB via PIN, Cek Lisensi
│   │   │   ├── inventory.py     # CRUD Bahan, SKU Barcode, Threshold
│   │   │   ├── bom.py           # CRUD Resep & Recipe Scaler
│   │   │   ├── purchases.py     # Transaksi Belanja Cash vs Tempo
│   │   │   ├── pos_sync.py      # Upload CSV Kasir & Rekonsiliasi
│   │   │   ├── forecast.py      # Smart Restock Sheet & Cuaca
│   │   │   └── valuation.py     # Valuasi Aset & Ekspor CSV
│   │   └── deps.py              # Dependency Injection (DB Session & Auth)
│   ├── core/                    # KONFIGURASI SISTEM
│   │   ├── config.py            # Environment & Public Key Ed25519
│   │   ├── database.py          # SQLCipher Engine Factory
│   │   └── security/            # MODUL KEAMANAN (DIKOMPILASI BINER)
│   │       ├── hardware.py      # Fingerprinting mesin (UUID/CPU)
│   │       ├── licensing.py     # Validasi Ed25519 & Clock Guard
│   │       ├── key_envelope.py  # Dual-Key Unlocking (Owner vs Dev)
│   │       └── ssl_pinning.py   # Pinning sertifikat ke cloud
│   ├── models/                  # SKEMA TABEL SQLALCHEMY / SQLCIPHER
│   │   ├── ingredient.py
│   │   ├── recipe.py
│   │   ├── purchase.py
│   │   ├── transaction.py
│   │   └── audit.py
│   ├── schemas/                 # VALIDASI INPUT/OUTPUT (PYDANTIC V2)
│   │   ├── ingredient_schema.py
│   │   ├── sync_schema.py
│   │   └── forecast_schema.py
│   ├── services/                # CORE DOMAIN & ANALYTICS PIPELINE
│   │   ├── pos_reconciler.py    # Deduplikasi SHA-256 & Potong Stok
│   │   ├── forecaster.py        # Model Deret Waktu + Bobot Bandung
│   │   ├── weather_client.py    # Fetch BMKG Weather API
│   │   └── recipe_scaler.py     # Perhitungan rasio porsi BOM
│   └── utils/
│       └── logger.py
├── scripts/
│   ├── build_binary.py          # Script build PyArmor + PyInstaller
│   └── generate_license.py      # Script internal dev untuk sign lisensi
├── main.py                      # Desktop Launcher & FastAPI Entrypoint
├── requirements.txt
└── LeuitApp.spec                # PyInstaller Packaging Specification
```

---

## 3. Spesifikasi Modul Keamanan & Anti-Crack (Deep-Dive)

### 3.1 Hardware Fingerprinting (`app/core/security/hardware.py`)
Mencegah file lisensi dipindahkan ke laptop lain tanpa izin:

```python
import hashlib
import subprocess
import platform

def get_machine_fingerprint() -> str:
    """Menghasilkan hash unik berdasarkan komponen fisik motherboard dan CPU."""
    system = platform.system()
    raw_id = ""
    try:
        if system == "Windows":
            # Ambil UUID Motherboard & Serial Processor
            uuid_cmd = subprocess.check_output("wmic csproduct get uuid", shell=True).decode()
            cpu_cmd = subprocess.check_output("wmic cpu get processorid", shell=True).decode()
            raw_id = f"{uuid_cmd.split()[1]}_{cpu_cmd.split()[1]}"
        elif system == "Darwin":  # macOS
            cmd = "ioreg -rd1 -c IOPlatformExpertDevice | grep IOPlatformUUID"
            raw_id = subprocess.check_output(cmd, shell=True).decode().split('"')[-2]
        else:  # Linux
            with open("/etc/machine-id", "r") as f:
                raw_id = f.read().strip()
    except Exception:
        import uuid
        raw_id = str(uuid.getnode())  # Fallback MAC address
        
    return hashlib.sha256(raw_id.strip().encode()).hexdigest()
```

### 3.2 Verifikasi Lisensi Asimetris & Clock Guard (`app/core/security/licensing.py`)
Menggunakan kriptografi kurva eliptik **Ed25519** untuk memverifikasi tanda tangan digital Cloud:

```python
import json
import time
import nacl.signing
import nacl.exceptions
from app.core.security.hardware import get_machine_fingerprint

CLOUD_PUBLIC_KEY = bytes.fromhex("YOUR_ED25519_PUBLIC_KEY_HEX_HERE")

class SecurityException(Exception):
    pass

def verify_license_token(token_bytes: bytes, signature_bytes: bytes, db_session) -> dict:
    verify_key = nacl.signing.VerifyKey(CLOUD_PUBLIC_KEY)
    
    # 1. Verifikasi Integritas Kriptografis
    try:
        payload = verify_key.verify(token_bytes, signature_bytes)
        license_data = json.loads(payload.decode('utf-8'))
    except (nacl.exceptions.BadSignatureError, Exception):
        raise SecurityException("Lisensi tidak valid atau telah dimodifikasi!")

    # 2. Validasi Hardware Binding
    if license_data.get("hardware_id") != get_machine_fingerprint():
        raise SecurityException("Lisensi ini terikat pada perangkat keras lain!")

    current_unix = int(time.time())

    # 3. Monotonic Clock Guard (Anti-Mundurin Jam)
    last_timestamp = db_session.execute(
        "SELECT MAX(last_seen_timestamp) FROM security_audit_clock"
    ).scalar() or 0

    if current_unix < last_timestamp:
        raise SecurityException("Manipulasi jam sistem terdeteksi! Sinkronkan jam komputer Anda.")

    # Simpan jejak waktu terbaru
    db_session.execute(
        "INSERT INTO security_audit_clock (last_seen_timestamp) VALUES (:ts)",
        {"ts": current_unix}
    )
    db_session.commit()

    # 4. Evaluasi Expired & Grace Period
    valid_until = license_data.get("valid_until", 0)
    grace_period_days = 3
    grace_limit = valid_until + (grace_period_days * 86400)

    if current_unix > grace_limit:
        return {"status": "LOCKED", "message": "Langganan telah kedaluwarsa."}
    elif current_unix > valid_until:
        return {"status": "GRACE_PERIOD", "days_left": int((grace_limit - current_unix) / 86400)}

    return {"status": "ACTIVE"}
```

### 3.3 Sistem Kunci Ganda (*Dual-Key Envelope Encryption*)
Database dienkripsi menggunakan kunci simetris `DEK` (*Data Encryption Key*). File `leuit_store.enc` hanya bisa dibuka jika `DEK` didekripsi menggunakan salah satu dari dua kunci berikut:
1. **Owner Passkey:** Diturunkan dari PIN/Password pemilik resto menggunakan algoritma *Argon2id*.
2. **Developer Master Key:** Kunci privat darurat yang dipegang pengembang aplikasi untuk *recovery*.

---

## 4. Skema Database Terenkripsi (SQLCipher DDL)

Koneksi database dibuka menggunakan parameter enkripsi:
```sql
PRAGMA key = 'DATABASE_ENCRYPTION_KEY_HASIL_DERIVASI';
PRAGMA cipher_compatibility = 4;
PRAGMA cipher_page_size = 4096;
PRAGMA kdf_iter = 256000;
```

### Definisi Tabel Inti (`leuit_store.enc`):
```sql
-- 1. Master Bahan Baku
CREATE TABLE ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode_sku TEXT UNIQUE,
    name TEXT NOT NULL,
    unit TEXT NOT NULL CHECK(unit IN ('ml', 'gram', 'pcs')),
    cost_per_unit REAL NOT NULL,
    shelf_life_days INTEGER NOT NULL,
    current_stock REAL DEFAULT 0,
    min_stock_threshold REAL DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Master Menu POS
CREATE TABLE menu_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pos_item_id TEXT UNIQUE,
    name TEXT NOT NULL,
    sale_price REAL NOT NULL
);

-- 3. Resep / Bill of Materials (BOM)
CREATE TABLE recipe_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_item_id INTEGER REFERENCES menu_items(id) ON DELETE CASCADE,
    ingredient_id INTEGER REFERENCES ingredients(id) ON DELETE RESTRICT,
    quantity_required REAL NOT NULL
);

-- 4. Riwayat Transaksi Penjualan (Deduplikasi Idempotent)
CREATE TABLE sales_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_hash TEXT UNIQUE NOT NULL, -- SHA256(pos_ref_id + timestamp + menu_id)
    pos_reference_id TEXT,
    menu_item_id INTEGER REFERENCES menu_items(id),
    quantity INTEGER NOT NULL,
    transaction_time DATETIME NOT NULL,
    sync_batch_id INTEGER REFERENCES pos_sync_logs(id)
);

-- 5. Log Sinkronisasi CSV Kasir
CREATE TABLE pos_sync_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name TEXT NOT NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_rows INTEGER NOT NULL,
    new_rows INTEGER NOT NULL,
    skipped_duplicates INTEGER NOT NULL
);

-- 6. Suplier & Transaksi Pembelian (Cash vs Tempo)
CREATE TABLE suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone_whatsapp TEXT,
    payment_terms_days INTEGER DEFAULT 0 -- 0 = Cash, 7/14/30 = Tempo
);

CREATE TABLE inventory_purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    purchase_date DATE NOT NULL,
    ingredient_id INTEGER REFERENCES ingredients(id),
    supplier_id INTEGER REFERENCES suppliers(id),
    quantity REAL NOT NULL,
    total_cost REAL NOT NULL,
    payment_method TEXT CHECK(payment_method IN ('CASH', 'CREDIT')),
    payment_status TEXT CHECK(payment_status IN ('PAID', 'UNPAID')),
    due_date DATE
);

-- 7. Audit Clock Guard (Anti-Time Travel)
CREATE TABLE security_audit_clock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    last_seen_timestamp INTEGER NOT NULL,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 5. Domain Engine & Rekonsiliasi Data

### 5.1 Mesin Rekonsiliasi CSV Berkala (`services/pos_reconciler.py`)
Mencegah data dobel dan otomatis memotong sisa stok bahan baku fisik di gudang:

```python
import hashlib
import pandas as pd
from sqlalchemy.orm import Session
from app.models.transaction import SalesTransaction, PosSyncLog
from app.models.recipe import RecipeItem
from app.models.ingredient import Ingredient

def reconcile_pos_csv(file_bytes, file_name: str, db: Session) -> dict:
    df = pd.read_csv(file_bytes)
    
    new_count = 0
    duplicate_count = 0
    stock_deductions = {} # {ingredient_id: total_qty_to_deduct}

    sync_log = PosSyncLog(file_name=file_name, total_rows=len(df), new_rows=0, skipped_duplicates=0)
    db.add(sync_log)
    db.flush()

    for _, row in df.iterrows():
        # Buat identitas unik transaksi
        raw_hash = f"{row['Order_ID']}_{row['Timestamp']}_{row['Menu_Name']}"
        tx_hash = hashlib.sha256(raw_hash.encode()).hexdigest()

        # Cek apakah sudah pernah masuk
        exists = db.query(SalesTransaction).filter_by(transaction_hash=tx_hash).first()
        if exists:
            duplicate_count += 1
            continue

        # Insert transaksi baru
        new_tx = SalesTransaction(
            transaction_hash=tx_hash,
            pos_reference_id=str(row['Order_ID']),
            menu_item_id=row['Menu_ID'],
            quantity=row['Qty'],
            transaction_time=pd.to_datetime(row['Timestamp']),
            sync_batch_id=sync_log.id
        )
        db.add(new_tx)
        new_count += 1

        # Hitung bahan baku yang harus dipotong dari resep BOM
        recipes = db.query(RecipeItem).filter_by(menu_item_id=row['Menu_ID']).all()
        for r in recipes:
            stock_deductions[r.ingredient_id] = stock_deductions.get(r.ingredient_id, 0) + (r.quantity_required * row['Qty'])

    # Eksekusi pemotongan stok bahan fisik di gudang
    for ing_id, deduct_qty in stock_deductions.items():
        ing = db.query(Ingredient).filter_by(id=ing_id).first()
        if ing:
            ing.current_stock = max(0.0, ing.current_stock - deduct_qty)

    sync_log.new_rows = new_count
    sync_log.skipped_duplicates = duplicate_count
    db.commit()

    return {
        "new_inserted": new_count,
        "duplicates_skipped": duplicate_count,
        "deducted_ingredients_count": len(stock_deductions)
    }
```

### 5.2 Mesin Simulasi Recipe Scaler (`services/recipe_scaler.py`)
```python
def calculate_recipe_scale(menu_id: int, target_portions: int, db: Session):
    recipes = db.query(RecipeItem).filter_by(menu_item_id=menu_id).all()
    results = []
    
    for r in recipes:
        ing = r.ingredient
        total_needed = r.quantity_required * target_portions
        is_sufficient = ing.current_stock >= total_needed
        deficit = max(0.0, total_needed - ing.current_stock)
        
        results.append({
            "ingredient_name": ing.name,
            "unit": ing.unit,
            "per_portion": r.quantity_required,
            "total_needed": total_needed,
            "current_stock": ing.current_stock,
            "is_sufficient": is_sufficient,
            "deficit": deficit
        })
    return results
```

---

## 6. Launcher Desktop & Build Pipeline (PyInstaller)

### 6.1 Entrypoint Launcher (`main.py`)
Mengeksekusi backend lokal di latar belakang dan otomatis membuka antarmuka browser:

```python
import sys
import threading
import time
import webbrowser
import uvicorn
from app.api.v1.api import app

def launch_browser():
    time.sleep(1.8)  # Tunggu server aktif
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    # Jalankan browser di thread independen
    threading.Thread(target=launch_browser, daemon=True).start()
    
    # Jalankan ASGI server
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="warning",
        access_log=False
    )
```

### 6.2 Prosedur Hardening & Packaging (`scripts/build_binary.py`)
Untuk mencegah cracking, proses build wajib melalui urutan proteksi berikut:

```bash
# 1. Obfuskasi file keamanan menggunakan PyArmor
pyarmor gen --exact app/core/security/licensing.py app/core/security/hardware.py

# 2. Build Frontend Vite menjadi static file
cd ../frontend && npm run build && cd ../backend

# 3. Mount static file frontend ke dalam binary via PyInstaller
pyinstaller --noconfirm --onedir --windowed \
    --add-data "frontend/dist;dist" \
    --hidden-import "sqlcipher3" \
    --name "LeuitApp" \
    main.py
```

---

## 7. Kontrak REST API Utama (OpenAPI Spec)

| Metode | Endpoint | Keterangan |
| :--- | :--- | :--- |
| `POST` | `/api/v1/auth/unlock` | Input PIN Owner / Dev Master Key untuk membuka database |
| `GET` | `/api/v1/auth/status` | Mengecek status lisensi, masa tenggang, dan status gembok |
| `GET` | `/api/v1/inventory` | Mendapatkan daftar seluruh bahan, progress bar, & threshold |
| `POST` | `/api/v1/inventory` | Menambah bahan baku baru (nama, SKU barcode, unit, HPP) |
| `POST` | `/api/v1/inventory/stock-opname` | Penyesuaian stok fisik harian |
| `GET` | `/api/v1/valuation` | Menghitung total nilai moneter stok gudang (IDR) |
| `GET` | `/api/v1/valuation/export-csv` | Mengunduh rekapitulasi data valuasi aset dalam berkas CSV |
| `POST` | `/api/v1/sync/pos-csv` | Unggah CSV kasir harian/mingguan dengan rekonsiliasi otomatis |
| `POST` | `/api/v1/bom/scaler` | Menghitung simulasi kebutuhan bahan untuk target porsi |
| `POST` | `/api/v1/purchases` | Mencatat transaksi pembelian stok (Cash vs Tempo) |
| `GET` | `/api/v1/purchases/payables` | Daftar pengingat tagihan suplier yang mendekati jatuh tempo |
| `GET` | `/api/v1/forecast/restock-sheet` | Menghasilkan rekomendasi belanja bahan 7 hari ke depan |

---

## 8. Panduan Eksekusi untuk Coding Agent (Sprint Breakdown)

Coding Agent harus mengeksekusi backend dalam urutan sprint berikut:

1. **Sprint 1 (Keamanan Biner & Database Factory):**
   * Buat `hardware.py` (fingerprint extraction) dan `licensing.py` (Ed25519 verifier).
   * Konfigurasi koneksi SQLCipher di `database.py` dengan penanganan `PRAGMA key`.
   * Terapkan middleware status lisensi (Active, Grace Period, Locked).

2. **Sprint 2 (Master Bahan, SKU Barcode, & Valuasi):**
   * Bangun router `/inventory` (CRUD bahan, stock opname, threshold).
   * Implementasikan endpoint `/valuation` dan fungsi *stream* file CSV.

3. **Sprint 3 (Engine Rekonsiliasi CSV Kasir):**
   * Terapkan logika deduplikasi SHA-256 pada `/sync/pos-csv`.
   * Integrasikan pengurangan stok bahan baku otomatis saat transaksi baru diimpor.

4. **Sprint 4 (Resep BOM, Scaler, & Pembelian Cash/Tempo):**
   * Bangun modul BOM dan logika perkalian rasio porsi di `/bom/scaler`.
   * Buat pencatatan pembelian stok dengan filter tagihan jatuh tempo di `/purchases`.

5. **Sprint 5 (Predictive Engine & Cuaca Bandung):**
   * Integrasikan client API cuaca BMKG Bandung.
   * Buat perhitungan estimasi konsumsi mingguan + safety stock buffer di `/forecast`.

6. **Sprint 6 (Packaging & Entrypoint):**
   * Buat launcher `main.py` yang otomatis membuka browser di `localhost:8000`.
   * Siapkan file spesifikasi PyInstaller `LeuitApp.spec` untuk pengujian kompilasi.