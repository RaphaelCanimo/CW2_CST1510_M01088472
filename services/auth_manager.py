from typing import Optional
from models.user import User
import bcrypt
from pathlib import Path


class AuthManager:
    """Handles user registration and login with bcrypt password hashing."""

    def __init__(self, db):
        """
        Initialize AuthManager with a DatabaseManager instance.
        
        Args:
            db: DatabaseManager instance
        """
        self._db = db

    def register_user(self, username: str, password: str, role: str = "user") -> bool:
        """
        Register a new user with bcrypt password hashing.

        Args:
            username: Desired username
            password: Plain text password (will be hashed with bcrypt)
            role: User role (default: 'user')

        Returns:
            bool: True if successful, False if username exists
        """
        # Check if user already exists
        existing = self._db.fetch_one(
            "SELECT username FROM users WHERE username = ?",
            (username,)
        )

        if existing is not None:
            return False

        # Hash the password with bcrypt
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        password_hash = hashed.decode('utf-8')

        # Insert new user
        self._db.execute_query(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role),
        )
        return True

    def login_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user with bcrypt password verification.

        Args:
            username: Username to authenticate
            password: Plain text password to verify

        Returns:
            User instance if successful, None otherwise
        """
        row = self._db.fetch_one(
            "SELECT username, password_hash, role FROM users WHERE username = ?",
            (username,),
        )

        if row is None:
            return None

        username_db, password_hash_db, role_db = row

        # Verify password with bcrypt
        password_bytes = password.encode('utf-8')
        hash_bytes = password_hash_db.encode('utf-8')

        if bcrypt.checkpw(password_bytes, hash_bytes):
            return User(username_db, password_hash_db, role_db)
        return None