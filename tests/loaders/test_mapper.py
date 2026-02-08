"""
Tests for data mapper.
"""
import pytest
from decimal import Decimal

from src.loaders.mapper import DataMapper
from src.loaders.exceptions import MappingError


def test_map_nflverse_players(sample_nflverse_data):
    """Test mapping NFLVerse data to player schema."""
    mapper = DataMapper()

    players = mapper.map_to_player_schema(sample_nflverse_data, "nflverse")

    assert len(players) == 3
    assert players[0].name == "Patrick Mahomes"
    assert players[0].position == "QB"
    assert players[0].team == "KC"

    assert players[1].name == "Christian McCaffrey"
    assert players[1].position == "RB"

    assert players[2].name == "Justin Jefferson"
    assert players[2].position == "WR"


def test_map_ffdp_players(sample_ffdp_data):
    """Test mapping FFDP data to player schema."""
    mapper = DataMapper()

    players = mapper.map_to_player_schema(sample_ffdp_data, "ffdp")

    assert len(players) == 3
    assert players[0].name == "Patrick Mahomes"
    assert players[0].position == "QB"
    assert players[0].team == "KC"


def test_map_nflverse_projections(sample_nflverse_data, sample_player_ids):
    """Test mapping NFLVerse data to projection schema."""
    mapper = DataMapper()

    projections = mapper.map_to_projection_schema(
        sample_nflverse_data,
        "nflverse",
        week=1,
        season=2023,
        player_id_map=sample_player_ids,
    )

    # Should have projections for all 3 players
    assert len(projections) == 3

    # Find Mahomes projection
    mahomes_proj = next(
        (p for p in projections if p.player_id == sample_player_ids["Patrick Mahomes"]),
        None,
    )

    assert mahomes_proj is not None
    assert mahomes_proj.week == 1
    assert mahomes_proj.season == 2023
    assert mahomes_proj.source == "nflverse"
    assert mahomes_proj.pass_yds == Decimal("320.0")
    assert mahomes_proj.pass_tds == Decimal("3.0")
    assert mahomes_proj.pass_ints == Decimal("1.0")


def test_map_projections_without_player_ids(sample_nflverse_data):
    """Test that projections without player IDs are skipped."""
    mapper = DataMapper()

    projections = mapper.map_to_projection_schema(
        sample_nflverse_data,
        "nflverse",
        week=1,
        season=2023,
        player_id_map=None,  # No player IDs
    )

    # Should have no projections without player IDs
    assert len(projections) == 0


def test_map_empty_dataframe():
    """Test mapping empty DataFrame."""
    import pandas as pd

    mapper = DataMapper()

    empty_df = pd.DataFrame()

    players = mapper.map_to_player_schema(empty_df, "nflverse")
    assert len(players) == 0

    projections = mapper.map_to_projection_schema(empty_df, "nflverse", 1, 2023)
    assert len(projections) == 0


def test_unknown_source_raises_error(sample_nflverse_data):
    """Test that unknown source raises error."""
    mapper = DataMapper()

    with pytest.raises(MappingError, match="Unknown data source"):
        mapper.map_to_player_schema(sample_nflverse_data, "unknown_source")


def test_decimal_conversion_handles_none():
    """Test that None values are handled correctly."""
    import pandas as pd

    mapper = DataMapper()

    assert mapper._to_decimal(None) is None
    assert mapper._to_decimal(pd.NA) is None
    assert mapper._to_decimal(float("nan")) is None


def test_decimal_conversion_handles_values():
    """Test decimal conversion with various values."""
    mapper = DataMapper()

    assert mapper._to_decimal(10) == Decimal("10")
    assert mapper._to_decimal(10.5) == Decimal("10.5")
    assert mapper._to_decimal("15.25") == Decimal("15.25")
