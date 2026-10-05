from fastapi import APIRouter

from app.api.v1 import (
    analytics,
    audit,
    auth_security,
    bom,
    categories,
    forecast,
    inventory,
    outlets,
    plugins,
    pos_sync,
    public_menu,
    purchases,
    reports,
)

api_router = APIRouter()

api_router.include_router(auth_security.router, tags=["Authentication"])
api_router.include_router(categories.router, tags=["Categories"])
api_router.include_router(inventory.router, tags=["Inventory"])
api_router.include_router(pos_sync.router, tags=["POS Sync"])
api_router.include_router(bom.router, tags=["BOM & Recipe"])
api_router.include_router(purchases.router, tags=["Purchases"])
api_router.include_router(forecast.router, tags=["Forecast & Weather"])
api_router.include_router(outlets.router)
api_router.include_router(reports.router)
api_router.include_router(audit.router)
api_router.include_router(analytics.router)
api_router.include_router(public_menu.router)
api_router.include_router(plugins.router)
