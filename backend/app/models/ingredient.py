from sqlalchemy import Boolean, Column, DateTime, Index, Integer, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    barcode_sku = Column(String(100), unique=True, nullable=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    unit = Column(String(20), nullable=False)  # ml, gram, pcs
    cost_per_unit = Column(Numeric(15, 2), nullable=False)  # HPP per unit
    shelf_life_days = Column(Integer, nullable=False)
    current_stock = Column(Numeric(15, 3), default=0, nullable=False)
    min_stock_threshold = Column(Numeric(15, 3), default=0, nullable=False)
    lead_time_days = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    outlet_id = Column(Integer, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    recipes = relationship("RecipeItem", back_populates="ingredient", cascade="all, delete-orphan")
    purchases = relationship("InventoryPurchase", back_populates="ingredient")
    daily_usage = relationship("IngredientDailyUsage", back_populates="ingredient")

    # Indexes
    __table_args__ = (
        Index("ix_ingredients_active_name", "is_active", "name"),
        Index("ix_ingredients_stock_threshold", "current_stock", "min_stock_threshold"),
    )

    def __repr__(self) -> str:
        return f"<Ingredient(id={self.id}, name='{self.name}', stock={self.current_stock})>"

    @property
    def stock_ratio(self) -> float:
        """Calculate stock ratio as percentage of threshold."""
        if self.min_stock_threshold <= 0:
            return 100.0
        return round((float(self.current_stock) / float(self.min_stock_threshold)) * 100, 1)

    @property
    def stock_status(self) -> str:
        """Get stock status: safe, warning, danger."""
        ratio = self.stock_ratio
        if ratio >= 150:
            return "safe"
        elif ratio >= 100:
            return "warning"
        return "danger"

    @property
    def valuation(self) -> float:
        """Total monetary value of current stock."""
        return round(float(self.current_stock) * float(self.cost_per_unit), 2)

    @property
    def days_until_expiry(self) -> int:
        """Estimated days until expiry (simplified)."""
        return int(self.shelf_life_days)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "barcode_sku": self.barcode_sku,
            "name": self.name,
            "unit": self.unit,
            "cost_per_unit": float(self.cost_per_unit),
            "shelf_life_days": self.shelf_life_days,
            "current_stock": float(self.current_stock),
            "min_stock_threshold": float(self.min_stock_threshold),
            "lead_time_days": self.lead_time_days,
            "is_active": self.is_active,
            "stock_ratio": self.stock_ratio,
            "stock_status": self.stock_status,
            "valuation": self.valuation,
            "days_until_expiry": self.days_until_expiry,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }