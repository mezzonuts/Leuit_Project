from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator, Optional
import os

from app.core.config import settings

# Base class for models
class Base(DeclarativeBase):
    pass

# Global engine variable (initialized after unlock)
_engine = None
_SessionLocal = None

def get_database_url(encryption_key: str) -> str:
    """Generate SQLite connection URL with SQLCipher encryption."""
    # For SQLCipher with pysqlcipher3, we use the file path and set PRAGMA key after connection
    db_path = settings.DATABASE_PATH
    return f"sqlite+pysqlcipher:///{db_path}"

def init_database(encryption_key: str) -> None:
    """Initialize database engine with encryption key."""
    global _engine, _SessionLocal

    database_url = get_database_url(encryption_key)

    _engine = create_engine(
        database_url,
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,
            "timeout": 30,
        },
        echo=settings.DEBUG,
    )

    # Set encryption key on connect
    @event.listens_for(_engine, "connect")
    def set_pragma_key(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute(f"PRAGMA key = '{encryption_key}';")
        cursor.execute("PRAGMA cipher_compatibility = 4;")
        cursor.execute("PRAGMA cipher_page_size = 4096;")
        cursor.execute("PRAGMA kdf_iter = 256000;")
        cursor.close()

    # Enable foreign keys
    @event.listens_for(_engine, "connect")
    def set_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.close()

    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

    # Create tables
    Base.metadata.create_all(bind=_engine)

def get_engine():
    """Get the current engine instance."""
    if _engine is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _engine

def get_session() -> Generator[Session, None, None]:
    """Dependency for FastAPI to get DB session."""
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")

    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Context manager for database sessions outside FastAPI."""
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")

    db = _SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def verify_database_key(encryption_key: str) -> bool:
    """Verify if the encryption key can open the database."""
    try:
        test_engine = create_engine(
            f"sqlite+pysqlcipher:///{settings.DATABASE_PATH}",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )

        @event.listens_for(test_engine, "connect")
        def set_test_key(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute(f"PRAGMA key = '{encryption_key}';")
            cursor.execute("PRAGMA cipher_compatibility = 4;")
            cursor.close()

        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1;"))

        test_engine.dispose()
        return True
    except Exception:
        return False

def change_encryption_key(old_key: str, new_key: str) -> bool:
    """Change database encryption key (rekey)."""
    try:
        # Initialize with old key first
        init_database(old_key)

        with session_scope() as db:
            db.execute(text(f"PRAGMA rekey = '{new_key}';"))

        # Re-initialize with new key
        init_database(new_key)
        return True
    except Exception:
        return False

def backup_database(backup_path: str, encryption_key: str) -> bool:
    """Create encrypted backup of database."""
    try:
        init_database(encryption_key)

        with session_scope() as db:
            db.execute(text(f"BACKUP TO '{backup_path}';"))

        return True
    except Exception:
        return False