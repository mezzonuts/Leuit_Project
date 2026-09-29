from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1 import api_router
from app.core.config import settings
from app.core.database import _engine


# Lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Environment: {settings.ENVIRONMENT}")

    yield

    # Shutdown
    print(f"Shutting down {settings.APP_NAME}")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Local-First F&B Demand & Inventory Forecasting API",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB Lock Guard Middleware — blocks protected endpoints when DB is locked
PROTECTED_PREFIXES = (
    "/api/v1/inventory",
    "/api/v1/bom",
    "/api/v1/purchases",
    "/api/v1/forecast",
    "/api/v1/sync",
)

@app.middleware("http")
async def db_lock_guard(request: Request, call_next):
    """Return 423 if database engine not initialized for protected routes."""
    path = request.url.path
    if any(path.startswith(prefix) for prefix in PROTECTED_PREFIXES):
        if _engine is None:
            return JSONResponse(
                status_code=423,
                content={"detail": "Database is locked. Please unlock the database first."},
            )
    response = await call_next(request)
    return response

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}

# Serve frontend in production
if not settings.DEBUG:
    try:
        app.mount("/static", StaticFiles(directory="dist"), name="static")

        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            return FileResponse("dist/index.html")
    except RuntimeError:
        pass  # dist folder doesn't exist yet

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )