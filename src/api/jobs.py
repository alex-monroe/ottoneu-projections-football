"""
API endpoints for job management and monitoring.
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from supabase import Client

from src.database.models import (
    JobStatus,
    JobExecution,
    JobTriggerRequest,
    ImportResultModel
)
from src.config import get_supabase_client
from src.jobs.scheduler import JobScheduler

router = APIRouter()

# Global scheduler instance (will be initialized in main.py)
_scheduler: JobScheduler = None


def set_scheduler(scheduler: JobScheduler):
    """Set the global scheduler instance."""
    global _scheduler
    _scheduler = scheduler


def get_scheduler() -> JobScheduler:
    """Dependency to get the scheduler instance."""
    if _scheduler is None:
        raise HTTPException(
            status_code=503,
            detail="Job scheduler not initialized"
        )
    return _scheduler


@router.get("/status", response_model=List[JobStatus])
async def get_jobs_status(
    scheduler: JobScheduler = Depends(get_scheduler),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get status of all scheduled jobs.

    Returns information about each job including:
    - Job ID and name
    - Next scheduled run time
    - Trigger configuration
    - Last execution result
    """
    jobs_info = scheduler.get_all_jobs()
    result = []

    for job_info in jobs_info:
        # Get last execution for this job
        last_exec = None
        try:
            response = supabase.table('job_executions') \
                .select('*') \
                .eq('job_id', job_info['id']) \
                .order('executed_at', desc=True) \
                .limit(1) \
                .execute()

            if response.data:
                last_exec = JobExecution(**response.data[0])
        except Exception:
            # Don't fail if we can't get last execution
            pass

        result.append(JobStatus(
            job_id=job_info['id'],
            name=job_info['name'],
            next_run=job_info['next_run'],
            trigger=job_info['trigger'],
            last_execution=last_exec
        ))

    return result


@router.post("/trigger", response_model=ImportResultModel)
async def trigger_manual_import(
    request: JobTriggerRequest,
    scheduler: JobScheduler = Depends(get_scheduler)
):
    """
    Manually trigger a data import job.

    This endpoint allows you to import data for a specific week/season
    without waiting for the scheduled job to run.

    Args:
        request: Job trigger parameters (year, week, source)

    Returns:
        Import result with counts and status
    """
    try:
        result_dict = await scheduler.manual_import(
            year=request.year,
            week=request.week,
            source=request.source
        )
        return ImportResultModel(**result_dict)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Manual import failed: {str(e)}"
        )


@router.get("/history", response_model=List[JobExecution])
async def get_job_history(
    job_id: str = None,
    limit: int = 50,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get job execution history.

    Args:
        job_id: Filter by specific job ID (optional)
        limit: Maximum number of results (default 50)

    Returns:
        List of job execution records
    """
    query = supabase.table('job_executions').select('*')

    if job_id:
        query = query.eq('job_id', job_id)

    query = query.order('executed_at', desc=True).limit(limit)

    try:
        response = query.execute()
        return [JobExecution(**record) for record in response.data]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch job history: {str(e)}"
        )


@router.get("/history/{execution_id}", response_model=JobExecution)
async def get_job_execution(
    execution_id: str,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get details of a specific job execution.

    Args:
        execution_id: Job execution UUID

    Returns:
        Job execution details
    """
    try:
        response = supabase.table('job_executions') \
            .select('*') \
            .eq('id', execution_id) \
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Job execution not found")

        return JobExecution(**response.data[0])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch job execution: {str(e)}"
        )
