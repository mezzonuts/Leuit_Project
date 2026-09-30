import enum
from datetime import UTC

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class PaymentMethod(enum.StrEnum):
    CASH = "CASH"
    CREDIT = "CREDIT"

class PaymentStatus(enum.StrEnum):
    PAID = "PAID"
    UNPAID = "UNPAID"

class InventoryPurchase(Base):
    __tablename__ = "inventory_purchases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    purchase_date = Column(DateTime(timezone=True), nullable=False, index=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id", ondelete="RESTRICT"), nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="RESTRICT"), nullable=False, index=True)
    quantity = Column(Numeric(15, 3), nullable=False)
    total_cost = Column(Numeric(15, 2), nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False, default=PaymentMethod.CASH)
    payment_status = Column(SQLEnum(PaymentStatus), nullable=False, default=PaymentStatus.PAID)
    due_date = Column(DateTime(timezone=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    ingredient = relationship("Ingredient", back_populates="purchases")
    supplier = relationship("Supplier", back_populates="purchases")

    # Indexes
    __table_args__ = (
        Index("ix_purchases_date_status", "purchase_date", "payment_status"),
        Index("ix_purchases_due_date_status", "due_date", "payment_status"),
    )

    def __repr__(self) -> str:
        return f"<InventoryPurchase(id={self.id}, ingredient={self.ingredient_id}, cost={self.total_cost})>"

    @property
    def is_overdue(self) -> bool:
        if self.payment_status == PaymentStatus.UNPAID and self.due_date:
            from datetime import datetime
            return bool(datetime.now(UTC) > self.due_date)
        return False

    @property
    def days_until_due(self) -> int:
        if self.due_date and self.payment_status == PaymentStatus.UNPAID:
            from datetime import datetime
            delta = self.due_date - datetime.now(UTC)
            return max(0, delta.days)
        return 0

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "purchase_date": self.purchase_date.isoformat() if self.purchase_date else None,
            "ingredient_id": self.ingredient_id,
            "ingredient_name": self.ingredient.name if self.ingredient else None,
            "supplier_id": self.supplier_id,
            "supplier_name": self.supplier.name if self.supplier else None,
            "quantity": float(self.quantity),
            "total_cost": float(self.total_cost),
            "payment_method": self.payment_method.value,
            "payment_status": self.payment_status.value,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "is_overdue": self.is_overdue,
            "days_until_due": self.days_until_due,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class OperationalAuditLog(Base):
    __tablename__ = "operational_audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action_type = Column(String(50), nullable=False, index=True)  # STOCK_OPNAME, RECIPE_EDIT, PURCHASE_PAID, etc.
    entity_name = Column(String(255), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    actor_role = Column(String(20), nullable=False)  # OWNER, OPERATOR

    # Indexes
    __table_args__ = (
        Index("ix_audit_timestamp_role", "timestamp", "actor_role"),
        Index("ix_audit_action_entity", "action_type", "entity_name"),
    )

    def __repr__(self) -> str:
        return f"<OperationalAuditLog(action={self.action_type}, entity={self.entity_name})>"

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "action_type": self.action_type,
            "entity_name": self.entity_name,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "actor_role": self.actor_role,
        }