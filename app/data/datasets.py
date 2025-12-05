import pandas as pd
from app.data.db import connect_database


def insert_dataset(conn, dataset_name, category, source, last_updated, record_count, file_size_mb):
    """
    Insert a new dataset into the database.

    Args:
        dataset_name: Name of the dataset
        category: Category (e.g., 'Threat Intelligence', 'Network Logs')
        source: Origin of the dataset
        last_updated: Last update date (YYYY-MM-DD)
        record_count: Number of records in the dataset
        file_size_mb: File size in megabytes

    Returns:
        int: ID of the inserted dataset
    """
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO datasets_metadata 
        (dataset_name, category, source, last_updated, record_count, file_size_mb)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (dataset_name, category, source, last_updated, record_count, file_size_mb))

    conn.commit()
    dataset_id = cursor.lastrowid
    conn.close()

    return dataset_id


def get_all_datasets(conn):
    """
    Get all datasets as DataFrame.

    Returns:
        pandas.DataFrame: All datasets ordered by ID descending
    """
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM datasets_metadata ORDER BY id DESC",
        conn
    )
    conn.close()
    return df


def update_dataset_record_count(conn, dataset_id, new_record_count):
    """
    Update the record count for a dataset.

    Args:
        dataset_id: ID of the dataset to update
        new_record_count: New record count

    Returns:
        int: Number of rows affected (1 if successful, 0 if not found)
    """
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE datasets_metadata SET record_count = ? WHERE id = ?",
        (new_record_count, dataset_id)
    )

    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()

    return rows_affected


def update_dataset_last_updated(conn, dataset_id, new_date):
    """
    Update the last_updated date for a dataset.

    Args:
        dataset_id: ID of the dataset to update
        new_date: New last updated date (YYYY-MM-DD)

    Returns:
        int: Number of rows affected
    """
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE datasets_metadata SET last_updated = ? WHERE id = ?",
        (new_date, dataset_id)
    )

    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()

    return rows_affected


def delete_dataset(conn, dataset_id):
    """
    Delete a dataset from the database.

    Args:
        dataset_id: ID of the dataset to delete

    Returns:
        int: Number of rows affected (1 if successful, 0 if not found)
    """
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM datasets_metadata WHERE id = ?",
        (dataset_id,)
    )

    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()

    return rows_affected
