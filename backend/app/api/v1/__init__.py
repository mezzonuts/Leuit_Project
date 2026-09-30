from fastapi import APIRouter

from app.api.v1 import (
    auth_security,
    bom,
    forecast,
    inventory,
    pos_sync,
    purchases,
)

api_router = APIRouter()

api_router.include_router(auth_security.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(inventory.router, tags=["Inventory"])
api_router.include_router(pos_sync.router, prefix="/sync", tags=["POS Sync"])
api_router.include_router(bom.router, prefix="/bom", tags=["BOM & Recipe"])
api_router.include_router(purchases.router, prefix="/purchases", tags=["Purchases"])
api_router.include_router(forecast.router, prefix="/forecast", tags=["Forecast & Weather"])