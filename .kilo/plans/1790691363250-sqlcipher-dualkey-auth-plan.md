# Plan: Hari 2 — Backend: SQLCipher + Dual-Key Auth

> **Scope:** `backend/app/core/security/`, `backend/app/core/database.py`, `backend/app/api/v1/auth_security.py`, `backend/app/api/v1/deps.py`, `backend/app/models/security.py`, `backend/app/main.py`
> **Status:** Code exists tapi punya security hole & missing pieces. Plan ini fix + harden + tambah missing flow.

---

## Audit Findings (Issue yang harus di-fix)

### CRITICAL
| # | File | Issue | Impact |
|---|------|-------|--------|
| C1 | `database.py:47` | `PRAGMA key = '{encryption_key}'` pakai f-string → **SQL injection via PRAGMA** | Bisa bypass enkripsi |
| C2 | `auth_security.py:52` | Dev master key hardcoded `sha256(b"LEUIT_DEV_MASTER_2024")` → bisa di-reverse dari source | Developer recovery tanpa signing |
| C3 | `main.py` | **Tidak ada DB init flow** — app start tanpa inisialisasi keyring/envelope | First-run tidak bisa unlock |
| C4 | `deps.py` | `verify_license()` dipanggil di semua protected routes tapi **DB belum tentu initialized** | Crash saat DB locked |

### HIGH
| # | File | Issue |
|---|------|-------|
| H1 | `database.py:47` | `init_database()` panggil `Base.metadata.create_all()` tanpa cek apakah DB sudah exist → create tables on locked DB bisa corrupt |
| H2 | `auth_security.py` | Tidak ada audit log untuk failed unlock attempts (brute force protection) |
| H3 | `auth_security.py:49-62` | Developer mode bypass SealedBox, pakai hardcoded hash → developer envelope (`encrypted_dek_developer`) never actually used |
| H4 | `key_envelope.py:134` | `derive_sqlcipher_key()` cuma return `dek.hex()` — tidak ada actual PBKDF2 derivation untuk SQLCipher |
| H5 | No middleware | Endpoint lain bisa diakses tanpa DB unlock |

### MEDIUM
| # | File | Issue |
|---|------|-------|
| M1 | `database.py:44-48` | PRAGMA `cipher_compatibility=4`, `kdf_iter=256000` — tapi SQLCipher 4 default sudah 256000, redundant |
| M2 | `config.py` | `CLOUD_PUBLIC_KEY_HEX` punya default value di code → public key hardcoded di source |
| M3 | `auth_schema.py:7` | `passkey: str` min_length=4 terlalu pendek untuk PIN |
| M4 | `licensing.py:99-103` | `check_monotonic_clock()` commit di dalam `verify_license_token()` → bisa leave open transaction |
| M5 | No rate limiting | `/auth/unlock` tanpa rate limiting → brute force |

---

## Implementation Tasks (Ordered)

### Task 1: Fix SQL Injection di PRAGMA key
**File:** `backend/app/core/database.py`

- `init_database()` dan `verify_database_key()`: ganti f-string PRAGMA key dengan parameterized approach
- SQLCipher pysqlcipher driver tidak support bind params untuk PRAGMA → pakai `dbapi_connection.executescript()` atau escape key via double-quote wrapping
- **Approach:** Buat helper `_escape_pragma_key(key: str) -> str` yang escape single quotes

```python
def _escape_pragma_key(key: str) -> str:
    """Escape key for safe PRAGMA execution."""
    return key.replace("'", "''")
```

- Apply di `set_pragma_key` event listener dan `verify_database_key`

### Task 2: First-Run Initialization Flow
**File:** `backend/app/api/v1/auth_security.py` (tambah endpoint baru)
**File:** `backend/app/schemas/auth_schema.py` (tambah schema)
**File:** `backend/app/api/v1/deps.py` (tambah `get_db_or_init`)

Tambah endpoint: `POST /api/v1/auth/initialize`

Flow:
1. Cek apakah `security_keyring` row ada di DB
2. Jika belum ada (first run):
   - Generate DEK baru via `KeyEnvelope.generate_dek()`
   - Minta owner passkey dari request
   - Load dev public key dari `dev_public_key.hex` (via settings)
   - `KeyEnvelope.create_envelope(dek, passkey, dev_public_key)` → simpan ke SecurityKeyring
   - `init_database(derive_sqlcipher_key(dek))` → buka DB
   - Sign & save license via `generate_license.py` flow
3. Jika sudah ada → redirect ke `/auth/unlock`

Schema:
```python
class InitializeRequest(BaseModel):
    owner_passkey: str = Field(..., min_length=6)
    license_id: str = "DEV-LOCAL-001"
```

### Task 3: Fix Developer Recovery via SealedBox
**File:** `backend/app/api/v1/auth_security.py`

- Ganti hardcoded hash dengan actual SealedBox decryption
- Load `dev_private_key.hex` saat developer mode
- `KeyEnvelope.open_envelope_developer(keyring, PrivateKey)` → DEK
- Private key hanya di-load dari file (bukan di-hardcode)

```python
if is_developer:
    private_key_bytes = bytes.fromhex(settings.DEV_PRIVATE_KEY_HEX)
    dev_private_key = PrivateKey(private_key_bytes)
    dek = KeyEnvelope.open_envelope_developer(
        {"encrypted_dek_developer": keyring.encrypted_dek_developer},
        dev_private_key
    )
```

**Config tambahan:** `DEV_PRIVATE_KEY_HEX` di `settings` (load dari env, jangan di-hardcode)

### Task 4: Audit Log untuk Unlock Attempts
**File:** `backend/app/models/security.py` (tambah model)
**File:** `backend/app/api/v1/auth_security.py` (tambah logging)

Tambah model:
```python
class SecurityUnlockAudit(Base):
    __tablename__ = "security_unlock_audit"
    id = Column(Integer, primary_key=True)
    attempted_at = Column(DateTime, server_default=func.now())
    role = Column(String(20))  # OWNER / DEVELOPER
    success = Column(Integer, default=0)  # 0=fail, 1=success
    ip_address = Column(String(45), nullable=True)
    failure_reason = Column(Text, nullable=True)
```

Log setiap attempt (success & fail) di `unlock_database()`.

### Task 5: DB Lock Guard Middleware
**File:** `backend/app/main.py`

Tambah middleware yang cek apakah DB sudah initialized sebelum proses request ke protected routes:

```python
@app.middleware("http")
async def db_lock_guard(request: Request, call_next):
    protected_prefixes = ["/api/v1/inventory", "/api/v1/bom", "/api/v1/purchases", "/api/v1/sync", "/api/v1/forecast"]
    if any(request.url.path.startswith(p) for p in protected_prefixes):
        from app.core.database import _engine
        if _engine is None:
            return JSONResponse(
                status_code=423,
                content={"detail": "Database terkunci. Silakan unlock terlebih dahulu."}
            )
    return await call_next(request)
```

### Task 6: Fix deps.py License Guard
**File:** `backend/app/api/v1/deps.py`

- `verify_license()` harus cek `_engine is None` → jika DB locked, return 423 bukan 401
- Pisahkan logic: license file check ≠ DB unlock check
- Tambah dependency `require_db_unlocked()` yang cek `_engine is not None`

### Task 7: Config Cleanup
**File:** `backend/app/core/config.py`

- Hapus default value `CLOUD_PUBLIC_KEY_HEX` → jadikan required (empty string = raise error saat startup)
- Tambah `DEV_PRIVATE_KEY_HEX: str = ""` (load dari env)
- Tambah `LICENSE_INIT_VALID_DAYS: int = 365`

### Task 8: Hardening database.py
**File:** `backend/app/core/database.py`

- `init_database()`: tambah guard — jika `_engine is not None`, dispose engine lama dulu
- `verify_database_key()`: tambah `PRAGMA quick_check` setelah `SELECT 1`
- `change_encryption_key()`: tambah validasi old_key ≠ new_key
- `backup_database()`: jangan re-init engine, pakai existing engine

### Task 9: Rate Limiting (Lightweight)
**File:** `backend/app/api/v1/auth_security.py`

Implementasi in-memory rate limiter tanpa dependency tambahan:
- Track failed attempts per IP dalam dict `{ip: (count, first_attempt_time)}`
- Max 5 attempts per 15 menit
- Return 429 Too Many Requests jika exceeded

```python
from collections import defaultdict
import time

_unlock_attempts: dict[str, list[float]] = defaultdict(list)
MAX_ATTEMPTS = 5
WINDOW_SECONDS = 900

def _check_rate_limit(ip: str) -> bool:
    now = time.time()
    _unlock_attempts[ip] = [t for t in _unlock_attempts[ip] if now - t < WINDOW_SECONDS]
    if len(_unlock_attempts[ip]) >= MAX_ATTEMPTS:
        return False
    _unlock_attempts[ip].append(now)
    return True
```

### Task 10: Expand Test Coverage
**File:** `backend/tests/test_smoke.py` → split ke multiple test files

Tambah test files:
- `tests/test_security.py` — test KeyEnvelope round-trip, hardware fingerprint, license verify
- `tests/test_database.py` — test init, verify, rekey, escape PRAGMA key
- `tests/test_auth_api.py` — test unlock endpoint (mock DB), rate limiting, 423 when locked

---

## File Changes Summary

| File | Action | Tasks |
|------|--------|-------|
| `app/core/database.py` | Edit | T1, T8 |
| `app/core/config.py` | Edit | T7 |
| `app/api/v1/auth_security.py` | Edit | T2, T3, T4, T9 |
| `app/api/v1/deps.py` | Edit | T6 |
| `app/schemas/auth_schema.py` | Edit | T2 |
| `app/models/security.py` | Edit | T4 |
| `app/models/__init__.py` | Edit | T4 |
| `app/main.py` | Edit | T5 |
| `tests/test_security.py` | Create | T10 |
| `tests/test_database.py` | Create | T10 |
| `tests/test_auth_api.py` | Create | T10 |

---

## Execution Order

1. **T1** (PRAGMA injection fix) — paling kritis, zero risk
2. **T7** (Config cleanup) — prerequisite untuk T3
3. **T8** (DB hardening) — prerequisite untuk T2
4. **T2** (First-run init flow) — core feature missing
5. **T3** (Fix developer recovery) — security hole
6. **T4** (Audit log) — audit trail
7. **T5** (Lock guard middleware) — defense in depth
8. **T6** (deps.py fix) — consistency
9. **T9** (Rate limiting) — brute force protection
10. **T10** (Tests) — validation

---

## Validation

- `uv run ruff check .` — 0 errors
- `uv run pytest tests/ -v` — all pass
- Manual test: start app → first run → initialize → unlock → access protected endpoint
- Manual test: wrong passkey → audit log recorded → 5 fails → rate limited

---

## Open Questions

1. **DEV_PRIVATE_KEY_HEX** — simpan di `.env` saja atau perlu encrypted storage? → Rekomendasi: `.env` + `.gitignore` (sudah ada)
2. **License server** — flow init generate license lokal dulu, nanti ganti ke cloud endpoint? → Ya, mock lokal untuk dev
