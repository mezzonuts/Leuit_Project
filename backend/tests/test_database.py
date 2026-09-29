"""Unit tests database module: escape, URL generation, session management."""

import sys
import types
from unittest.mock import MagicMock, patch

# Stub heavy security deps before any app.core import
_stubbed = {}
for mod_name in [
    "nacl", "nacl.signing", "nacl.exceptions",
    "app.core.security", "app.core.security.licensing",
    "app.core.security.hardware", "app.core.security.key_envelope",
]:
    if mod_name not in sys.modules:
        stub = types.ModuleType(mod_name)
        stub.__dict__.setdefault("SecurityException", type("SecurityException", (Exception,), {}))
        stub.__dict__.setdefault("LicenseData", MagicMock)
        sys.modules[mod_name] = stub
        _stubbed[mod_name] = stub

import pytest  # noqa: E402

from app.core import database as db_mod  # noqa: E402
from app.core.database import (  # noqa: E402
    _escape_pragma_key,
    change_encryption_key,
    get_database_url,
    get_engine,
    get_session,
    session_scope,
)

# Restore original sys.modules so other test files (e.g. test_security.py) can import the real packages
for _name, _stub in _stubbed.items():
    sys.modules.pop(_name, None)


class TestEscapePragmaKey:
    def test_plain_key_unchanged(self):
        assert _escape_pragma_key("simple-key-123") == "simple-key-123"

    def test_single_quotes_escaped(self):
        assert _escape_pragma_key("key'with'quotes") == "key''with''quotes"

    def test_empty_string(self):
        assert _escape_pragma_key("") == ""

    def test_hex_key(self):
        hex_key = "abcdef0123456789"
        assert _escape_pragma_key(hex_key) == hex_key

    def test_key_with_single_quote_at_start(self):
        assert _escape_pragma_key("'start") == "''start"

    def test_key_with_single_quote_at_end(self):
        assert _escape_pragma_key("end'") == "end''"

    def test_multiple_consecutive_quotes(self):
        assert _escape_pragma_key("a''b") == "a''''b"

    def test_only_quotes(self):
        assert _escape_pragma_key("''") == "''''"


class TestGetDatabaseUrl:
    def test_returns_sqlite_url(self):
        with patch.object(db_mod.settings, "DATABASE_PATH", "/tmp/test.db"):
            url = get_database_url("test-key")
            assert url == "sqlite+pysqlcipher:////tmp/test.db"

    def test_ignores_encryption_key_in_url(self):
        with patch.object(db_mod.settings, "DATABASE_PATH", "/tmp/test.db"):
            url = get_database_url("any-key")
            assert "pysqlcipher" in url

    def test_uses_settings_database_path(self):
        with patch.object(db_mod.settings, "DATABASE_PATH", "/custom/path/db.sqlite"):
            url = get_database_url("key")
            assert "/custom/path/db.sqlite" in url


class TestSessionScope:
    def test_raises_when_not_initialized(self):
        db_mod._SessionLocal = None
        with pytest.raises(RuntimeError, match="Database not initialized"):
            with session_scope():
                pass

    def test_calls_rollback_on_exception(self):
        mock_session = MagicMock()
        db_mod._SessionLocal = MagicMock(return_value=mock_session)

        with pytest.raises(ValueError):
            with session_scope():
                raise ValueError("test error")

        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
        mock_session.commit.assert_not_called()

    def test_calls_commit_on_success(self):
        mock_session = MagicMock()
        db_mod._SessionLocal = MagicMock(return_value=mock_session)

        with session_scope():
            pass

        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
        mock_session.rollback.assert_not_called()

    def test_always_closes_session(self):
        mock_session = MagicMock()
        db_mod._SessionLocal = MagicMock(return_value=mock_session)

        with session_scope():
            pass

        mock_session.close.assert_called_once()

    def test_yields_session_instance(self):
        mock_session = MagicMock()
        db_mod._SessionLocal = MagicMock(return_value=mock_session)

        with session_scope() as sess:
            assert sess is mock_session


class TestGetEngine:
    def test_raises_when_not_initialized(self):
        db_mod._engine = None
        with pytest.raises(RuntimeError, match="Database not initialized"):
            get_engine()

    def test_returns_engine_when_set(self):
        mock_engine = MagicMock()
        db_mod._engine = mock_engine
        assert get_engine() is mock_engine
        db_mod._engine = None


class TestGetSession:
    def test_raises_when_not_initialized(self):
        db_mod._SessionLocal = None
        gen = get_session()
        with pytest.raises(RuntimeError, match="Database not initialized"):
            next(gen)

    def test_yields_and_closes_session(self):
        mock_session = MagicMock()
        db_mod._SessionLocal = MagicMock(return_value=mock_session)

        gen = get_session()
        session = next(gen)

        assert session is mock_session

        with pytest.raises(StopIteration):
            next(gen)

        mock_session.close.assert_called_once()
        db_mod._SessionLocal = None


class TestChangeEncryptionKey:
    def test_returns_false_when_same_key(self):
        assert change_encryption_key("same-key", "same-key") is False

    def test_returns_false_on_exception(self):
        with patch.object(db_mod, "init_database", side_effect=Exception("fail")):
            assert change_encryption_key("old", "new") is False
