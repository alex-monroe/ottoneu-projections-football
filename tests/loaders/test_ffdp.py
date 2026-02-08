"""
Tests for FFDP loader.
"""
import pytest
import pandas as pd
import responses
from requests.exceptions import Timeout

from src.loaders.ffdp import FFDPLoader
from src.loaders.exceptions import DataNotAvailableError, LoaderError


@pytest.fixture
def ffdp_loader():
    """Create FFDP loader instance."""
    return FFDPLoader()


@responses.activate
def test_load_weekly_csv_success(ffdp_loader, sample_ffdp_data):
    """Test successful CSV loading."""
    url = "https://raw.githubusercontent.com/fantasydatapros/data/master/weekly/2023/week1.csv"

    # Mock the HTTP request
    responses.add(
        responses.GET,
        url,
        body=sample_ffdp_data.to_csv(index=False),
        status=200,
        content_type="text/csv",
    )

    df = ffdp_loader.load_weekly_csv(2023, 1)

    assert not df.empty
    assert len(df) == 3
    assert "Player" in df.columns or "player" in df.columns


@responses.activate
def test_load_weekly_csv_404(ffdp_loader):
    """Test handling of 404 (data not available)."""
    url = "https://raw.githubusercontent.com/fantasydatapros/data/master/weekly/2099/week1.csv"

    responses.add(responses.GET, url, status=404)

    with pytest.raises(DataNotAvailableError, match="404"):
        ffdp_loader.load_weekly_csv(2099, 1)


@responses.activate
def test_load_weekly_csv_timeout(ffdp_loader):
    """Test handling of timeout."""
    url = "https://raw.githubusercontent.com/fantasydatapros/data/master/weekly/2023/week1.csv"

    # Simulate timeout
    responses.add(responses.GET, url, body=Timeout("Connection timed out"))

    with pytest.raises(LoaderError, match="timeout"):
        ffdp_loader.load_weekly_csv(2023, 1)


@responses.activate
def test_load_weekly_csv_empty_file(ffdp_loader):
    """Test handling of empty CSV."""
    url = "https://raw.githubusercontent.com/fantasydatapros/data/master/weekly/2023/week1.csv"

    responses.add(responses.GET, url, body="", status=200, content_type="text/csv")

    with pytest.raises(DataNotAvailableError, match="empty"):
        ffdp_loader.load_weekly_csv(2023, 1)


def test_construct_url(ffdp_loader):
    """Test URL construction."""
    url = ffdp_loader._construct_url(2023, 1)

    expected = "https://raw.githubusercontent.com/fantasydatapros/data/master/weekly/2023/week1.csv"
    assert url == expected


def test_construct_url_different_weeks(ffdp_loader):
    """Test URL construction for different weeks."""
    url5 = ffdp_loader._construct_url(2022, 5)
    assert url5.endswith("/2022/week5.csv")

    url18 = ffdp_loader._construct_url(2023, 18)
    assert url18.endswith("/2023/week18.csv")


def test_validate_data_with_player_column(sample_ffdp_data):
    """Test validation with player identifier column."""
    loader = FFDPLoader()

    assert loader.validate_data(sample_ffdp_data) is True


def test_validate_data_without_player_column():
    """Test validation fails without player column."""
    df = pd.DataFrame({"PassYds": [300, 250], "RushYds": [50, 100]})

    loader = FFDPLoader()
    assert loader.validate_data(df) is False


def test_validate_data_empty_dataframe():
    """Test validation with empty DataFrame."""
    loader = FFDPLoader()

    assert loader.validate_data(pd.DataFrame()) is False


def test_load_data_calls_load_weekly_csv(ffdp_loader, sample_ffdp_data):
    """Test that load_data calls load_weekly_csv."""
    with responses.RequestsMock() as rsps:
        url = "https://raw.githubusercontent.com/fantasydatapros/data/master/weekly/2023/week1.csv"
        rsps.add(
            responses.GET,
            url,
            body=sample_ffdp_data.to_csv(index=False),
            status=200,
            content_type="text/csv",
        )

        df = ffdp_loader.load_data(year=2023, week=1)

        assert not df.empty
