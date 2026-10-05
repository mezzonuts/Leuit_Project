"""Category CRUD API."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, verify_license
from app.models.category import IngredientCategory
from app.models.ingredient import Ingredient
from app.schemas.category_schema import (
    CategoryCreate,
    CategoryListResponse,
    CategoryResponse,
    CategoryUpdate,
)

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=CategoryListResponse)
def list_categories(db: Session = Depends(get_db), license_info: dict = Depends(verify_license)):
    cats = db.query(IngredientCategory).order_by(IngredientCategory.name).all()
    return CategoryListResponse(
        items=[CategoryResponse(id=c.id, name=c.name, color=c.color,
                                created_at=c.created_at.isoformat() if c.created_at else None) for c in cats],
        total=len(cats),
    )


@router.post("", response_model=CategoryResponse)
def create_category(data: CategoryCreate, db: Session = Depends(get_db), license_info: dict = Depends(verify_license)):
    existing = db.query(IngredientCategory).filter(IngredientCategory.name == data.name).first()
    if existing:
        raise HTTPException(status_code=409, detail="Category already exists")
    cat = IngredientCategory(name=data.name, color=data.color)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return CategoryResponse(id=cat.id, name=cat.name, color=cat.color,
                            created_at=cat.created_at.isoformat() if cat.created_at else None)


@router.put("/{cat_id}", response_model=CategoryResponse)
def update_category(cat_id: int, data: CategoryUpdate, db: Session = Depends(get_db), license_info: dict = Depends(verify_license)):
    cat = db.query(IngredientCategory).filter(IngredientCategory.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(cat, field, value)
    db.commit()
    db.refresh(cat)
    return CategoryResponse(id=cat.id, name=cat.name, color=cat.color,
                            created_at=cat.created_at.isoformat() if cat.created_at else None)


@router.delete("/{cat_id}")
def delete_category(cat_id: int, db: Session = Depends(get_db), license_info: dict = Depends(verify_license)):
    cat = db.query(IngredientCategory).filter(IngredientCategory.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    # Check if any ingredients use this category
    count = db.query(Ingredient).filter(Ingredient.category_id == cat_id).count()
    if count > 0:
        raise HTTPException(status_code=409, detail=f"Cannot delete: {count} ingredients use this category")
    db.delete(cat)
    db.commit()
    return {"message": "Category deleted"}
