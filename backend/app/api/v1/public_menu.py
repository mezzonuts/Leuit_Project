"""Public menu API for customer-facing features."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.models.menu import MenuItem, RecipeItem

router = APIRouter(prefix="/public", tags=["Public"])


@router.get("/menu")
def get_public_menu(
    db: Session = Depends(get_db),
) -> dict:
    """Get active menu items with safe fields only (no cost/margin data)."""
    items = db.query(MenuItem).filter(MenuItem.is_active).all()
    
    result = []
    for item in items:
        recipes = db.query(RecipeItem).filter(RecipeItem.menu_item_id == item.id).all()
        result.append({
            "id": item.id,
            "name": item.name,
            "sale_price": float(item.sale_price),
            "ingredient_count": len(recipes),
            "is_active": item.is_active,
        })
    
    return {
        "items": result,
        "total": len(result),
    }
