class BaseHudsonException(Exception):
    """Base class for Hudson exceptions."""


class WriteDatasetException(BaseHudsonException):
    """Exception raised when writing to a dataset fails."""
