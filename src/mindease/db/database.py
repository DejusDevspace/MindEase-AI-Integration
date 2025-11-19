import sqlite3
import logging
import os
from pathlib import Path
from contextlib import contextmanager
from typing import Generator

logger = logging.getLogger(__name__)

# Database path - store in data folder in project root
DB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "mindease.db"


def init_db(reset: bool = False) -> None:
    """
    Initialize SQLite database with required tables.
    
    Args:
        reset: If True, drop and recreate tables. If False, create only if not exists.
               Also checks DB_RESET env variable if reset is not explicitly set.
    """
    # Ensure data directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check environment variable for reset flag
    reset = reset or os.getenv("DB_RESET", "").lower() == "true"

    # Drop tables if reset is True
    if reset:
        logger.info("Resetting database tables...")
        cursor.execute("DROP TABLE IF EXISTS messages")
        cursor.execute("DROP TABLE IF EXISTS conversations")

    # Create conversations table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL UNIQUE,
            user_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # Create messages table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
            content TEXT NOT NULL,
            tokens_used INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id),
            FOREIGN KEY (user_id) REFERENCES conversations(user_id)
        )
        """
    )

    # Create indexes for faster queries
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_user_id ON conversations(user_id)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_conversation_id ON messages(conversation_id)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_user_messages ON messages(user_id)"
    )

    conn.commit()
    conn.close()
    logger.info(f"Database initialized at {DB_PATH}")


@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database connections with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
