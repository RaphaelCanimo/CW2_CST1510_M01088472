import sqlite3
from pathlib import Path
import pandas as pd

# Define paths
DATA_DIR = Path("DATA")
DB_PATH = DATA_DIR / "intelligence_platform.db"


def connect_database(db_path=DB_PATH):
    """Connect to SQLite database."""
    return sqlite3.connect(str(db_path))


def load_csv_to_table(conn, csv_path, table_name):
    """
    Load a CSV file into a database table using pandas.

    Args:
        conn: Database connection
        csv_path: Path to CSV file
        table_name: Name of the target table

    Returns:
        int: Number of rows loaded
    """
    csv_path = Path(csv_path)

    if not csv_path.exists():
        print(f"CSV file not found: {csv_path}")
        return 0

    df = pd.read_csv(csv_path)
    row_count = len(df)

    df.to_sql(name=table_name, con=conn, if_exists='append', index=False)

    print(
        f"Loaded {row_count} rows from {csv_path.name} into {table_name}")
    return row_count


def load_all_csv_data(conn):
    """
    Load all CSV files into their respective tables.

    Args:
        conn: Database connection

    Returns:
        int: Total number of rows loaded
    """
    total_rows = 0

    csv_files = [
        (DATA_DIR / "cyber_incidents.csv", "cyber_incidents"),
        (DATA_DIR / "datasets_metadata.csv", "datasets_metadata"),
        (DATA_DIR / "it_tickets.csv", "it_tickets")
    ]

    for csv_path, table_name in csv_files:
        rows_loaded = load_csv_to_table(conn, csv_path, table_name)
        total_rows += rows_loaded

    print(f"\nTotal rows loaded: {total_rows}")
    return total_rows
