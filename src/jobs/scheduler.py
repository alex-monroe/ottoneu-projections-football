"""
Scheduled job service using APScheduler for automated data imports.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.loaders.service import LoaderService
from src.config import get_supabase_client

logger = logging.getLogger(__name__)


class JobScheduler:
    """Manages scheduled jobs for automated data imports."""

    def __init__(self):
        """Initialize the job scheduler."""
        self.scheduler = AsyncIOScheduler()
        self.supabase = get_supabase_client()
        self.loader_service = LoaderService(self.supabase)

    def start(self):
        """Start the scheduler and register jobs."""
        logger.info("Starting job scheduler...")

        # Weekly data import - runs every Tuesday at 8:00 AM UTC
        # (NFL games are Sunday/Monday, data typically available by Tuesday)
        self.scheduler.add_job(
            self.weekly_import_job,
            trigger=CronTrigger(day_of_week="tue", hour=8, minute=0, timezone="UTC"),
            id="weekly_import",
            name="Weekly NFL Data Import",
            replace_existing=True,
            max_instances=1,  # Prevent overlapping runs
        )

        self.scheduler.start()
        logger.info("Job scheduler started successfully")

    def shutdown(self):
        """Shutdown the scheduler gracefully."""
        logger.info("Shutting down job scheduler...")
        self.scheduler.shutdown(wait=True)
        logger.info("Job scheduler shut down")

    async def weekly_import_job(self):
        """
        Automated weekly data import job.

        Imports data for the most recent completed NFL week.
        This job runs every Tuesday at 8:00 AM UTC.
        """
        try:
            logger.info("Starting weekly import job...")

            # Determine current NFL season and week
            # For MVP, we'll use current date to estimate the week
            # In production, you'd use an NFL schedule API
            current_year = datetime.now(timezone.utc).year

            # NFL season typically starts in September
            # For simplicity, assume week 1 starts first week of September
            # This is a simplified calculation - production would use actual NFL schedule
            current_month = datetime.now(timezone.utc).month

            if current_month < 9:
                # Off-season, import last year's data
                season = current_year - 1
                week = 18  # Last week of regular season
            else:
                season = current_year
                # Rough estimate: weeks since September
                week = min(((current_month - 9) * 4) + 1, 18)

            logger.info(f"Importing data for season {season}, week {week}")

            # Import using NFLVerse as primary source
            result = await self.loader_service.import_weekly_data(
                year=season, week=week, source="nflverse"
            )

            # Log result to job execution table
            await self._log_job_execution(
                job_id="weekly_import",
                status="success" if result.success else "failed",
                result=result.model_dump(),
                season=season,
                week=week,
            )

            if result.success:
                logger.info(
                    f"Weekly import completed: {result.players_imported} players, "
                    f"{result.projections_imported} projections"
                )
            else:
                logger.error(f"Weekly import failed: {result.errors}")

        except Exception as e:
            logger.error(f"Weekly import job failed with exception: {e}", exc_info=True)
            await self._log_job_execution(
                job_id="weekly_import",
                status="error",
                result={"error": str(e)},
                season=season if "season" in locals() else None,
                week=week if "week" in locals() else None,
            )

    async def manual_import(
        self, year: int, week: int, source: str = "nflverse"
    ) -> dict:
        """
        Manually trigger a data import.

        Args:
            year: NFL season year
            week: Week number (1-18)
            source: Data source ('nflverse' or 'ffdp')

        Returns:
            Import result dictionary
        """
        logger.info(f"Manual import triggered for {year} week {week} from {source}")

        try:
            result = await self.loader_service.import_weekly_data(
                year=year, week=week, source=source
            )

            await self._log_job_execution(
                job_id="manual_import",
                status="success" if result.success else "failed",
                result=result.model_dump(),
                season=year,
                week=week,
            )

            return result.model_dump()

        except Exception as e:
            logger.error(f"Manual import failed: {e}", exc_info=True)
            await self._log_job_execution(
                job_id="manual_import",
                status="error",
                result={"error": str(e)},
                season=year,
                week=week,
            )
            raise

    async def _log_job_execution(
        self,
        job_id: str,
        status: str,
        result: dict,
        season: Optional[int] = None,
        week: Optional[int] = None,
    ):
        """
        Log job execution to database.

        Args:
            job_id: Identifier for the job type
            status: 'success', 'failed', or 'error'
            result: Job result data
            season: NFL season (optional)
            week: NFL week (optional)
        """
        try:
            self.supabase.table("job_executions").insert(
                {
                    "job_id": job_id,
                    "status": status,
                    "executed_at": datetime.now(timezone.utc).isoformat(),
                    "result": result,
                    "season": season,
                    "week": week,
                }
            ).execute()
            logger.debug(f"Logged job execution: {job_id} - {status}")
        except Exception as e:
            # Don't fail the job if logging fails
            logger.error(f"Failed to log job execution: {e}")

    def get_next_run_time(self, job_id: str) -> Optional[datetime]:
        """
        Get the next scheduled run time for a job.

        Args:
            job_id: Job identifier

        Returns:
            Next run datetime or None if job not found
        """
        job = self.scheduler.get_job(job_id)
        if job:
            return job.next_run_time
        return None

    def get_all_jobs(self) -> list:
        """
        Get information about all scheduled jobs.

        Returns:
            List of job information dictionaries
        """
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append(
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat()
                    if job.next_run_time
                    else None,
                    "trigger": str(job.trigger),
                }
            )
        return jobs
