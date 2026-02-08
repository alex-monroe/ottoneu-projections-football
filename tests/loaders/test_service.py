"""
Tests for loader service.
"""
import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4

from src.loaders.service import LoaderService, ImportResult
from src.loaders.exceptions import DataNotAvailableError


@pytest.fixture
def loader_service(mock_supabase_client):
    """Create loader service with mocked dependencies."""
    return LoaderService(mock_supabase_client)


def test_import_result_to_dict():
    """Test ImportResult conversion to dictionary."""
    result = ImportResult()
    result.success = True
    result.players_imported = 10
    result.projections_imported = 50
    result.source = "nflverse"
    result.year = 2023
    result.week = 1

    data = result.to_dict()

    assert data["success"] is True
    assert data["players_imported"] == 10
    assert data["projections_imported"] == 50
    assert data["source"] == "nflverse"
    assert data["year"] == 2023
    assert data["week"] == 1
    assert "timestamp" in data


def test_import_weekly_data_success(
    loader_service, sample_nflverse_data, mock_supabase_client
):
    """Test successful weekly data import."""
    with patch.object(loader_service.nflverse_loader, "load_weekly_data") as mock_load:
        mock_load.return_value = sample_nflverse_data

        # Mock database responses
        select_response = MagicMock()
        select_response.data = []
        mock_supabase_client.table().select().eq().eq().execute.return_value = (
            select_response
        )

        insert_response = MagicMock()
        insert_response.data = [{"id": str(uuid4())}]
        mock_supabase_client.table().insert().execute.return_value = insert_response

        result = loader_service.import_weekly_data(2023, 1, source="nflverse")

        assert result.success is True
        assert result.players_imported > 0
        assert result.year == 2023
        assert result.week == 1


def test_import_weekly_data_with_fallback(loader_service, sample_ffdp_data):
    """Test fallback to FFDP when NFLVerse fails."""
    with patch.object(
        loader_service.nflverse_loader, "load_weekly_data"
    ) as mock_nflverse:
        with patch.object(loader_service.ffdp_loader, "load_weekly_csv") as mock_ffdp:
            # NFLVerse fails
            mock_nflverse.side_effect = DataNotAvailableError("NFLVerse unavailable")

            # FFDP succeeds
            mock_ffdp.return_value = sample_ffdp_data

            result = loader_service.import_weekly_data(
                2023, 1, source="nflverse", use_fallback=True
            )

            assert result.source == "ffdp"  # Should have switched to fallback
            mock_ffdp.assert_called_once()


def test_import_weekly_data_fallback_disabled(loader_service):
    """Test that fallback doesn't occur when disabled."""
    with patch.object(
        loader_service.nflverse_loader, "load_weekly_data"
    ) as mock_nflverse:
        with patch.object(loader_service.ffdp_loader, "load_weekly_csv") as mock_ffdp:
            mock_nflverse.side_effect = DataNotAvailableError("NFLVerse unavailable")

            result = loader_service.import_weekly_data(
                2023, 1, source="nflverse", use_fallback=False
            )

            assert result.success is False
            assert len(result.errors) > 0
            mock_ffdp.assert_not_called()


def test_upsert_players_new(loader_service, mock_supabase_client):
    """Test upserting new players."""
    from src.database.models import PlayerCreate

    players = [
        PlayerCreate(name="Test Player", position="QB", team="KC"),
    ]

    # Mock: player doesn't exist
    select_response = MagicMock()
    select_response.data = []

    # Mock: insert succeeds
    insert_response = MagicMock()
    insert_response.data = [{"id": str(uuid4())}]

    mock_supabase_client.table().select().eq().eq().execute.return_value = (
        select_response
    )
    mock_supabase_client.table().insert().execute.return_value = insert_response

    player_id_map, new_count, updated_count = loader_service.upsert_players(players)

    assert new_count == 1
    assert updated_count == 0
    assert "Test Player" in player_id_map


def test_upsert_players_existing(loader_service, mock_supabase_client):
    """Test upserting existing players."""
    from src.database.models import PlayerCreate

    existing_id = uuid4()
    players = [
        PlayerCreate(name="Existing Player", position="RB", team="SF"),
    ]

    # Mock: player exists
    select_response = MagicMock()
    select_response.data = [
        {
            "id": str(existing_id),
            "name": "Existing Player",
            "position": "RB",
            "team": "DAL",  # Different team - should update
        }
    ]

    update_response = MagicMock()
    update_response.data = [{"id": str(existing_id)}]

    mock_supabase_client.table().select().eq().eq().execute.return_value = (
        select_response
    )
    mock_supabase_client.table().update().eq().execute.return_value = update_response

    player_id_map, new_count, updated_count = loader_service.upsert_players(players)

    assert new_count == 0
    assert updated_count == 1
    assert existing_id == player_id_map["Existing Player"]


def test_upsert_projections_new(loader_service, mock_supabase_client):
    """Test upserting new projections."""
    from src.database.models import ProjectionCreate
    from decimal import Decimal

    player_id = uuid4()
    projections = [
        ProjectionCreate(
            player_id=player_id,
            week=1,
            season=2023,
            source="nflverse",
            pass_yds=Decimal("300"),
            pass_tds=Decimal("2"),
        )
    ]

    # Mock: projection doesn't exist
    select_response = MagicMock()
    select_response.data = []

    insert_response = MagicMock()
    insert_response.data = [{"id": str(uuid4())}]

    mock_supabase_client.table().select().eq().eq().eq().eq().execute.return_value = (
        select_response
    )
    mock_supabase_client.table().insert().execute.return_value = insert_response

    new_count, updated_count = loader_service.upsert_projections(projections)

    assert new_count == 1
    assert updated_count == 0


def test_get_available_sources(loader_service):
    """Test getting available data sources."""
    with patch.object(
        loader_service.nflverse_loader, "get_available_columns"
    ) as mock_cols:
        mock_cols.return_value = ["player_name", "position"]

        sources = loader_service.get_available_sources()

        assert len(sources) >= 2
        source_names = [s["name"] for s in sources]
        assert "nflverse" in source_names
        assert "ffdp" in source_names


def test_import_weekly_data_unknown_source(loader_service):
    """Test error with unknown source."""
    result = loader_service.import_weekly_data(2023, 1, source="unknown")

    assert result.success is False
    assert len(result.errors) > 0
