# Sprint 2 Plan: Features & Polish (Hari 15-28)

> **Produk**: LEUIT - Local-First F&B Demand & Inventory Forecasting  
> **Versi**: v1.8 → v1.9 (Sprint 2 Features)  
> **Durasi**: 14 Hari (Hari 15-28)  
> **Branch Strategy**: `main` → `staging` → `feat/day<N>-<scope>`  
> **Quality Gates**: 0 lint/typecheck errors, 0 CI failures, >80% coverage

---

## 📋 Sprint 2 Overview

| Metric | Target |
|--------|--------|
| **Hari** | 14 hari (Day 15-28) |
| **Fokus** | Advanced Features, Multi-outlet, Mobile, Analytics, Hardening |
| **PR Target** | 1 PR/hari (14 PRs total) |
| **Test Target** | +200 tests (backend + frontend) |
| **Branch Base** | `staging` (Sprint 1 complete) |

---

## 🗓️ Daily Schedule

### Week 3: Advanced Features (Day 15-21)

| Hari | Fokus | Deliverable | Tests Target | PR Target |
|------|-------|-------------|--------------|-----------|
| **15** | **Advanced Forecasting** | Prophet integration, seasonality, holiday effects, 30-day forecast | 15 backend | #16 |
| **16** | **Multi-outlet Support** | Branch management, consolidated reports, per-outlet inventory | 15 backend + 10 frontend | #17 |
| **17** | **Mobile Companion (PWA)** | PWA manifest, offline sync, install prompt, React Native starter | 15 frontend | #18 |
| **18** | **Advanced Analytics** | Drill-down reports, export scheduling, custom dashboards | 15 backend + 10 frontend | #19 |
| **19** | **Supplier Integration** | API connectors (Moka, Majoo), auto-PO generation | 15 backend + 10 frontend | #20 |
| **20** | **Customer Facing** | Menu QR codes, digital receipts, public menu page | 10 frontend + 5 backend | #21 |
| **21** | **Audit Trail** | Immutable logs, compliance export, tamper-proof | 10 backend + 5 frontend | #22 |

### Week 4: Polish & Production (Day 22-28)

| Hari | Fokus | Deliverable | Tests Target | PR Target |
|------|-------|-------------|--------------|-----------|
| **22** | **Performance Tuning** | Query optimization, Redis caching, bundle splitting | 10 backend + 10 frontend | #23 |
| **23** | **Accessibility Audit** | WCAG 2.1 AA compliance, keyboard nav, screen reader | 15 frontend | #23 |
| **24** | **Localization** | Multi-language (ID/EN), i18n infrastructure | 10 frontend + 5 backend | #24 |
| **24** | **Plugin Architecture** | 3rd party extensions, webhook system, SDK | 10 backend | #25 |
| **25** | **CI/CD Hardening** | Security scanning (SAST/DAST), SBOM, signed releases | 10 backend | #25 |
| **26** | **Load Testing** | 1000+ concurrent users, k6 scripts, bottlenecks | 5 backend | #26 |
| **27** | **Release Candidate** | v1.9.0-rc1 tag, docs, migration guide | 5 full-stack | #27 |
| **28** | **Sprint 2 Review** | Sprint 2 report, Sprint 3 planning, retro | - | - |

---

## 🎯 Detailed Task Breakdown

### Day 15: Advanced Forecasting (Prophet Integration)

**Scope**: `backend/app/services/forecaster.py` enhancement, `weather_client.py` upgrade

| Task | Description | Acceptance Criteria |
|------|-------------|---------------------|
| 15.1 | Integrate Prophet library | `pip install prophet`, model training on 90-day history |
| 15.2 | Seasonality detection | Weekly/yearly seasonality auto-detection |
| 15.3 | Holiday effects | Indonesian holidays (libur nasional, cuti bersama) |
| 15.3 | Weather-adjusted predictions | Temperature/humidity correlation with sales |
| 15.4 | 30-day forecast endpoint | `/forecast/30-day` endpoint with confidence intervals |
| 15.5 | Model persistence | Save/load trained models, versioning |
| 15.6 | Tests | 15 tests: Prophet integration, seasonality, holidays, weather adj, 30-day forecast |

**Files**: `backend/app/services/forecaster.py`, `backend/app/api/v1/forecast.py`, `tests/test_forecasting.py`

---

### Day 16: Multi-outlet Support

**Scope**: Branch management, consolidated reports, per-outlet inventory

| Task | Description | Acceptance Criteria |
|------|-------------|---------------------|
| 16.1 | Outlet model | `Outlet` model: id, name, address, phone, is_active, settings JSON |
| 16.2 | Per-outlet inventory | `Inventory` → add `outlet_id`, isolate stock per outlet |
| 16.3 | Consolidated reports | `/reports/consolidated` aggregates across outlets |
| 16.4 | Outlet switcher UI | Header dropdown, persists in localStorage |
| 16.4 | Per-outlet purchases | PurchaseEntryDrawer filters by outlet |
| 16.5 | Tests | 15 backend + 10 frontend |

**Files**: New `Outlet` model, modify `Ingredient`, `InventoryPurchase`, `Purchases.tsx`, new `OutletSwitcher.tsx`

---

### Day 17: Mobile Companion (PWA)

**Scope**: PWA manifest, offline sync, install prompt, React Native starter

| Task | Description | Acceptance Criteria |
|------|-------------|---------------------|
| 17.1 | PWA manifest | `manifest.json`, icons, splash screens, theme color |
| 17.2 | Service Worker | Workbox: cache-first for assets, network-first for API |
| 17.3 | Offline queue | IndexedDB queue for mutations, sync on reconnect |
| 17.4 | Install prompt | BeforeInstallPromptEvent handler, custom install button |
| 17.5 | React Native starter | `mobile/` folder, Expo init, shared types |
| 17.4 | Tests | 15 frontend |

**Files**: `frontend/public/manifest.json`, `frontend/src/sw.js`, `frontend/src/hooks/useOfflineSync.ts`, `mobile/`

---

### Day 18: Advanced Analytics

**Scope**: Drill-down reports, export scheduling, custom dashboards

| Task | Description | Acceptance Criteria |
|------|-------------|---------------------|
| 18.1 | Drill-down reports | Click chart → detail view (daily/weekly/monthly) |
| 18.2 | Export scheduling | Cron jobs: daily/weekly PDF/Excel email |
| 18.3 | Custom dashboards | Drag-drop widgets, save layouts per user |
| 18.3 | Date range picker | Presets: 7d, 30d, 90d, custom |
| 18.4 | Tests | 15 backend + 10 frontend |

**Files**: New `DashboardBuilder.tsx`, `ReportScheduler.tsx`, `backend/app/services/report_scheduler.py`

---

### Day 19: Supplier Integration

**Scope**: API connectors (Moka, Majoo), auto-PO generation

| Task | Description | Acceptance Criteria |
|------|-------------|---------------------|
| 19.1 | Moka API connector | OAuth2, sync products/orders, webhook for real-time |
| 19.2 | Majoo API connector | API key auth, sync products/orders |
| 19.3 | Auto-PO generation | Threshold-based PO draft creation |
| 19.4 | Supplier portal | Supplier self-service: view POs, update catalog |
| 19.4 | Tests | 15 backend + 10 frontend |

**Files**: `backend/app/services/moka_connector.py`, `majoo_connector.py`, `backend/app/api/v1/suppliers.py`

---

### Day 20: Customer Facing Features

**Scope**: Menu QR codes, digital receipts, public menu page

| Task | Description | Acceptance Criteria |
|------|-------------|---------------------|
| 20.1 | QR code generator | Per-table QR, deep link to menu |
| 20.2 | Digital receipts | Email/SMS/WhatsApp receipt, PDF download |
| 20.2 | Public menu page | SEO-friendly, no auth required, read-only |
| 20.3 | Tests | 10 frontend + 5 backend |

**Files**: `frontend/src/components/customer/MenuQR.tsx`, `ReceiptGenerator.tsx`, `PublicMenuPage.tsx`

---

### Day 21: Audit Trail

**Scope**: Immutable logs, compliance export, tamper-proof

| Task | Description | Acceptance Criteria |
|------|-------------|---------------------|
| 21.1 | Append-only log table | `AuditLog`: id, timestamp, user_id, action, entity, before, after, hash |
| 21.2 | Hash chaining | Each log.hash = SHA256(prev_hash + current_data) |
| 21.3 | Compliance export | CSV/JSON export with hash verification |
| 21.3 | Tamper detection | API endpoint to verify chain integrity |
| 21.4 | Tests | 10 backend + 5 frontend |

**Files**: `backend/app/models/audit_log.py`, `backend/app/services/audit_trail.py`, `backend/app/api/v1/audit.py`

---

### Day 22: Performance Tuning

**Scope**: Query optimization, Redis caching, bundle splitting

| Task | Description | Acceptance Criteria |
|------|-------------|---------------------|
| 22.1 | Query optimization | EXPLAIN ANALYZE slow queries, add indexes |
| 22.1 | Redis caching | Cache forecast results, valuation, inventory (TTL: 5min) |
| 22.2 | Bundle splitting | Code-split by route, lazy-load heavy components |
| 22.2 | Image optimization | WebP, lazy loading, responsive images |
| 22.3 | Tests | 10 backend + 10 frontend |

**Files**: `backend/app/core/cache.py`, `frontend/vite.config.ts` (manualChunks)

---

### Day 23: Accessibility Audit (WCAG 2.1 AA)

**Scope**: Keyboard nav, screen reader, color contrast, ARIA

| Task | Description | Acceptance Criteria |
|------|-------------|---------------------|
| 23.1 | Keyboard navigation | All interactive elements reachable, focus visible |
| 23.1 | Screen reader | ARIA labels, roles, live regions for dynamic content |
| 23.2 | Color contrast | 4.5:1 normal, 3:1 large text |
| 23.2 | Focus management | Focus trap in modals, skip links |
| 23.3 | Tests | 15 frontend (axe-core, manual) |

**Files**: `frontend/src/hooks/useFocusTrap.ts`, `frontend/src/components/ui/AccessibleModal.tsx`

---

### Day 24: Localization (i18n)

**Scope**: Multi-language (ID/EN), i18n infrastructure

| Task | Description | Acceptance Criteria |
|------|-------------|---------------------|
| 24.1 | i18n infrastructure | react-i18next, locale detection, fallback |
| 24.1 | Translation files | `public/locales/id.json`, `en.json` (500+ keys) |
| 24.2 | Language switcher | Header dropdown, persists in localStorage |
| 24.2 | Date/number formatting | Locale-aware (ID: dd/MM/yyyy, EN: MM/dd/yyyy) |
| 24.3 | Tests | 10 frontend + 5 backend |

**Files**: `frontend/src/i18n/`, `frontend/src/components/ui/LanguageSwitcher.tsx`

---

### Day 25: Plugin Architecture

**Scope**: 3rd party extensions, webhook system, SDK

| Task | Description | Acceptance Criteria |
|------|-------------|---------------------|
| 25.1 | Plugin manifest | `plugin.json`: name, version, permissions, entry points |
| 25.1 | Webhook system | Register URLs, retry with backoff, signature verification |
| 25.2 | SDK/TypeScript types | NPM package `@leuit/sdk` with types |
| 25.2 | Example plugin | `leuit-plugin-whatsapp` (send order notifications) |
| 25.3 | Tests | 10 backend |

**Files**: `backend/app/plugins/`, `backend/app/api/v1/webhooks.py`, `sdk/`

---

### Day 26: Load Testing

**Scope**: 1000+ concurrent users, k6 scripts, bottleneck identification

| Task | Description | Acceptance Criteria |
|------|-------------|---------------------|
| 26.1 | k6 scripts | Scenarios: login, inventory CRUD, sync upload, forecast |
| 26.1 | Baseline metrics | p95 < 200ms, error rate < 0.1% at 1000 VU |
| 26.2 | Bottleneck identification | Profile CPU, memory, DB connections |
| 26.2 | Optimization | Connection pooling, query optimization |
| 26.3 | Tests | 5 backend (k6 integration) |

**Files**: `load-test/k6-scenarios.js`, `load-test/config.yaml`

---

### Day 27: Release Candidate

**Scope**: v1.9.0-rc1 tag, docs, migration guide

| Task | Description | Acceptance Criteria |
|------|-------------|---------------------|
| 27.1 | Version bump | `v1.9.0-rc1` tag, CHANGELOG.md |
| 27.1 | Migration guide | `MIGRATION_v1.8_TO_v1.9.md` |
| 27.2 | Documentation | Updated API docs, component storybook |
| 27.2 | Binary signing | Windows (EV cert), macOS (notarization) |
| 27.3 | Tests | 5 full-stack (E2E Cypress) |

**Files**: `CHANGELOG.md`, `MIGRATION_v1.8_TO_v1.9.md`, `.github/workflows/release.yml`

---

### Day 28: Sprint 2 Review & Retrospective

**Scope**: Sprint 2 report, Sprint 3 planning, retrospective

| Task | Description | Output |
|------|-------------|--------|
| 28.1 | Sprint 2 report | Aggregate daily reports, metrics |
| 28.1 | Sprint 3 planning | Backlog grooming, capacity planning |
| 28.2 | Retrospective | Start/Stop/Continue, action items |
| 28.2 | Celebration | Team demo, celebrate wins! |

**Output**: `IMPLEMENTATION_REPORT_SPRINT_2.md`, Sprint 3 backlog

---

## 🧪 Test Strategy

| Layer | Tool | Coverage Target |
|-------|------|-----------------|
| Unit (Backend) | pytest | > 80% |
| Unit (Frontend) | Vitest | > 80% |
| Integration | pytest + Vitest | Critical paths |
| E2E | Cypress | Critical user journeys |
| Load | k6 | 1000 VU |
| Security | SAST/DAST | Zero critical |

---

## 📦 Definition of Done (per PR)

- [ ] All tests pass (backend + frontend)
- [ ] `ruff check .` / `pnpm lint` = 0 errors
- [ ] `mypy` / `pnpm typecheck` = 0 errors
- [ ] Coverage > 80% on new code
- [ ] No hardcoded secrets
- [ ] Documentation updated
- [ ] CI green
- [ ] PR approved + merged to `staging`

---

## 📅 Sprint 2 Calendar

```
Week 3 (Day 15-21)          Week 4 (Day 22-28)
┌─────────────────────────┬─────────────────────────┐
│ Day 15  Mon  │ Forecast  │ Day 22  Mon  │ Perf    │
│ Day 16  Tue  │ Multi-    │ Day 23  Tue  │ A11y    │
│ Day 17  Wed  │ PWA       │ Day 24  Wed  │ i18n    │
│ Day 18  Thu  │ Analytics │ Day 25  Thu  │ Plugin  │
│ Day 19  Fri  │ Supplier  │ Day 26  Fri  │ Load    │
│ Day 20  Sat  │ Customer  │ Day 27  Sat  │ RC      │
│ Day 20  Sun  │ (buffer)  │ Day 27  Sun  │ (buffer)│
│ Day 21  Mon  │ Audit     │ Day 28  Mon  │ Review  │
└─────────────────────────┴─────────────────────────┘
```

---

## 📋 Definition of Ready (per task)

- [ ] Task broken down to < 4 hours
- [ ] Acceptance criteria clear
- [ ] Dependencies identified
- [ ] Test approach defined
- [ ] No blocking dependencies

## 📋 Definition of Done (per PR)

- [ ] All tests pass (backend + frontend)
- [ ] `ruff check .` / `pnpm lint` = 0 errors
- [ ] `mypy` / `pnpm typecheck` = 0 errors
- [ ] Coverage > 80% on new code
- [ ] No hardcoded secrets
- [ ] Documentation updated
- [ ] CI green
- [ ] PR approved + merged to `staging`

---

## 🚀 Sprint 2 Success Criteria

- [ ] All 14 days complete
- [ ] 14 PRs merged to `staging`
- [ ] 200+ new tests added
- [ ] All quality gates passing
- [ ] Sprint 2 report generated
- [ ] Sprint 3 backlog ready
- [ ] v1.9.0-rc1 tagged

---

*Plan created: 2026-10-01*  
*Based on: RELEASE_REPORT.md Sprint 1 completion*  
*Next: Sprint 2 execution starts Day 15*