import pandas as pd
from app.data.db import connect_database


def insert_incident(conn, date, incident_type, severity, status, description, reported_by=None):
    """
    Insert a new cyber incident into the database.

    Args:
        conn: Database connection
        date: Incident date (YYYY-MM-DD)
        incident_type: Type of incident
        severity: Severity level
        status: Current status
        description: Incident description
        reported_by: Username of reporter (optional)

    Returns:
        int: ID of the inserted incident
    """
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO cyber_incidents 
        (date, incident_type, severity, status, description, reported_by)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (date, incident_type, severity, status, description, reported_by))

    conn.commit()
    incident_id = cursor.lastrowid
    conn.close()

    return incident_id


def get_all_incidents(conn):
    """
    Retrieve all incidents from the database.

    Returns:
        pandas.DataFrame: All incidents
    """
    conn = connect_database()

    df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents ORDER BY id DESC",
        conn
    )

    conn.close()
    return df


def update_incident_status(conn, incident_id, new_status):
    """
    Update the status of an incident.
    """
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE cyber_incidents SET assigned_to = ? WHERE id = ?",
        (new_status, incident_id)
    )

    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()

    return rows_affected


def delete_incident(conn, incident_id):
    """
    Delete an incident from the database.
    """
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM datasets_metadata WHERE id = ?",
        (incident_id,)
    )

    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()

    return rows_affected
