import bcrypt
import sqlite3
from pathlib import Path
from app.data.db import connect_database
from app.data.users import insert_user

DATA = Path("DATA")


def register_user(username, password, role="user"):
    """
    Register a new user in the database.

    Args:
        username: User's login name
        password: Plain text password (will be hashed)
        role: User role (default: 'user')

    Returns:
        bool: success
    """
    conn = connect_database()
    cursor = conn.cursor()

    # Check if user already exists
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False # , f"Username '{username}' already exists."

    # Hash the password
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    password_hash = hashed.decode('utf-8')

    # Insert new user
    insert_user(username, password_hash, role)

    return True  # , f"User '{username}' registered successfully!"


def login_user(username, password):
    """
    Authenticate a user against the database.

    Args:
        username: User's login name
        password: Plain text password to verify

    Returns:
        bool: success
    """
    conn = connect_database()
    cursor = conn.cursor()

    # Check both username and password_hash
    cursor.execute(
        "SELECT username, password_hash FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return False  # Username not found

    stored_hash = user[1]
    password_bytes = password.encode('utf-8')
    hash_bytes = stored_hash.encode('utf-8')

    if bcrypt.checkpw(password_bytes, hash_bytes):
        return True
    else:
        return False


def migrate_users_from_file(conn, filepath=DATA / "users.txt"):
    """
    Migrate users from users.txt to the database.

    Args:
        conn: Database connection
        filepath: Path to users.txt file
    """
    if not filepath.exists():
        print(f"⚠️  File not found: {filepath}")
        print("   No users to migrate.")
        return
    conn = connect_database()
    cursor = conn.cursor()
    migrated_count = 0

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Parse line: username,password_hash
            parts = line.split(',')
            if len(parts) >= 2:
                username = parts[0]
                password_hash = parts[1]

                # Insert user (ignore if already exists)
                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                        (username, password_hash, 'user')
                    )
                    if cursor.rowcount > 0:
                        migrated_count += 1
                except sqlite3.Error as e:
                    print(f"Error migrating user {username}: {e}")

    conn.commit()
    print(f"✅ Migrated {migrated_count} users from {filepath.name}")
