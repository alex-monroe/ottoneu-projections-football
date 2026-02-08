"""
NFLVerse data loader using nfl_data_py library.

This is the primary data source for the application.
"""
from typing import List, Optional
import pandas as pd
import logging

from src.loaders.base import BaseLoader
from src.loaders.exceptions import DataNotAvailableError, LoaderError

logger = logging.getLogger(__name__)


class NFLVerseLoader(BaseLoader):
    """
    Loader for NFLVerse data using the nfl_data_py library.

    This provides access to historical NFL player statistics from the nflverse project.
    """

    def __init__(self):
        """Initialize the NFLVerse loader."""
        super().__init__("nflverse")

        # Import here to avoid dependency issues if package not installed
        try:
            import nfl_data_py as nfl

            self.nfl = nfl
        except ImportError as e:
            raise LoaderError(
                "nfl_data_py package not installed. "
                "Install with: pip install nfl-data-py"
            ) from e

    def load_data(self, year: int, week: Optional[int] = None) -> pd.DataFrame:
        """
        Load data from NFLVerse.

        Args:
            year: NFL season year
            week: Optional week number (1-18). If None, loads entire season.

        Returns:
            DataFrame with player statistics

        Raises:
            DataNotAvailableError: If data cannot be loaded
            LoaderError: For other errors
        """
        if week is not None:
            return self.load_weekly_data(year, week)
        else:
            return self.load_season_data(year)

    def load_weekly_data(self, year: int, week: int) -> pd.DataFrame:
        """
        Load weekly player statistics.

        Args:
            year: NFL season year (e.g., 2023)
            week: Week number (1-18)

        Returns:
            DataFrame with weekly player stats

        Raises:
            DataNotAvailableError: If data doesn't exist for this year/week
            LoaderError: For other errors
        """
        try:
            logger.info(f"Loading NFLVerse data for {year} week {week}")

            # Load weekly data for the specified year
            df = self.nfl.import_weekly_data(years=[year])

            if df is None or df.empty:
                raise DataNotAvailableError(f"No data available for year {year}")

            # Filter to specific week
            if "week" in df.columns:
                df = df[df["week"] == week]
            else:
                raise LoaderError("'week' column not found in NFLVerse data")

            if df.empty:
                raise DataNotAvailableError(f"No data available for {year} week {week}")

            logger.info(f"Loaded {len(df)} player records from NFLVerse")
            return df

        except DataNotAvailableError:
            raise
        except Exception as e:
            logger.error(f"Error loading NFLVerse data: {str(e)}")
            raise LoaderError(f"Failed to load NFLVerse data: {str(e)}") from e

    def load_season_data(self, year: int) -> pd.DataFrame:
        """
        Load all weekly data for an entire season.

        Args:
            year: NFL season year

        Returns:
            DataFrame with all weekly stats for the season

        Raises:
            DataNotAvailableError: If data doesn't exist
            LoaderError: For other errors
        """
        try:
            logger.info(f"Loading NFLVerse data for entire {year} season")

            df = self.nfl.import_weekly_data(years=[year])

            if df is None or df.empty:
                raise DataNotAvailableError(f"No data available for season {year}")

            logger.info(f"Loaded {len(df)} player records for {year} season")
            return df

        except DataNotAvailableError:
            raise
        except Exception as e:
            logger.error(f"Error loading NFLVerse season data: {str(e)}")
            raise LoaderError(f"Failed to load NFLVerse data: {str(e)}") from e

    def get_available_columns(self) -> List[str]:
        """
        Get list of available columns in NFLVerse data.

        Returns:
            List of column names
        """
        try:
            cols = self.nfl.see_weekly_cols()
            return cols if cols else []
        except Exception as e:
            logger.warning(f"Could not retrieve NFLVerse columns: {str(e)}")
            return []

    def get_required_columns(self) -> List[str]:
        """
        Get list of required columns for this loader.

        Returns:
            List of required column names
        """
        return [
            "player_name",
            "position",
            "week",
            "season",
        ]

    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate NFLVerse data structure.

        Args:
            df: DataFrame to validate

        Returns:
            True if valid, False otherwise
        """
        if not super().validate_data(df):
            return False

        # Additional NFLVerse-specific validation
        # Check that we have some stat columns
        stat_cols = [
            "passing_yards",
            "rushing_yards",
            "receiving_yards",
            "completions",
            "attempts",
            "carries",
            "receptions",
        ]

        has_stats = any(col in df.columns for col in stat_cols)
        if not has_stats:
            logger.warning("No recognized stat columns found in data")
            return False

        return True
