"""
Tests for NFLVerse loader.
"""
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from src.loaders.exceptions import DataNotAvailableError


@pytest.fixture
def mock_nfl_data_py(sample_nflverse_data):
    """Mock the nfl_data_py module."""
    mock_nfl = MagicMock()
    mock_nfl.import_weekly_data.return_value = sample_nflverse_data
    mock_nfl.see_weekly_cols.return_value = list(sample_nflverse_data.columns)
    return mock_nfl


def test_load_weekly_data_success(sample_nflverse_data):
    """Test successful loading of weekly data."""
    mock_nfl = MagicMock()
    mock_nfl.import_weekly_data.return_value = sample_nflverse_data

    from src.loaders.nflverse import NFLVerseLoader

    loader = NFLVerseLoader()
    loader.nfl = mock_nfl  # Replace with mock

    df = loader.load_weekly_data(2023, 1)

    assert not df.empty
    assert len(df) == 3
    mock_nfl.import_weekly_data.assert_called_once_with(years=[2023])


def test_load_weekly_data_filters_by_week(sample_nflverse_data):
    """Test that weekly data is filtered to specific week."""
    # Add multiple weeks
    multi_week_data = pd.concat(
        [sample_nflverse_data, sample_nflverse_data.assign(week=2)]
    )
    mock_nfl = MagicMock()
    mock_nfl.import_weekly_data.return_value = multi_week_data

    from src.loaders.nflverse import NFLVerseLoader

    loader = NFLVerseLoader()
    loader.nfl = mock_nfl

    df = loader.load_weekly_data(2023, 1)

    # Should only have week 1 data
    assert all(df["week"] == 1)
    assert len(df) == 3


def test_load_weekly_data_no_data_for_week(sample_nflverse_data):
    """Test error when no data exists for requested week."""
    mock_nfl = MagicMock()
    mock_nfl.import_weekly_data.return_value = sample_nflverse_data

    from src.loaders.nflverse import NFLVerseLoader

    loader = NFLVerseLoader()
    loader.nfl = mock_nfl

    with pytest.raises(DataNotAvailableError, match="No data available"):
        loader.load_weekly_data(2023, 18)


def test_load_weekly_data_empty_dataframe():
    """Test error when API returns empty DataFrame."""
    mock_nfl = MagicMock()
    mock_nfl.import_weekly_data.return_value = pd.DataFrame()

    from src.loaders.nflverse import NFLVerseLoader

    loader = NFLVerseLoader()
    loader.nfl = mock_nfl

    with pytest.raises(DataNotAvailableError, match="No data available"):
        loader.load_weekly_data(2023, 1)


def test_load_season_data(sample_nflverse_data):
    """Test loading entire season data."""
    mock_nfl = MagicMock()
    mock_nfl.import_weekly_data.return_value = sample_nflverse_data

    from src.loaders.nflverse import NFLVerseLoader

    loader = NFLVerseLoader()
    loader.nfl = mock_nfl

    df = loader.load_season_data(2023)

    assert not df.empty
    mock_nfl.import_weekly_data.assert_called_once_with(years=[2023])


def test_get_available_columns():
    """Test getting available columns."""
    expected_cols = ["player_name", "position", "passing_yards"]
    mock_nfl = MagicMock()
    mock_nfl.see_weekly_cols.return_value = expected_cols

    from src.loaders.nflverse import NFLVerseLoader

    loader = NFLVerseLoader()
    loader.nfl = mock_nfl

    cols = loader.get_available_columns()

    assert cols == expected_cols
    mock_nfl.see_weekly_cols.assert_called_once()


def test_validate_data_success(sample_nflverse_data):
    """Test data validation with valid data."""
    from src.loaders.nflverse import NFLVerseLoader

    loader = NFLVerseLoader()

    assert loader.validate_data(sample_nflverse_data) is True


def test_validate_data_missing_columns():
    """Test validation fails with missing columns."""
    df = pd.DataFrame({"some_column": [1, 2, 3]})

    from src.loaders.nflverse import NFLVerseLoader

    loader = NFLVerseLoader()

    assert loader.validate_data(df) is False


def test_load_data_calls_weekly_with_week():
    """Test that load_data calls load_weekly_data when week is provided."""
    from src.loaders.nflverse import NFLVerseLoader

    loader = NFLVerseLoader()

    with patch.object(loader, "load_weekly_data") as mock_weekly:
        mock_weekly.return_value = pd.DataFrame()
        loader.load_data(year=2023, week=1)

        mock_weekly.assert_called_once_with(2023, 1)


def test_load_data_calls_season_without_week():
    """Test that load_data calls load_season_data when week is None."""
    from src.loaders.nflverse import NFLVerseLoader

    loader = NFLVerseLoader()

    with patch.object(loader, "load_season_data") as mock_season:
        mock_season.return_value = pd.DataFrame()
        loader.load_data(year=2023, week=None)

        mock_season.assert_called_once_with(2023)
