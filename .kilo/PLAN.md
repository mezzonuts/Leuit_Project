# Implementation Plan: LEUIT Desktop App

> **Produk:** LEUIT - Local-First F&B Demand & Inventory Forecasting  
> **Versi:** v1.8 (Encrypted Ledger & Continuous CRUD Edition)  
> **Arsitektur:** React SPA (Vite) + FastAPI + SQLCipher AES-256  
> **Distribusi:** Portable `.exe` / `.dmg` via PyInstaller + PyArmor  

---

## 📋 Konfigurasi Proyek

| Item | Keputusan |
|------|-----------|
| **Hosting Repo** | GitLab (self-hosted atau gitlab.com) |
| **CI/CD** | GitHub Actions (runner self-hosted di server GitLab) |
| **Frontend PM** | pnpm |
| **Backend PM** | uv (Python) |
| **Branch Strategy** | `main` → `staging` → feature branches |
| **Code Quality** | ESLint + Prettier + TypeScript strict + Ruff + mypy |
| **Testing** | Vitest (frontend) + pytest (backend) + Playwright (E2E) |

---

## 🗓️ Rencana Harian (14 Hari / 2 Sprint)

### Sprint 1: Foundation & Security (Hari 1-7)

| Hari | Fokus | Deliverable |
|------|-------|-------------|
| **1** | **Repo Init & CI/CD** ✅ | `git init`, folder structure, GitHub Actions workflow, GitLab CI mirror, README, `.gitignore`, `pnpm-workspace.yaml`, `pyproject.toml` — merged to staging |
| **2** | **Backend: SQLCipher + Dual-Key Auth** ✅ | `app/core/security/` (hardware.py, licensing.py, key_envelope.py), `app/core/database.py` (SQLCipher engine), middleware license guard — PR #3 merged |
| **3** | **Backend: Auth API & Models** ✅ | All models verified, 59 new tests (model properties, to_dict, repr, auth schemas), PR #4 merged |
| **4** | **Backend: Inventory CRUD + Valuation** ✅ | Router verified (11 endpoints), 40 new tests, schema hardened (barcode regex, cost>0), PR #5 merged |
| **5** | **Backend: POS Sync Engine** ✅ | Router verified (3 endpoints, 235 lines), 20 new tests (dedup, column mapping, BOM deduction), schema hardened, PR #6 merged |
| **6** | **Frontend: Vite + React + Tailwind + Auth UI** ✅ | Auth components verified (11+7), Layout verified (10+12+11), 51 new tests, PR #7 merged |
| **7** | **Frontend: Inventory CRUD + Slide-Over Drawer** | `IngredientTable.tsx`, `IngredientDrawer.tsx` (450px slide-over), `BarcodeCameraModal.tsx` (html5-qrcode), React Hook Form + Zod |

---

### Sprint 2: Features & Polish (Hari 8-14)

| Hari | Fokus | Deliverable |
|------|-------|-------------|
| **8** | **Frontend: Dashboard Monitoring** | `ValuationMetricCard.tsx` (CSV export), `UsageTrendBarChart.tsx` (Recharts 30 hari + filter), `CriticalAlertsSection.tsx` (pulse icon <3 hari), `StockHealthTable.tsx` (progress bar threshold) |
| **9** | **Frontend: BOM + Recipe Scaler** | `RecipeList.tsx`, `RecipeDrawer.tsx`, `RecipeScalerTool.tsx` (simulasi porsi vs stok real-time) |
| **10** | **Frontend: Purchases Cash/Tempo** | `PurchaseEntryDrawer.tsx`, `RestockSheetView.tsx`, `AccountsPayableAlert.tsx` (jatuh tempo) |
| **11** | **Frontend: POS Sync UI** | `PosSyncDrawer.tsx` (drag-drop CSV), `SyncResultSummary.tsx` (new/duplicate cards), `SyncHistoryTable.tsx` |
| **12** | **Backend: Forecasting & Weather** | `services/forecaster.py` (Prophet + BMKG Bandung), `services/weather_client.py`, `/forecast/restock-sheet` |
| **13** | **Integration & Hardening** | PyArmor obfuscation (security modules), PyInstaller spec, `main.py` launcher (auto-open browser), license grace banner |
| **14** | **QA, Code Review, Bug Fix, Report** | Full test run, lint/typecheck, security audit, performance check, generate `RELEASE_REPORT.md` |

---

## 🔧 CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  lint-typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
      - uses: actions/setup-node@v4
      - uses: astral-sh/setup-uv@v3
      - run: pnpm install --frozen-lockfile
      - run: uv sync --frozen
      - run: pnpm lint && pnpm typecheck
      - run: uv run ruff check . && uv run mypy .
  
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
      - uses: actions/setup-node@v4
      - uses: astral-sh/setup-uv@v3
      - run: pnpm install --frozen-lockfile
      - run: uv sync --frozen
      - run: pnpm test:coverage
      - run: uv run pytest --cov=app --cov-report=xml
  
  build-frontend:
    needs: [lint-typecheck, test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
      - uses: actions/setup-node@v4
      - run: pnpm install --frozen-lockfile
      - run: pnpm build
      - uses: actions/upload-artifact@v4
        with: { name: frontend-dist, path: frontend/dist }
  
  build-binary:
    needs: build-frontend
    runs-on: windows-latest  # untuk .exe
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - uses: actions/download-artifact@v4
        with: { name: frontend-dist, path: frontend/dist }
      - run: uv sync --frozen
      - run: pyarmor gen --exact app/core/security/licensing.py app/core/security/hardware.py
      - run: pyinstaller --noconfirm --onedir --windowed --add-data "frontend/dist;dist" --hidden-import "sqlcipher3" --name "LeuitApp" main.py
      - uses: actions/upload-artifact@v4
        with: { name: LeuitApp-win64, path: dist/LeuitApp }
```

---

## 📁 Struktur Repo (Monorepo)

```
leuit/
├── .github/workflows/ci.yml
├── .gitlab-ci.yml          # mirror untuk GitLab runner
├── pnpm-workspace.yaml
├── pyproject.toml
├── README.md
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── stores/
│   │   ├── types/
│   │   ├── utils/
│   │   ├── App.tsx
│   │   └── main.tsx
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
│   │   └── generate_license.py
│   ├── main.py
│   └── LeuitApp.spec
└── docs/
    ├── PRD.md
    ├── Frontend_arsitektur.md
    └── Backend_arsitektur.md
```

---

## ✅ Quality Gates (Setiap PR ke `staging`)

| Gate | Tool | Threshold |
|------|------|-----------|
| **Lint** | ESLint (frontend) + Ruff (backend) | 0 error, 0 warning |
| **TypeCheck** | TypeScript strict + mypy | 0 error |
| **Unit Test** | Vitest + pytest | Coverage ≥ 80% |
| **E2E Test** | Playwright (critical paths) | 100% pass |
| **Security** | PyArmor obfuscation verified, SQLCipher key never logged | Manual review |
| **Build** | `pnpm build` + `pyinstaller` success | Artifacts generated |

---

## 🐛 Bug Tracking & Code Review Process

1. **Branch naming**: `feat/<scope>`, `fix/<scope>`, `chore/<scope>`
2. **PR Template**: Deskripsi, linked issue, test plan, screenshot (UI)
3. **Review checklist**:
   - [ ] TypeScript strict / mypy clean
   - [ ] Test coverage ≥ 80% untuk logic baru
   - [ ] No hardcoded secrets (API key, encryption key)
   - [ ] SQLCipher PRAGMA key tidak di-log
   - [ ] Accessibility: keyboard nav, ARIA labels
   - [ ] Responsive: desktop 1366x768 minimum
4. **Merge**: Squash & merge ke `staging`, delete branch

---

## 📊 Final Report: `RELEASE_REPORT.md`

Akan di-generate otomatis di akhir Sprint 2 berisi:
- Ringkasan fitur terimplementasi vs PRD
- Test coverage report (frontend + backend)
- Security audit findings
- Binary size & startup time benchmark
- Known issues / technical debt
- Checklist production readiness

---

## ❓ Open Questions (Perlu Keputusan)

1. **Ed25519 Public Key** - Sudah ada key pair production? Atau generate baru di Sprint 1?
2. **BMKG API** - Apakah butuh API key resmi atau pakai public endpoint?
3. **License Server** - Cloud endpoint untuk verifikasi lisensi sudah siap? Atau mock dulu?
4. **Code Signing** - Windows EV certificate & Apple Developer ID tersedia untuk binary signing?
5. **Updater** - Apakah butuh auto-update mechanism (Squirrel/Sparkle) atau manual download?

---

## 🚀 Next Steps

1. User review plan ini
2. Jika approve → `plan_exit` dan mulai implementasi
3. Setup repo di GitLab + GitHub Actions runner
4. Mulai **Hari 1: Repo Init & CI/CD**

---

*Plan dibuat berdasarkan PRD v1.8, Frontend Architecture v1.8, Backend Architecture v1.0*  
*Semua komentar & dokumentasi dalam Bahasa Indonesia*