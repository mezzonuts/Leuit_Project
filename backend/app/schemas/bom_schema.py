from datetime import datetime

from pydantic import BaseModel, Field


# Menu schemas
class MenuItemBase(BaseModel):
    pos_item_id: str | None = Field(None, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    sale_price: float = Field(..., ge=0)

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemUpdate(BaseModel):
    pos_item_id: str | None = Field(None, max_length=100)
    name: str | None = Field(None, min_length=1, max_length=255)
    sale_price: float | None = Field(None, ge=0)
    is_active: bool | None = None

class MenuItemResponse(MenuItemBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Recipe schemas
class RecipeItemBase(BaseModel):
    ingredient_id: int = Field(..., ge=1)
    quantity_required: float = Field(..., gt=0)

class RecipeItemCreate(RecipeItemBase):
    pass

class RecipeItemUpdate(BaseModel):
    ingredient_id: int | None = Field(None, ge=1)
    quantity_required: float | None = Field(None, gt=0)

class RecipeItemResponse(RecipeItemBase):
    id: int
    menu_item_id: int
    menu_item_name: str | None = None
    ingredient_name: str | None = None
    ingredient_unit: str | None = None
    cost_per_portion: float

    class Config:
        from_attributes = True

# Menu with recipes
class MenuWithRecipesResponse(MenuItemResponse):
    recipes: list[RecipeItemResponse] = []

# BOM endpoints
class MenuListResponse(BaseModel):
    items: list[MenuItemResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class RecipeListResponse(BaseModel):
    items: list[RecipeItemResponse]
    total: int