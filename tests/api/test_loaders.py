"""
Tests for loader API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from datetime import datetime

from src.main import app
from src.loaders.service import ImportResult, LoaderService
from src.api.loaders import get_loader_service
from src.config import get_supabase_client


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_import_result():
    """Create a successful mock import result."""
    result = ImportResult()
    result.success = True
    result.players_imported = 10
    result.players_updated = 2
    result.projections_imported = 50
    result.projections_updated = 5
    result.source = "nflverse"
    result.year = 2023
    result.week = 1
    result.timestamp = datetime.utcnow()
    return result


@pytest.fixture
def mock_service(mock_import_result):
    """Create a mock loader service."""
    service = MagicMock(spec=LoaderService)
    service.import_weekly_data.return_value = mock_import_result
    service.get_available_sources.return_value = [
        {"name": "nflverse", "status": "available", "description": "NFLVerse data"},
        {"name": "ffdp", "status": "available", "description": "FFDP CSV data"},
    ]
    return service


@pytest.fixture(autouse=True)
def override_dependencies(mock_service):
    """Override dependencies for all tests."""
    # Override loader service
    app.dependency_overrides[get_loader_service] = lambda: mock_service

    # Override Supabase client
    mock_supabase = MagicMock()
    app.dependency_overrides[get_supabase_client] = lambda: mock_supabase

    yield

    # Clear overrides after test
    app.dependency_overrides.clear()


def test_import_weekly_data_success(client, mock_service, mock_import_result):
    """Test successful weekly data import via API."""
    response = client.post(
        "/api/loaders/import/weekly",
        json={"year": 2023, "week": 1, "source": "nflverse"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["players_imported"] == 10
    assert data["projections_imported"] == 50
    assert data["year"] == 2023
    assert data["week"] == 1


def test_import_weekly_data_validation_error(client):
    """Test validation error for invalid request."""
    response = client.post(
        "/api/loaders/import/weekly", json={"year": 2023, "week": 25}  # Invalid week
    )

    assert response.status_code == 422  # Validation error


def test_import_weekly_data_not_found(client, mock_service):
    """Test 404 when data not available."""
    from src.loaders.exceptions import DataNotAvailableError

    mock_service.import_weekly_data.side_effect = DataNotAvailableError("No data")

    response = client.post(
        "/api/loaders/import/weekly",
        json={
            "year": 2020,
            "week": 1,
        },  # Valid year but will raise DataNotAvailableError
    )

    assert response.status_code == 404


def test_import_weekly_data_import_failed(client, mock_service):
    """Test handling of failed import (success=False)."""
    failed_result = ImportResult()
    failed_result.success = False
    failed_result.errors = ["Import failed"]
    failed_result.year = 2023
    failed_result.week = 1
    failed_result.timestamp = datetime.utcnow()

    mock_service.import_weekly_data.return_value = failed_result

    response = client.post("/api/loaders/import/weekly", json={"year": 2023, "week": 1})

    assert response.status_code == 500


def test_import_season_data_success(client, mock_service, mock_import_result):
    """Test importing multiple weeks."""
    response = client.post(
        "/api/loaders/import/season?year=2023&start_week=1&end_week=3"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3  # 3 weeks imported
    assert all(item["success"] for item in data)


def test_import_season_data_invalid_range(client):
    """Test validation for invalid week range."""
    response = client.post(
        "/api/loaders/import/season?year=2023&start_week=5&end_week=2"
    )

    assert response.status_code == 400


def test_get_data_sources_success(client, mock_service):
    """Test getting available data sources."""
    response = client.get("/api/loaders/sources")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "nflverse"


def test_get_available_data_empty(client):
    """Test getting available data when database is empty."""
    mock_supabase = MagicMock()
    mock_response = MagicMock()
    mock_response.data = []

    mock_supabase.table().select().execute.return_value = mock_response
    app.dependency_overrides[get_supabase_client] = lambda: mock_supabase

    response = client.get("/api/loaders/available-data")

    assert response.status_code == 200
    data = response.json()
    assert data["total_weeks"] == 0
    assert data["seasons"] == []


def test_get_available_data_with_data(client):
    """Test getting available data summary."""
    mock_supabase = MagicMock()
    mock_response = MagicMock()
    mock_response.data = [
        {"season": 2023, "week": 1, "source": "nflverse"},
        {"season": 2023, "week": 2, "source": "nflverse"},
        {"season": 2023, "week": 1, "source": "ffdp"},
    ]

    mock_supabase.table().select().execute.return_value = mock_response
    app.dependency_overrides[get_supabase_client] = lambda: mock_supabase

    response = client.get("/api/loaders/available-data")

    assert response.status_code == 200
    data = response.json()
    assert data["total_weeks"] == 2
    assert len(data["seasons"]) == 1
    assert data["seasons"][0]["season"] == 2023
    assert "nflverse" in data["sources"]
    assert "ffdp" in data["sources"]
