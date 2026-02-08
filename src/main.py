"""
Main FastAPI application for NFL Fantasy Football Projections.
"""
from datetime import datetime
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.config import get_settings
from src.database.models import HealthCheck

# Initialize FastAPI app
app = FastAPI(
    title="NFL Fantasy Football Projections API",
    description="API for managing and retrieving NFL fantasy football projections",
    version="0.1.0"
)

# Templates for dashboard
templates = Jinja2Templates(directory="src/dashboard/templates")


@app.get("/", response_model=HealthCheck)
async def root():
    """Root endpoint - health check."""
    settings = get_settings()
    return HealthCheck(
        status="healthy",
        environment=settings.environment,
        timestamp=datetime.now()
    )


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint."""
    settings = get_settings()
    return HealthCheck(
        status="healthy",
        environment=settings.environment,
        timestamp=datetime.now()
    )


# Import and include routers
from src.api.loaders import router as loaders_router
app.include_router(loaders_router, prefix="/api", tags=["api"])

# Dashboard router will be added in Phase 4
# from src.dashboard.routes import router as dashboard_router
# app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
