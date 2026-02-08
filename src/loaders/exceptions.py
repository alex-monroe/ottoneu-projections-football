"""
Custom exceptions for data loader operations.
"""


class LoaderError(Exception):
    """Base exception for all loader-related errors."""

    pass


class DataNotAvailableError(LoaderError):
    """Raised when requested data is not available from the source."""

    pass


class MappingError(LoaderError):
    """Raised when data transformation/mapping fails."""

    pass
