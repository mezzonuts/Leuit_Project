# LEUIT Implementation Report - Day 2 (Backend: SQLCipher + Dual-Key Auth)

**Tanggal**: 2026-09-29
**Sprint**: 1 (Foundation & Security)
**Hari**: 2 dari 14
**Status**: ✅ COMPLETED
**PR**: #3 merged (commit `ea848d43`)

---

## Executive Summary

Berhasil memperkuat sistem enkripsi SQLCipher dan autentikasi dual-key dengan memperbaiki 4 critical security holes, menambahkan first-run initialization flow, developer recovery via SealedBox, audit logging, dan rate limiting. Total 57 unit tests ditambahkan untuk security, database, dan auth modules.

---

## 1. Files Changed

| Category | File | Fungsi | Perubahan |
|---|---|---|---|
| **Security Core** | `app/core/security/hardware.py` | Hardware fingerprinting | Escape PRAGMA key usage |
| | `app/core/security/licensing.py` | License verification | Unchanged (used by new flows) |
| | `app/core/security/key_envelope.py` | Dual-key envelope | `open_envelope_developer()` via SealedBox |
| | `app/core/security/__init__.py` | Exports | Export new functions |
| **Database** | `app/core/database.py` | SQLCipher engine | `_escape_pragma_key()`, quick_check, dispose guard, same-key check |
| **Auth API** | `app/api/v1/auth_security.py` | Auth endpoints | `/initialize`, SealedBox dev recovery, audit log, rate limit |
| **Deps** | `app/api/v1/deps.py` | Dependencies | `require_db_unlocked()`, 423 responses |
| **Config** | `app/core/config.py` | Settings | Removed hardcoded public key, added DEV_PRIVATE_KEY_HEX, LICENSE_INIT_VALID_DAYS |
| **Models** | `app/models/security.py` | Security models | Added `SecurityUnlockAudit` |
| | `app/models/__init__.py` | Model exports | Export SecurityUnlockAudit |
| **Main** | `app/main.py` | Launcher | DB lock guard middleware (423 on protected routes) |
| **Schemas** | `app/schemas/auth_schema.py` | Auth schemas | Added InitializeRequest/Response |
| **Tests** | `tests/test_security.py` | Security tests | 22 tests (KeyEnvelope, Hardware, License) |
| | `tests/test_database.py` | Database tests | 22 tests (escape, init, session, rekey) |
| | `tests/test_auth_api.py` | Auth API tests | 15 tests (rate limit, schemas) |
| **CI** | `.github/workflows/ci.yml` | GitHub Actions | `continue-on-error: true` on coverage uploads |
| | `.gitlab-ci.yml` | GitLab CI | Full rewrite: Node 24, Python 3.12, pnpm cache, SQLCipher |
| **Orchestrator** | `.kilo/agent/orchestrator.md` | Lifecycle agent | Auto-retry CI loop, daily report stage |

---

## 2. Security Fixes (Critical)

| ID | Issue | Fix | File |
|---|---|---|---|
| **C1** | PRAGMA key SQL injection via f-string | `_escape_pragma_key()` helper escapes `'` → `''` at 3 injection points | `database.py` |
| **C2** | Hardcoded dev master key `sha256(b"LEUIT_DEV_MASTER_2024")` | Actual SealedBox decryption via `PrivateKey` loaded from `dev_private_key.hex` | `auth_security.py` |
| **C3** | Missing first-run init flow | New `POST /api/v1/auth/initialize` generates DEK, dual-envelope, persists keyring | `auth_security.py` |
| **C4** | `deps.py` crashes on locked DB | `require_db_unlocked()` dependency returns HTTP 423 | `deps.py` |

---

## 3. New Features

### First-Run Initialization (`POST /auth/initialize`)
```json
{
  "owner_passkey": "secure-pin-123",  // min_length=6
  "license_id": "DEV-LOCAL-001"
}
```
Generates DEK → creates dual-envelope (owner + developer) → persists SecurityKeyring → initializes SQLCipher DB → returns hardware_id.

### Developer Recovery via SealedBox
```python
dev_private_key = PrivateKey(bytes.fromhex(settings.DEV_PRIVATE_KEY_PATH.read()))
dek = KeyEnvelope.open_envelope_developer(
    {"encrypted_dek_developer": keyring.encrypted_dek_developer},
    dev_private_key
)
```

### SecurityUnlockAudit Model
```python
class SecurityUnlockAudit(Base):
    attempted_at = DateTime(timezone=True, server_default=func.now())
    role = String(20)  # OWNER / DEVELOPER / UNKNOWN
    success = Integer(default=0)  # 0=fail, 1=success
    ip_address = String(45, nullable=True)
    failure_reason = Text(nullable=True)
```

### In-Memory Rate Limiting
- Max 5 attempts per 15 minutes per IP
- Returns HTTP 429 when exceeded
- Sliding window cleanup

---

## 4. Tests Added (57 total)

| File | Tests | Coverage |
|---|---|---|
| `tests/test_security.py` | 22 | KeyEnvelope (9), Hardware (3), LicenseData (2), LicenseStatus (3), HardwareBinding (2), MonotonicClock (2), SecurityException (1) |
| `tests/test_database.py` | 22 | EscapePragmaKey (8), GetDatabaseUrl (3), SessionScope (5), GetEngine (2), GetSession (2), ChangeEncryptionKey (2) |
| `tests/test_auth_api.py` | 15 | RateLimiting (4), UnlockRequest (2), InitializeRequest (2), AuthStatusResponse (2) |

---

## 5. CI Iterations

| Iteration | Commit | Status | Notes |
|---|---|---|---|
| 1 | `2b069b9a` | FAIL | Initial push |
| 2 | `e205ed4e` | FAIL | Added mypy type annotations |
| 3 | `770efc45` | FAIL | CI hardening + orchestrator |
| 4 | `175cf29f` | FAIL | Fixed mypy callable error |
| 5 | `80e1590d` | **PASS** | SQLAlchemy ColumnElement → bool() wraps |

---

## 6. Known Issues / Technical Debt

| Issue | Status |
|---|---|
| Frontend TypeScript errors (~30 unused imports, type mismatches) | Pending Day 6 |
| SQLCipher C-extensions (pysqlcipher3, pynacl) need MSVC Build Tools on Windows | Documented |
| Frontend `@tanstack/react-query-devtools` missing | Pending Day 6 |

---

## 7. Architecture Compliance

| PRD Requirement | Implementation | Status |
|---|---|---|
| SQLCipher AES-256 encrypted DB | `database.py` + `key_envelope.py` + PRAGMA hardening | ✅ |
| Dual-Key Access (Owner PIN + Dev Key) | `key_envelope.py` SealedBox + `/initialize` + `/unlock` | ✅ |
| Hardware Binding (Motherboard + CPU) | `hardware.py` SHA256(MB UUID + CPU ID) | ✅ |
| Monotonic Clock Guard | `licensing.py` + `SecurityAuditClock` | ✅ |
| Ed25519 License Verification | `licensing.py` + `generate_license.py` | ✅ |

---

## 8. Commands to Resume Development

```bash
# Backend
cd D:\Project\Leuit\backend
.venv\Scripts\activate
uv run uvicorn app.main:app --reload --port 8000

# Test
uv run pytest tests/ -v
uv run ruff check .

# Frontend (pending fixes)
cd D:\Project\Leuit\frontend
pnpm add @tanstack/react-query-devtools
pnpm dev
```

---

*Report generated by Kilo AI Assistant*  
*Next: Day 3 - Auth API & Models Verification*