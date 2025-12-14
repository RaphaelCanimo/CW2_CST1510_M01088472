import sqlite3
from typing import Any, Iterable, Optional, List
from pathlib import Path
import pandas as pd


class DatabaseManager:
    """Handles SQLite database connections and queries."""

    def __init__(self, db_path: str):
        self._db_path = db_path
        self._connection: sqlite3.Connection | None = None

    def connect(self) -> None:
        """Establish database connection."""
        if self._connection is None:
            self._connection = sqlite3.connect(self._db_path)

    def close(self) -> None:
        """Close database connection."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def execute_query(self, sql: str, params: Iterable[Any] = ()):
        """Execute a write query (INSERT, UPDATE, DELETE)."""
        if self._connection is None:
            self.connect()
        cur = self._connection.cursor()
        cur.execute(sql, tuple(params))
        self._connection.commit()
        return cur

    def fetch_one(self, sql: str, params: Iterable[Any] = ()):
        """Fetch a single row from the database."""
        if self._connection is None:
            self.connect()
        cur = self._connection.cursor()
        cur.execute(sql, tuple(params))
        return cur.fetchone()

    def fetch_all(self, sql: str, params: Iterable[Any] = ()):
        """Fetch all rows from the database."""
        if self._connection is None:
            self.connect()
        cur = self._connection.cursor()
        cur.execute(sql, tuple(params))
        return cur.fetchall()

    def fetch_dataframe(self, sql: str, params: Iterable[Any] = ()) -> pd.DataFrame:
        """Fetch results as a pandas DataFrame."""
        if self._connection is None:
            self.connect()
        return pd.read_sql_query(sql, self._connection, params=params)
