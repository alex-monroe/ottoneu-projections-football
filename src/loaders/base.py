"""
Base classes and interfaces for data loaders.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import pandas as pd
from datetime import datetime


@dataclass
class LoaderResult:
    """
    Standardized result from a data loader operation.

    Attributes:
        success: Whether the load operation succeeded
        data: The loaded data (typically a pandas DataFrame)
        source: Name of the data source
        metadata: Additional information about the load (row count, columns, etc.)
        errors: List of error messages if any occurred
        timestamp: When the data was loaded
    """
    success: bool
    data: Optional[pd.DataFrame]
    source: str
    metadata: Dict[str, Any]
    errors: List[str]
    timestamp: datetime


class BaseLoader(ABC):
    """
    Abstract base class for all data loaders.

    Defines the interface that all loaders must implement.
    """

    def __init__(self, source_name: str):
        """
        Initialize the loader.

        Args:
            source_name: Identifier for this data source
        """
        self.source_name = source_name

    @abstractmethod
    def load_data(self, **kwargs) -> pd.DataFrame:
        """
        Load data from the source.

        Args:
            **kwargs: Source-specific parameters (year, week, etc.)

        Returns:
            DataFrame containing the loaded data

        Raises:
            DataNotAvailableError: If data cannot be loaded
            LoaderError: For other loader-specific errors
        """
        pass

    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate that loaded data meets basic requirements.

        Args:
            df: DataFrame to validate

        Returns:
            True if valid, False otherwise
        """
        if df is None or df.empty:
            return False

        # Check for required columns (can be overridden by subclasses)
        required_cols = self.get_required_columns()
        missing_cols = set(required_cols) - set(df.columns)

        if missing_cols:
            return False

        return True

    def get_required_columns(self) -> List[str]:
        """
        Get list of required columns for this loader.

        Returns:
            List of required column names
        """
        return []  # Override in subclasses

    def transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply any necessary transformations to the data.

        Args:
            df: Raw DataFrame from source

        Returns:
            Transformed DataFrame
        """
        # Default: return as-is, override in subclasses if needed
        return df
