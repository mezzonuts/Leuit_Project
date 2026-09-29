from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.core.database import Base


class SecurityKeyring(Base):
    __tablename__ = "security_keyring"

    id = Column(Integer, primary_key=True, autoincrement=True)
    encrypted_dek_owner = Column(Text, nullable=False)  # DEK encrypted with Owner's passkey
    encrypted_dek_developer = Column(Text, nullable=False)  # DEK encrypted with Developer's public key
    last_key_rotation = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<SecurityKeyring(rotation={self.last_key_rotation})>"

class SecurityAuditClock(Base):
    __tablename__ = "security_audit_clock"

    id = Column(Integer, primary_key=True, autoincrement=True)
    last_seen_timestamp = Column(Integer, nullable=False)  # Unix timestamp
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<SecurityAuditClock(ts={self.last_seen_timestamp})>"

class AppLicense(Base):
    __tablename__ = "app_license"

    id = Column(Integer, primary_key=True, autoincrement=True)
    license_key = Column(Text, nullable=False)
    valid_until = Column(DateTime(timezone=True), nullable=False)
    last_verified_at = Column(DateTime(timezone=True), nullable=False)
    grace_period_end = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<AppLicense(valid_until={self.valid_until})>"

class SecurityUnlockAudit(Base):
    """Audit log for database unlock attempts (success and failure)."""
    __tablename__ = "security_unlock_audit"
    id = Column(Integer, primary_key=True, autoincrement=True)
    attempted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    role = Column(String(20), nullable=False)  # OWNER / DEVELOPER / UNKNOWN
    success = Column(Integer, default=0, nullable=False)  # 0=fail, 1=success
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    failure_reason = Column(Text, nullable=True)

    def __repr__(self):
        return f"<SecurityUnlockAudit(role={self.role}, success={self.success})>"