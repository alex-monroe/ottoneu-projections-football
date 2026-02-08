"""
Tests for dashboard routes.
"""
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from uuid import uuid4
from decimal import Decimal
from datetime import datetime

from src.main import app
from src.config import get_supabase_client


@pytest.fixture
def client():
    """Create a test client for the app."""
    # Clean up any existing overrides
    app.dependency_overrides.clear()
    yield TestClient(app)
    # Clean up after test
    app.dependency_overrides.clear()


@pytest.fixture
def mock_supabase():
    """Mock Supabase client."""
    mock = MagicMock()
    return mock


@pytest.fixture
def sample_projections():
    """Sample projection data for testing."""
    from src.database.models import PlayerProjection

    return [
        PlayerProjection(
            player_id=str(uuid4()),
            player_name="Patrick Mahomes",
            team="KC",
            position="QB",
            week=1,
            season=2023,
            source="nflverse",
            fantasy_points=Decimal("28.50"),
            pass_yds=Decimal("320"),
            pass_tds=Decimal("3"),
            rush_yds=Decimal("15"),
            rush_tds=Decimal("0"),
            receptions=None,
            rec_yds=None,
            rec_tds=None,
        ),
        PlayerProjection(
            player_id=str(uuid4()),
            player_name="Christian McCaffrey",
            team="SF",
            position="RB",
            week=1,
            season=2023,
            source="nflverse",
            fantasy_points=Decimal("25.90"),
            pass_yds=None,
            pass_tds=None,
            rush_yds=Decimal("152"),
            rush_tds=Decimal("1"),
            receptions=Decimal("5"),
            rec_yds=Decimal("39"),
            rec_tds=Decimal("0"),
        ),
    ]


def test_dashboard_home_loads_without_data(client, mock_supabase):
    """Test that dashboard home page loads successfully even with no data."""
    # Mock empty responses
    mock_scoring = MagicMock()
    mock_scoring.data = [{"name": "PPR (Point Per Reception)"}]

    mock_projections = MagicMock()
    mock_projections.data = []

    def table_side_effect(table_name):
        if table_name == "scoring_configs":
            scoring_mock = MagicMock()
            scoring_mock.select.return_value.eq.return_value.execute.return_value = (
                mock_scoring
            )
            return scoring_mock
        elif table_name == "projections":
            proj_mock = MagicMock()
            proj_mock.select.return_value.eq.return_value.eq.return_value.execute.return_value = (
                mock_projections
            )
            return proj_mock
        return MagicMock()

    mock_supabase.table.side_effect = table_side_effect

    # Override dependency
    app.dependency_overrides[get_supabase_client] = lambda: mock_supabase

    response = client.get("/dashboard?season=2023&week=1")

    assert response.status_code == 200
    assert b"Fantasy Projections" in response.content
    assert b"No projections found" in response.content


def test_dashboard_with_invalid_scoring_config(client, mock_supabase):
    """Test dashboard handles invalid scoring config gracefully."""
    # Mock empty scoring configs
    mock_scoring = MagicMock()
    mock_scoring.data = []

    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = (
        mock_scoring
    )

    # Override dependency
    app.dependency_overrides[get_supabase_client] = lambda: mock_supabase

    response = client.get("/dashboard?season=2023&week=1&scoring=InvalidScoring")

    # Should show error page
    assert response.status_code == 404
    assert b"Error" in response.content


def test_player_detail_not_found(client, mock_supabase):
    """Test player detail page with invalid player ID."""
    player_id = str(uuid4())

    # Mock empty player response
    mock_player = MagicMock()
    mock_player.data = []

    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = (
        mock_player
    )

    # Override dependency
    app.dependency_overrides[get_supabase_client] = lambda: mock_supabase

    response = client.get(f"/dashboard/player/{player_id}?season=2023")

    # Should show 404 error
    assert response.status_code == 404
    assert b"Player not found" in response.content


def test_player_detail_loads_with_no_stats(client, mock_supabase):
    """Test player detail page when player has no stats."""
    player_id = str(uuid4())

    # Create separate mock chains for each table query
    mock_player_table = MagicMock()
    mock_projections_table = MagicMock()
    mock_scoring_table = MagicMock()

    # Mock player data
    mock_player_response = MagicMock()
    mock_player_response.data = [
        {
            "id": player_id,
            "name": "New Player",
            "team": "MIA",
            "position": "WR",
            "status": "active",
        }
    ]
    mock_player_table.select.return_value.eq.return_value.execute.return_value = (
        mock_player_response
    )

    # No projections
    mock_projections_response = MagicMock()
    mock_projections_response.data = []
    mock_projections_table.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value = (
        mock_projections_response
    )

    # Mock scoring configs
    mock_scoring_response = MagicMock()
    mock_scoring_response.data = [
        {
            "id": str(uuid4()),
            "name": "PPR (Point Per Reception)",
            "pass_yds_per_point": 25,
            "pass_td_points": 4,
            "pass_int_points": -2,
            "rush_yds_per_point": 10,
            "rush_td_points": 6,
            "rec_yds_per_point": 10,
            "rec_td_points": 6,
            "rec_points": 1,
            "fumble_points": -2,
            "is_default": True,
            "created_at": datetime.utcnow().isoformat(),
        }
    ]
    mock_scoring_table.select.return_value.execute.return_value = mock_scoring_response

    # Setup table() to return the appropriate mock based on table name
    def table_side_effect(table_name):
        if table_name == "players":
            return mock_player_table
        elif table_name == "projections":
            return mock_projections_table
        elif table_name == "scoring_configs":
            return mock_scoring_table
        return MagicMock()

    mock_supabase.table.side_effect = table_side_effect

    # Override dependency
    app.dependency_overrides[get_supabase_client] = lambda: mock_supabase

    response = client.get(f"/dashboard/player/{player_id}?season=2023")

    assert response.status_code == 200
    assert b"New Player" in response.content
    assert b"No stats found" in response.content
