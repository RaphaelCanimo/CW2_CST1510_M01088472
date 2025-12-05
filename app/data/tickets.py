import pandas as pd
from app.data.db import connect_database


def insert_ticket(conn, ticket_id, priority, status, category, subject, description,
                  created_date, resolved_date=None, assigned_to=None):
    """
    Insert a new IT ticket into the database.

    Args:
        ticket_id: Unique ticket ID (e.g., 'TKT-001')
        priority: Priority level (e.g., 'Critical', 'High', 'Medium', 'Low')
        status: Current status (e.g., 'Open', 'In Progress', 'Resolved', 'Closed')
        category: Ticket category (e.g., 'Hardware', 'Software', 'Network')
        subject: Brief description of the issue
        description: Detailed description
        created_date: Date created (YYYY-MM-DD)
        resolved_date: Date resolved (YYYY-MM-DD)
        assigned_to: Username of assigned person

    Returns:
        int: ID of the inserted ticket
    """
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO it_tickets 
        (ticket_id, priority, status, category, subject, description, 
         created_date, resolved_date, assigned_to)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (ticket_id, priority, status, category, subject, description,
          created_date, resolved_date, assigned_to))

    conn.commit()
    ticket_db_id = cursor.lastrowid
    conn.close()

    return ticket_db_id


def get_all_tickets(conn):
    """
    Get all IT tickets as DataFrame.

    Returns:
        pandas.DataFrame: All tickets ordered by ID descending
    """
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM it_tickets ORDER BY id DESC",
        conn
    )
    conn.close()
    return df


def update_ticket_status(conn, ticket_id, new_status):
    """
    Update the status of a ticket.

    Args:
        ticket_id: Unique ticket identifier (e.g., 'TKT-001')
        new_status: New status value

    Returns:
        int: Number of rows affected
    """
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE it_tickets SET status = ? WHERE id = ?",
        (new_status, ticket_id)
    )

    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()

    return rows_affected


def update_ticket_assignment(conn, ticket_id, assigned_to):
    """
    Assign a ticket to a user.

    Args:
        ticket_id: Unique ticket identifier
        assigned_to: Username to assign the ticket to

    Returns:
        int: Number of rows affected
    """
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE it_tickets SET assigned_to = ? WHERE id = ?",
        (assigned_to, ticket_id)
    )

    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()

    return rows_affected


def resolve_ticket(conn, ticket_id, resolved_date):
    """
    Mark a ticket as resolved and set the resolved date.

    Args:
        ticket_id: Unique ticket identifier
        resolved_date: Date resolved (YYYY-MM-DD)

    Returns:
        int: Number of rows affected
    """
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE it_tickets SET status = 'Resolved', resolved_date = ? WHERE id = ?",
        (resolved_date, ticket_id)
    )

    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()

    return rows_affected


def delete_ticket(conn, ticket_id):
    """
    Delete a ticket from the database.

    Args:
        ticket_id: Unique ticket identifier to delete

    Returns:
        int: Number of rows affected
    """
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM it_tickets WHERE id = ?",
        (ticket_id,)
    )

    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()

    return rows_affected
