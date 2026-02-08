"""
Main FastAPI application for NFL Fantasy Football Projections.
"""
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from src.config import get_settings
from src.database.models import HealthCheck
from src.jobs.scheduler import JobScheduler

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = JobScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.
    Starts the job scheduler on startup and shuts it down on shutdown.
    """
    # Startup: Start the job scheduler
    logger.info("Application startup: initializing job scheduler")
    scheduler.start()
    logger.info("Job scheduler started successfully")

    yield

    # Shutdown: Stop the job scheduler
    logger.info("Application shutdown: stopping job scheduler")
    scheduler.shutdown()
    logger.info("Job scheduler stopped successfully")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="NFL Fantasy Football Projections API",
    description="API for managing and retrieving NFL fantasy football projections",
    version="0.1.0",
    lifespan=lifespan,
)

# Templates for dashboard
templates = Jinja2Templates(directory="src/dashboard/templates")


@app.get("/", response_model=HealthCheck)
async def root():
    """Root endpoint - health check."""
    settings = get_settings()
    return HealthCheck(
        status="healthy", environment=settings.environment, timestamp=datetime.now()
    )


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint."""
    settings = get_settings()
    return HealthCheck(
        status="healthy", environment=settings.environment, timestamp=datetime.now()
    )


# Import and include routers
# Note: Imports placed here to avoid circular dependencies with scheduler
from src.api.loaders import router as loaders_router  # noqa: E402
from src.api.projections import router as projections_router  # noqa: E402
from src.api.jobs import router as jobs_router, set_scheduler  # noqa: E402
from src.dashboard.routes import router as dashboard_router  # noqa: E402

# Set the global scheduler instance for the jobs API
set_scheduler(scheduler)

app.include_router(loaders_router, prefix="/api", tags=["api"])
app.include_router(projections_router, prefix="/api", tags=["api"])
app.include_router(jobs_router, prefix="/api/jobs", tags=["jobs"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
