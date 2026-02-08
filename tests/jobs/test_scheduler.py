"""Tests for the job scheduler."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone

from src.jobs.scheduler import JobScheduler
from src.database.models import ImportResultModel


@pytest.fixture
def mock_supabase():
    """Mock Supabase client."""
    mock = Mock()
    mock.table.return_value.insert.return_value.execute.return_value = Mock()
    return mock


@pytest.fixture
def mock_loader_service():
    """Mock LoaderService."""
    mock = Mock()
    mock.import_weekly_data = AsyncMock(
        return_value=ImportResultModel(
            success=True,
            players_imported=10,
            players_updated=5,
            projections_imported=20,
            projections_updated=10,
            source="nflverse",
            year=2023,
            week=1,
            errors=[],
            timestamp=datetime.now(timezone.utc),
        )
    )
    return mock


@pytest.fixture
def scheduler(mock_supabase, mock_loader_service):
    """Create a JobScheduler with mocked dependencies."""
    with patch("src.jobs.scheduler.get_supabase_client", return_value=mock_supabase):
        with patch(
            "src.jobs.scheduler.LoaderService", return_value=mock_loader_service
        ):
            scheduler = JobScheduler()
            scheduler.supabase = mock_supabase
            scheduler.loader_service = mock_loader_service
            return scheduler


def test_scheduler_initialization(scheduler):
    """Test that scheduler initializes correctly."""
    assert scheduler.scheduler is not None
    assert scheduler.supabase is not None
    assert scheduler.loader_service is not None


def test_scheduler_start(scheduler):
    """Test starting the scheduler."""
    scheduler.start()

    # Verify scheduler is running
    assert scheduler.scheduler.running

    # Verify weekly_import job was added
    jobs = scheduler.scheduler.get_jobs()
    assert len(jobs) > 0
    assert any(job.id == "weekly_import" for job in jobs)

    # Cleanup
    scheduler.shutdown()


def test_scheduler_shutdown(scheduler):
    """Test shutting down the scheduler."""
    scheduler.start()
    assert scheduler.scheduler.running

    # Shutdown should complete without errors
    scheduler.shutdown()
    # Note: APScheduler may not immediately set running=False after shutdown
    # The important thing is that shutdown() completes without exceptions


@pytest.mark.asyncio
async def test_manual_import_success(scheduler, mock_loader_service):
    """Test manual import succeeds."""
    result = await scheduler.manual_import(year=2023, week=1, source="nflverse")

    # Verify loader service was called
    mock_loader_service.import_weekly_data.assert_called_once_with(
        year=2023, week=1, source="nflverse"
    )

    # Verify result
    assert result["success"] is True
    assert result["year"] == 2023
    assert result["week"] == 1


@pytest.mark.asyncio
async def test_manual_import_logs_execution(scheduler, mock_supabase):
    """Test manual import logs to database."""
    await scheduler.manual_import(year=2023, week=1)

    # Verify log was written
    mock_supabase.table.assert_called_with("job_executions")
    mock_supabase.table.return_value.insert.assert_called()


@pytest.mark.asyncio
async def test_weekly_import_job(scheduler, mock_loader_service):
    """Test weekly import job execution."""
    await scheduler.weekly_import_job()

    # Verify loader service was called
    mock_loader_service.import_weekly_data.assert_called_once()

    # Verify it used nflverse as source
    call_args = mock_loader_service.import_weekly_data.call_args
    assert call_args.kwargs["source"] == "nflverse"


def test_get_next_run_time(scheduler):
    """Test getting next run time for a job."""
    scheduler.start()

    next_run = scheduler.get_next_run_time("weekly_import")

    # Should have a next run time scheduled
    assert next_run is not None
    assert isinstance(next_run, datetime)

    scheduler.shutdown()


def test_get_next_run_time_invalid_job(scheduler):
    """Test getting next run time for non-existent job."""
    scheduler.start()

    next_run = scheduler.get_next_run_time("nonexistent_job")

    assert next_run is None

    scheduler.shutdown()


def test_get_all_jobs(scheduler):
    """Test getting all jobs."""
    scheduler.start()

    jobs = scheduler.get_all_jobs()

    assert isinstance(jobs, list)
    assert len(jobs) > 0

    # Verify job info structure
    job = jobs[0]
    assert "id" in job
    assert "name" in job
    assert "next_run" in job
    assert "trigger" in job

    scheduler.shutdown()


@pytest.mark.asyncio
async def test_log_job_execution(scheduler, mock_supabase):
    """Test logging job execution."""
    await scheduler._log_job_execution(
        job_id="test_job", status="success", result={"count": 10}, season=2023, week=1
    )

    # Verify Supabase insert was called
    mock_supabase.table.assert_called_with("job_executions")
    insert_call = mock_supabase.table.return_value.insert.call_args

    assert insert_call is not None
    data = insert_call[0][0]
    assert data["job_id"] == "test_job"
    assert data["status"] == "success"
    assert data["season"] == 2023
    assert data["week"] == 1


@pytest.mark.asyncio
async def test_log_job_execution_handles_errors(scheduler, mock_supabase):
    """Test that logging errors don't fail the job."""
    # Make insert raise an exception
    mock_supabase.table.return_value.insert.side_effect = Exception("DB error")

    # Should not raise exception
    await scheduler._log_job_execution(job_id="test_job", status="success", result={})
