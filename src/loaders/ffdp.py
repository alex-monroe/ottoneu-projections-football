"""
Fantasy Football Data Pros (FFDP) CSV loader.

Backup data source that fetches CSV files from GitHub repository.
"""
from typing import Optional
import pandas as pd
import requests
import logging
import time

from src.loaders.base import BaseLoader
from src.loaders.exceptions import DataNotAvailableError, LoaderError

logger = logging.getLogger(__name__)


class FFDPLoader(BaseLoader):
    """
    Loader for Fantasy Football Data Pros CSV files from GitHub.

    This serves as a backup data source.
    """

    BASE_URL = "https://raw.githubusercontent.com/fantasydatapros/data/master/weekly"
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds

    def __init__(self):
        """Initialize the FFDP loader."""
        super().__init__("ffdp")

    def load_data(self, year: int, week: int, **kwargs) -> pd.DataFrame:
        """
        Load data from FFDP.

        Args:
            year: NFL season year
            week: Week number (1-18)

        Returns:
            DataFrame with player statistics

        Raises:
            DataNotAvailableError: If data cannot be loaded
            LoaderError: For other errors
        """
        return self.load_weekly_csv(year, week)

    def load_weekly_csv(self, year: int, week: int) -> pd.DataFrame:
        """
        Load weekly CSV file from GitHub.

        Args:
            year: NFL season year
            week: Week number (1-18)

        Returns:
            DataFrame with player data

        Raises:
            DataNotAvailableError: If CSV doesn't exist (404)
            LoaderError: For network or parsing errors
        """
        url = self._construct_url(year, week)
        logger.info(f"Fetching FFDP data from: {url}")

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                response = requests.get(url, timeout=30)

                if response.status_code == 404:
                    raise DataNotAvailableError(
                        f"Data not available for {year} week {week} (404)"
                    )

                response.raise_for_status()

                # Parse CSV
                try:
                    df = pd.read_csv(pd.io.common.BytesIO(response.content))
                except pd.errors.EmptyDataError:
                    raise DataNotAvailableError(
                        f"CSV file is empty for {year} week {week}"
                    )

                if df.empty:
                    raise DataNotAvailableError(
                        f"CSV file is empty for {year} week {week}"
                    )

                logger.info(f"Loaded {len(df)} records from FFDP CSV")
                return df

            except DataNotAvailableError:
                raise

            except requests.exceptions.Timeout as e:
                logger.warning(f"Timeout on attempt {attempt}/{self.MAX_RETRIES}")
                if attempt == self.MAX_RETRIES:
                    raise LoaderError(f"Request timeout after {self.MAX_RETRIES} attempts") from e
                time.sleep(self.RETRY_DELAY)

            except requests.exceptions.RequestException as e:
                logger.error(f"Network error on attempt {attempt}: {str(e)}")
                if attempt == self.MAX_RETRIES:
                    raise LoaderError(f"Network error: {str(e)}") from e
                time.sleep(self.RETRY_DELAY)

            except pd.errors.ParserError as e:
                raise LoaderError(f"Failed to parse CSV: {str(e)}") from e

            except Exception as e:
                logger.error(f"Unexpected error loading FFDP data: {str(e)}")
                raise LoaderError(f"Failed to load FFDP data: {str(e)}") from e

        raise LoaderError("Failed to load data after all retries")

    def _construct_url(self, year: int, week: int) -> str:
        """
        Construct the GitHub URL for a specific week's data.

        Args:
            year: NFL season year
            week: Week number

        Returns:
            Full URL to the CSV file
        """
        return f"{self.BASE_URL}/{year}/week{week}.csv"

    def get_required_columns(self) -> list:
        """
        Get list of required columns for FFDP data.

        Returns:
            List of required column names
        """
        # FFDP CSVs may have varying column names, so we're lenient
        return []

    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate FFDP data structure.

        Args:
            df: DataFrame to validate

        Returns:
            True if valid, False otherwise
        """
        if df is None or df.empty:
            return False

        # Check for some player identifier column
        player_cols = ['Player', 'player', 'player_name', 'name']
        has_player_col = any(col in df.columns for col in player_cols)

        if not has_player_col:
            logger.warning("No player identifier column found in FFDP data")
            return False

        return True
