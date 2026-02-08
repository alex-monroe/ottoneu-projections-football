"""Tests for jobs API endpoints."""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient

from src.main import app
from src.api.jobs import set_scheduler
from src.config import get_supabase_client


@pytest.fixture
def mock_supabase():
    """Mock Supabase client."""
    mock = Mock()
    # Mock job executions table queries
    mock.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = Mock(
        data=[
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "job_id": "weekly_import",
                "status": "success",
                "executed_at": datetime.now(timezone.utc).isoformat(),
                "result": {"players_imported": 10},
                "season": 2023,
                "week": 1,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        ]
    )
    return mock


@pytest.fixture
def mock_scheduler():
    """Mock JobScheduler."""
    mock = Mock()
    mock.get_all_jobs.return_value = [
        {
            "id": "weekly_import",
            "name": "Weekly NFL Data Import",
            "next_run": datetime.now(timezone.utc).isoformat(),
            "trigger": "cron[day_of_week='tue']",
        }
    ]
    mock.manual_import = AsyncMock(
        return_value={
            "success": True,
            "players_imported": 10,
            "players_updated": 5,
            "projections_imported": 20,
            "projections_updated": 10,
            "source": "nflverse",
            "year": 2023,
            "week": 1,
            "errors": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
    return mock


@pytest.fixture
def client(mock_supabase, mock_scheduler):
    """Create test client with mocked dependencies."""
    # Override dependencies
    app.dependency_overrides[get_supabase_client] = lambda: mock_supabase
    set_scheduler(mock_scheduler)

    # Patch the scheduler in main.py to prevent startup issues in tests
    with patch("src.main.scheduler") as mock_sched:
        mock_sched.start = Mock()
        mock_sched.shutdown = Mock()

        with TestClient(app) as c:
            yield c

    # Cleanup
    app.dependency_overrides.clear()


def test_get_jobs_status(client, mock_scheduler, mock_supabase):
    """Test getting job status."""
    response = client.get("/api/jobs/status")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0

    job = data[0]
    assert job["job_id"] == "weekly_import"
    assert job["name"] == "Weekly NFL Data Import"
    assert "next_run" in job
    assert "trigger" in job


def test_trigger_manual_import(client, mock_scheduler):
    """Test manually triggering an import."""
    response = client.post(
        "/api/jobs/trigger", json={"year": 2023, "week": 1, "source": "nflverse"}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["year"] == 2023
    assert data["week"] == 1
    assert data["source"] == "nflverse"

    # Verify scheduler was called
    mock_scheduler.manual_import.assert_called_once_with(
        year=2023, week=1, source="nflverse"
    )


def test_trigger_manual_import_validation(client):
    """Test manual import with invalid data."""
    response = client.post(
        "/api/jobs/trigger",
        json={"year": 1990, "week": 1, "source": "nflverse"},  # Too old
    )

    assert response.status_code == 422  # Validation error


def test_get_job_history(client, mock_supabase):
    """Test getting job execution history."""
    # Mock the history query
    mock_supabase.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = Mock(
        data=[
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "job_id": "weekly_import",
                "status": "success",
                "executed_at": datetime.now(timezone.utc).isoformat(),
                "result": {"players_imported": 10},
                "season": 2023,
                "week": 1,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        ]
    )

    response = client.get("/api/jobs/history")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0

    execution = data[0]
    assert execution["job_id"] == "weekly_import"
    assert execution["status"] == "success"


def test_get_job_history_filtered(client, mock_supabase):
    """Test getting filtered job history."""
    response = client.get("/api/jobs/history?job_id=weekly_import&limit=10")

    assert response.status_code == 200

    # Verify filter was applied
    mock_supabase.table.return_value.select.return_value.eq.assert_called()


def test_get_job_execution_by_id(client, mock_supabase):
    """Test getting a specific job execution."""
    execution_id = "123e4567-e89b-12d3-a456-426614174000"

    # Mock single execution query
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
        data=[
            {
                "id": execution_id,
                "job_id": "weekly_import",
                "status": "success",
                "executed_at": datetime.now(timezone.utc).isoformat(),
                "result": {"players_imported": 10},
                "season": 2023,
                "week": 1,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        ]
    )

    response = client.get(f"/api/jobs/history/{execution_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == execution_id
    assert data["job_id"] == "weekly_import"


def test_get_job_execution_not_found(client, mock_supabase):
    """Test getting non-existent job execution."""
    execution_id = "nonexistent-id"

    # Mock empty result
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
        data=[]
    )

    response = client.get(f"/api/jobs/history/{execution_id}")

    assert response.status_code == 404
