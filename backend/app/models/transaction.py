from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class SalesTransaction(Base):
    __tablename__ = "sales_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_hash = Column(String(64), unique=True, nullable=False, index=True)  # SHA256
    pos_reference_id = Column(String(100), nullable=True, index=True)  # Original POS transaction ID
    menu_item_id = Column(Integer, ForeignKey("menu_items.id", ondelete="SET NULL"), nullable=True, index=True)
    quantity = Column(Integer, nullable=False)
    transaction_time = Column(DateTime(timezone=True), nullable=False, index=True)
    sync_log_id = Column(Integer, ForeignKey("pos_sync_logs.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    menu_item = relationship("MenuItem", back_populates="sales")
    sync_log = relationship("PosSyncLog", back_populates="transactions")

    # Indexes
    __table_args__ = (
        Index("ix_sales_transaction_time_menu", "transaction_time", "menu_item_id"),
        Index("ix_sales_sync_log_time", "sync_log_id", "transaction_time"),
    )

    def __repr__(self):
        return f"<SalesTransaction(hash={self.transaction_hash[:8]}..., qty={self.quantity})>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "transaction_hash": self.transaction_hash,
            "pos_reference_id": self.pos_reference_id,
            "menu_item_id": self.menu_item_id,
            "menu_item_name": self.menu_item.name if self.menu_item else None,
            "quantity": self.quantity,
            "transaction_time": self.transaction_time.isoformat() if self.transaction_time else None,
            "sync_log_id": self.sync_log_id,
        }

class PosSyncLog(Base):
    __tablename__ = "pos_sync_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String(255), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    total_rows_read = Column(Integer, nullable=False)
    new_rows_inserted = Column(Integer, nullable=False)
    duplicate_rows_skipped = Column(Integer, nullable=False)
    date_range_start = Column(DateTime(timezone=True), nullable=True)
    date_range_end = Column(DateTime(timezone=True), nullable=True)
    reconciled_stock_items = Column(Integer, default=0, nullable=False)

    # Relationships
    transactions = relationship("SalesTransaction", back_populates="sync_log")

    def __repr__(self):
        return f"<PosSyncLog(id={self.id}, file='{self.file_name}', new={self.new_rows_inserted})>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "file_name": self.file_name,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "total_rows_read": self.total_rows_read,
            "new_rows_inserted": self.new_rows_inserted,
            "duplicate_rows_skipped": self.duplicate_rows_skipped,
            "date_range_start": self.date_range_start.isoformat() if self.date_range_start else None,
            "date_range_end": self.date_range_end.isoformat() if self.date_range_end else None,
            "reconciled_stock_items": self.reconciled_stock_items,
        }

class IngredientDailyUsage(Base):
    __tablename__ = "ingredient_daily_usage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usage_date = Column(DateTime(timezone=True), nullable=False, index=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False, index=True)
    total_quantity_used = Column(Numeric(15, 3), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    ingredient = relationship("Ingredient", back_populates="daily_usage")

    # Unique constraint: one record per ingredient per day
    __table_args__ = (
        UniqueConstraint("usage_date", "ingredient_id", name="uq_daily_usage_ingredient"),
        Index("ix_daily_usage_date_ingredient", "usage_date", "ingredient_id"),
    )

    def __repr__(self):
        return f"<IngredientDailyUsage(ingredient={self.ingredient_id}, date={self.usage_date}, qty={self.total_quantity_used})>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "usage_date": self.usage_date.isoformat() if self.usage_date else None,
            "ingredient_id": self.ingredient_id,
            "ingredient_name": self.ingredient.name if self.ingredient else None,
            "total_quantity_used": float(self.total_quantity_used),
        }