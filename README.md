# LEUIT - Lumbung Digital & Prediksi Stok Kafe

> **Local-First F&B Demand & Inventory Forecasting**  
> Desktop App Portable untuk Kafe & Restoran Independen di Bandung & Jawa Barat

---

## 🎯 Fitur Utama

| Modul | Deskripsi |
|-------|-----------|
| **Dashboard Monitoring** | Valuasi aset real-time, grafik tren konsumsi 30 hari (Recharts), alert kadaluwarsa pulse icon, progress bar threshold stok |
| **Inventaris (CRUD)** | Master bahan baku, barcode/QR scanner via kamera, stock opname, custom minimum threshold per bahan |
| **Resep & Menu (BOM)** | Bill of Materials, Recipe Scaler simulasi porsi catering vs stok real-time |
| **Pembelian Stok** | Cash vs Kredit/Tempo (7/14/30 hari), supplier management, accounts payable alert jatuh tempo |
| **Sinkronisasi POS** | Upload CSV kasir berkala (Moka/Majoo/Olsera), deduplikasi SHA-256 otomatis, rekonsiliasi stok bahan baku |
| **Prediksi Restock** | Forecasting 7 hari ke depan + cuaca BMKG Bandung + safety buffer |

---

## 🔐 Keamanan Data

- **Database Terenkripsi**: SQLCipher AES-256 (`leuit_store.enc`)
- **Dual-Key Access**: Owner PIN (pemilik kafe) + Developer Master Key (recovery audit)
- **Privacy-First**: 100% data lokal di laptop kafe, zero cloud sync data transaksi/resep
- **Anti-Manipulasi**: Hardware binding, monotonic clock guard, Ed25519 license verification

---

## 🏗️ Arsitektur Teknis

```
┌─────────────────────────────────────────────────────────────┐
│                    DESKTOP APP (Portable)                   │
├─────────────────────────────────────────────────────────────┤
│  Frontend: React + Vite + Tailwind + Recharts (SPA)        │
│  Backend:  Python FastAPI + SQLCipher + Prophet            │
│  Database: SQLite Encrypted (AES-256)                      │
│  Packaging: PyInstaller + PyArmor (single .exe/.dmg)       │
└─────────────────────────────────────────────────────────────┘
```

**Stack:**
- Frontend: React 18, TypeScript, Vite, Tailwind CSS, TanStack Query, Recharts, React Hook Form + Zod, html5-qrcode
- Backend: Python 3.11+, FastAPI, SQLAlchemy 2.0, SQLCipher (pysqlcipher3), Prophet, pandas, uv package manager
- CI/CD: GitHub Actions (Linux + Windows runners)
- Distribution: Portable executable via PyInstaller

---

## 🚀 Quick Start (Development)

### Prerequisites
- Node.js 20+ & pnpm 9+
- Python 3.11+ & uv
- Git

### Setup
```bash
# Clone repo
git clone <repo-url>
cd leuit

# Install frontend dependencies
cd frontend && pnpm install

# Install backend dependencies
cd ../backend && uv sync

# Generate dev keys (first time only)
cd .. && python scripts/generate_keys.py
python scripts/generate_license.py

# Run development servers
# Terminal 1 - Backend
cd backend && uv run uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend && pnpm dev
```

Aplikasi akan terbuka di `http://localhost:5173` (frontend) + `http://localhost:8000` (backend API)

---

## 📦 Build Production Binary

```bash
# Build frontend
cd frontend && pnpm build

# Obfuscate security modules
cd ../backend && pyarmor gen --exact app/core/security/licensing.py app/core/security/hardware.py

# Build binary
pyinstaller --noconfirm --onedir --windowed \
  --add-data "frontend/dist;dist" \
  --hidden-import "sqlcipher3" \
  --name "LeuitApp" \
  main.py

# Output: dist/LeuitApp/LeuitApp.exe (Windows)
```

---

## 📁 Struktur Monorepo

```
leuit/
├── .github/workflows/ci.yml      # GitHub Actions CI/CD
├── .gitlab-ci.yml                # GitLab CI mirror
├── pnpm-workspace.yaml           # pnpm workspace config
├── pyproject.toml                # Root Python config (optional)
├── README.md
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── src/
│   └── index.html
├── backend/
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── app/
│   │   ├── api/v1/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── utils/
│   ├── scripts/
│   │   ├── build_binary.py
│   │   ├── generate_keys.py
│   │   └── generate_license.py
│   ├── main.py
│   └── LeuitApp.spec
└── docs/
    ├── PRD.md
    ├── Frontend_arsitektur.md
    └── Backend_arsitektur.md
```

---

## 🧪 Testing & Quality Gates

```bash
# Frontend
cd frontend
pnpm lint          # ESLint
pnpm typecheck     # TypeScript strict
pnpm test          # Vitest
pnpm test:coverage # Coverage report

# Backend
cd backend
uv run ruff check .      # Lint
uv run mypy .            # Type check
uv run pytest --cov=app  # Tests + coverage
```

**Quality Gates (PR ke `staging`):**
- Lint: 0 error, 0 warning
- TypeCheck: 0 error
- Unit Test Coverage: ≥ 80%
- E2E Test: 100% pass (Playwright)
- Security: PyArmor verified, no secrets in logs

---

## 📋 Branch Strategy

```
main (production-ready)
  ↑
staging (integration branch, CI passes)
  ↑
feat/<scope> | fix/<scope> | chore/<scope>
```

- PR target: `staging`
- Merge: Squash & merge, delete branch
- Release: Tag `vX.Y.Z` on `main` → trigger build binary workflow

---

## 📄 Dokumentasi

- [PRD v1.8](docs/PRD.md) - Product Requirement Document
- [Frontend Architecture v1.8](docs/Frontend_arsitektur.md)
- [Backend Architecture v1.0](docs/Backend_arsitektur.md)
- [Implementation Plan](.kilo/PLAN.md)

---

## 📝 Lisensi

Proprietary - LEUIT Team. All rights reserved.