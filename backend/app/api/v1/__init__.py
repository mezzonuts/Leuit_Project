from fastapi import APIRouter

from app.api.v1 import (
    analytics,
    audit,
    auth_security,
    bom,
    forecast,
    inventory,
    outlets,
    pos_sync,
    public_menu,
    purchases,
    reports,
)

api_router = APIRouter()

api_router.include_router(auth_security.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(inventory.router, tags=["Inventory"])
api_router.include_router(pos_sync.router, prefix="/sync", tags=["POS Sync"])
api_router.include_router(bom.router, prefix="/bom", tags=["BOM & Recipe"])
api_router.include_router(purchases.router, prefix="/purchases", tags=["Purchases"])
api_router.include_router(forecast.router, prefix="/forecast", tags=["Forecast & Weather"])
api_router.include_router(outlets.router)
api_router.include_router(reports.router)
api_router.include_router(audit.router)
api_router.include_router(analytics.router)
api_router.include_router(public_menu.router)
