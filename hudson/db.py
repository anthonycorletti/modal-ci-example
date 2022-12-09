from contextlib import contextmanager
from typing import Generator, Optional

import duckdb


def _db(
    database_filename: Optional[str] = None,
    read_only: bool = False,
) -> duckdb.DuckDBPyConnection:
    """Return a DuckDB database connection."""
    if not database_filename:
        database_filename = "hudson.db"
    return duckdb.connect(database=database_filename, read_only=read_only)


@contextmanager
def db(database_filename: Optional[str] = None, read_only: bool = False) -> Generator:
    """Context manager for a DuckDB database connection."""
    db = _db(database_filename=database_filename, read_only=read_only)
    try:
        yield db
    finally:
        db.close()
