from sqlalchemy import (
    Boolean,
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


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pos_item_id = Column(String(100), unique=True, nullable=True, index=True)  # ID from POS system
    name = Column(String(255), nullable=False, index=True)
    sale_price = Column(Numeric(15, 2), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    recipes = relationship("RecipeItem", back_populates="menu_item", cascade="all, delete-orphan")
    sales = relationship("SalesTransaction", back_populates="menu_item")

    def __repr__(self) -> str:
        return f"<MenuItem(id={self.id}, name='{self.name}', price={self.sale_price})>"

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "pos_item_id": self.pos_item_id,
            "name": self.name,
            "sale_price": float(self.sale_price),
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class RecipeItem(Base):
    __tablename__ = "recipe_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id", ondelete="CASCADE"), nullable=False, index=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id", ondelete="RESTRICT"), nullable=False, index=True)
    quantity_required = Column(Numeric(15, 3), nullable=False)  # Amount per portion
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    menu_item = relationship("MenuItem", back_populates="recipes")
    ingredient = relationship("Ingredient", back_populates="recipes")

    # Unique constraint: one ingredient per menu item
    __table_args__ = (
        UniqueConstraint("menu_item_id", "ingredient_id", name="uq_menu_ingredient"),
        Index("ix_recipe_menu_ingredient", "menu_item_id", "ingredient_id"),
    )

    def __repr__(self) -> str:
        return f"<RecipeItem(menu={self.menu_item_id}, ingredient={self.ingredient_id}, qty={self.quantity_required})>"

    @property
    def cost_per_portion(self) -> float:
        """Calculate cost of this ingredient per portion."""
        if self.ingredient:
            return round(float(self.quantity_required) * float(self.ingredient.cost_per_unit), 2)
        return 0.0

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "menu_item_id": self.menu_item_id,
            "menu_item_name": self.menu_item.name if self.menu_item else None,
            "ingredient_id": self.ingredient_id,
            "ingredient_name": self.ingredient.name if self.ingredient else None,
            "ingredient_unit": self.ingredient.unit if self.ingredient else None,
            "quantity_required": float(self.quantity_required),
            "cost_per_portion": self.cost_per_portion,
        }