
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, verify_license
from app.models.ingredient import Ingredient
from app.models.menu import MenuItem, RecipeItem
from app.schemas.bom_schema import (
    MenuItemCreate,
    MenuItemResponse,
    MenuItemUpdate,
    MenuListResponse,
    MenuWithRecipesResponse,
    RecipeItemCreate,
    RecipeItemResponse,
    RecipeItemUpdate,
    RecipeListResponse,
)
from app.schemas.forecast_schema import (
    RecipeScalerItemResponse,
    RecipeScalerRequest,
    RecipeScalerResponse,
)

router = APIRouter(prefix="/bom", tags=["BOM & Recipe"])

# Menu endpoints
@router.get("/menus", response_model=MenuListResponse)
def list_menus(
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: str | None = Query(None),
):
    """List all menu items."""
    query = db.query(MenuItem).filter(MenuItem.is_active)

    if search:
        search_term = f"%{search}%"
        query = query.filter(MenuItem.name.ilike(search_term))

    total = query.count()
    items = query.order_by(MenuItem.name).offset(skip).limit(limit).all()

    return MenuListResponse(
        items=[MenuItemResponse.model_validate(item) for item in items],
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        total_pages=(total + limit - 1) // limit,
    )

@router.get("/menus/{menu_id}", response_model=MenuWithRecipesResponse)
def get_menu(
    menu_id: int,
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
):
    """Get menu with full recipe details."""
    menu = db.query(MenuItem).filter(MenuItem.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")

    recipes = db.query(RecipeItem).filter(RecipeItem.menu_item_id == menu_id).all()

    return MenuWithRecipesResponse(
        **MenuItemResponse.model_validate(menu).model_dump(),
        recipes=[RecipeItemResponse.model_validate(r) for r in recipes],
    )

@router.post("/menus", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
def create_menu(
    data: MenuItemCreate,
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
):
    """Create new menu item."""
    if data.pos_item_id:
        existing = db.query(MenuItem).filter(MenuItem.pos_item_id == data.pos_item_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="POS Item ID already exists")

    menu = MenuItem(**data.model_dump())
    db.add(menu)
    db.commit()
    db.refresh(menu)
    return MenuItemResponse.model_validate(menu)

@router.put("/menus/{menu_id}", response_model=MenuItemResponse)
def update_menu(
    menu_id: int,
    data: MenuItemUpdate,
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
):
    """Update menu item."""
    menu = db.query(MenuItem).filter(MenuItem.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")

    if data.pos_item_id and data.pos_item_id != menu.pos_item_id:
        existing = db.query(MenuItem).filter(MenuItem.pos_item_id == data.pos_item_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="POS Item ID already exists")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(menu, field, value)

    db.commit()
    db.refresh(menu)
    return MenuItemResponse.model_validate(menu)

@router.delete("/menus/{menu_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu(
    menu_id: int,
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
):
    """Soft delete menu item."""
    menu = db.query(MenuItem).filter(MenuItem.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")

    menu.is_active = False
    db.commit()
    return

# Recipe endpoints
@router.get("/menus/{menu_id}/recipes", response_model=RecipeListResponse)
def list_recipes(
    menu_id: int,
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
):
    """List all recipes for a menu."""
    menu = db.query(MenuItem).filter(MenuItem.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")

    recipes = db.query(RecipeItem).filter(RecipeItem.menu_item_id == menu_id).all()

    return RecipeListResponse(
        items=[RecipeItemResponse.model_validate(r) for r in recipes],
        total=len(recipes),
    )

@router.post("/menus/{menu_id}/recipes", response_model=RecipeItemResponse, status_code=status.HTTP_201_CREATED)
def add_recipe(
    menu_id: int,
    data: RecipeItemCreate,
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
):
    """Add ingredient to menu recipe."""
    menu = db.query(MenuItem).filter(MenuItem.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")

    ingredient = db.query(Ingredient).filter(Ingredient.id == data.ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    # Check if already exists
    existing = db.query(RecipeItem).filter(
        RecipeItem.menu_item_id == menu_id,
        RecipeItem.ingredient_id == data.ingredient_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ingredient already in recipe")

    recipe = RecipeItem(
        menu_item_id=menu_id,
        ingredient_id=data.ingredient_id,
        quantity_required=data.quantity_required,
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return RecipeItemResponse.model_validate(recipe)

@router.put("/recipes/{recipe_id}", response_model=RecipeItemResponse)
def update_recipe(
    recipe_id: int,
    data: RecipeItemUpdate,
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
):
    """Update recipe ingredient quantity."""
    recipe = db.query(RecipeItem).filter(RecipeItem.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    if data.ingredient_id and data.ingredient_id != recipe.ingredient_id:
        ingredient = db.query(Ingredient).filter(Ingredient.id == data.ingredient_id).first()
        if not ingredient:
            raise HTTPException(status_code=404, detail="Ingredient not found")

        # Check uniqueness
        existing = db.query(RecipeItem).filter(
            RecipeItem.menu_item_id == recipe.menu_item_id,
            RecipeItem.ingredient_id == data.ingredient_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Ingredient already in recipe")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(recipe, field, value)

    db.commit()
    db.refresh(recipe)
    return RecipeItemResponse.model_validate(recipe)

@router.delete("/recipes/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
):
    """Remove ingredient from recipe."""
    recipe = db.query(RecipeItem).filter(RecipeItem.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    db.delete(recipe)
    db.commit()
    return

# Recipe Scaler
@router.post("/scaler", response_model=RecipeScalerResponse)
def scale_recipe(
    data: RecipeScalerRequest,
    db: Session = Depends(get_db),
    license_info: dict = Depends(verify_license),
):
    """
    Calculate ingredient requirements for target portions.
    Compares with current stock and returns sufficiency status.
    """
    menu = db.query(MenuItem).filter(MenuItem.id == data.menu_item_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")

    recipes = db.query(RecipeItem).filter(RecipeItem.menu_item_id == data.menu_item_id).all()
    if not recipes:
        raise HTTPException(status_code=400, detail="Menu has no recipe defined")

    items = []
    all_sufficient = True
    total_cost = 0.0

    for recipe in recipes:
        ingredient = db.query(Ingredient).filter(Ingredient.id == recipe.ingredient_id).first()
        if not ingredient:
            continue

        total_needed = float(recipe.quantity_required) * data.target_portions
        current_stock = float(ingredient.current_stock)
        is_sufficient = current_stock >= total_needed
        deficit = max(0.0, total_needed - current_stock)
        item_cost = total_needed * float(ingredient.cost_per_unit)

        if not is_sufficient:
            all_sufficient = False

        total_cost += item_cost

        items.append(RecipeScalerItemResponse(
            ingredient_name=ingredient.name,
            unit=ingredient.unit,
            per_portion=float(recipe.quantity_required),
            total_needed=total_needed,
            current_stock=current_stock,
            is_sufficient=is_sufficient,
            deficit=deficit,
        ))

    return RecipeScalerResponse(
        menu_name=menu.name,
        target_portions=data.target_portions,
        items=items,
        all_sufficient=all_sufficient,
        total_estimated_cost=round(total_cost, 2),
    )