from datetime import datetime

from pydantic import BaseModel, Field


# Weather
class WeatherForecastResponse(BaseModel):
    date: datetime
    temperature_min: float
    temperature_max: float
    humidity: float
    rainfall_probability: float
    weather_description: str

# Restock Recommendation
class RestockItemResponse(BaseModel):
    ingredient_id: int
    ingredient_name: str
    unit: str
    current_stock: float
    predicted_consumption_7d: float
    recommended_order_qty: float
    safety_stock: float
    estimated_cost: float
    priority: str  # high, medium, low
    supplier_id: int | None = None
    supplier_name: str | None = None
    lead_time_days: int

class RestockSheetResponse(BaseModel):
    items: list[RestockItemResponse]
    total_estimated_cost: float
    high_priority_count: int
    generated_at: datetime

# Recipe Scaler
class RecipeScalerRequest(BaseModel):
    menu_item_id: int = Field(..., ge=1)
    target_portions: int = Field(..., ge=1)

class RecipeScalerItemResponse(BaseModel):
    ingredient_name: str
    unit: str
    per_portion: float
    total_needed: float
    current_stock: float
    is_sufficient: bool
    deficit: float

class RecipeScalerResponse(BaseModel):
    menu_name: str
    target_portions: int
    items: list[RecipeScalerItemResponse]
    all_sufficient: bool
    total_estimated_cost: float