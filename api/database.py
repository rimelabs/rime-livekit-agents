"""
Database Module

Handles storage of search results and chat history using SQLite.
"""

import os
import json
import logging
import aiosqlite
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class Database:
    """Database handler for profile search application."""

    def __init__(self, db_path: str = "database/profile_search.db"):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.db = None

        # Ensure database directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    async def initialize(self):
        """Initialize database connection and create tables."""
        logger.info(f"Initializing database at {self.db_path}")

        self.db = await aiosqlite.connect(self.db_path)
        self.db.row_factory = aiosqlite.Row

        await self._create_tables()
        logger.info("Database initialized successfully")

    async def _create_tables(self):
        """Create database tables if they don't exist."""

        # Searches table
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS searches (
                search_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                search_query TEXT NOT NULL,
                results TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Chat messages table
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                search_id TEXT,
                user_message TEXT NOT NULL,
                assistant_message TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Sessions table
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_activity DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes
        await self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_searches_session
            ON searches(session_id)
        """)

        await self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_session
            ON chat_messages(session_id)
        """)

        await self.db.commit()

    async def save_search(
        self,
        search_id: str,
        session_id: str,
        search_query: Dict[str, Any],
        results: Dict[str, Any]
    ) -> bool:
        """
        Save search results to database.

        Args:
            search_id: Unique search identifier
            session_id: Session identifier
            search_query: Search parameters
            results: Search results data

        Returns:
            True if successful
        """
        try:
            # Ensure session exists
            await self._ensure_session(session_id)

            await self.db.execute("""
                INSERT INTO searches (search_id, session_id, search_query, results, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                search_id,
                session_id,
                json.dumps(search_query),
                json.dumps(results),
                datetime.utcnow().isoformat()
            ))

            await self.db.commit()
            logger.info(f"Saved search {search_id} for session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving search: {e}", exc_info=True)
            return False

    async def get_search(self, search_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve search results by ID.

        Args:
            search_id: Search identifier

        Returns:
            Search data or None if not found
        """
        try:
            async with self.db.execute("""
                SELECT * FROM searches WHERE search_id = ?
            """, (search_id,)) as cursor:
                row = await cursor.fetchone()

                if row:
                    return {
                        "search_id": row["search_id"],
                        "session_id": row["session_id"],
                        "search_query": json.loads(row["search_query"]),
                        "results": json.loads(row["results"]),
                        "timestamp": row["timestamp"],
                        "created_at": row["created_at"]
                    }

                return None

        except Exception as e:
            logger.error(f"Error retrieving search: {e}", exc_info=True)
            return None

    async def save_chat_message(
        self,
        session_id: str,
        user_message: str,
        assistant_message: str,
        search_id: Optional[str] = None
    ) -> bool:
        """
        Save a chat message exchange.

        Args:
            session_id: Session identifier
            user_message: User's message
            assistant_message: Assistant's response
            search_id: Related search ID (optional)

        Returns:
            True if successful
        """
        try:
            # Ensure session exists
            await self._ensure_session(session_id)

            await self.db.execute("""
                INSERT INTO chat_messages
                (session_id, search_id, user_message, assistant_message, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_id,
                search_id,
                user_message,
                assistant_message,
                datetime.utcnow().isoformat()
            ))

            # Update session last activity
            await self.db.execute("""
                UPDATE sessions
                SET last_activity = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, (session_id,))

            await self.db.commit()
            logger.info(f"Saved chat message for session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving chat message: {e}", exc_info=True)
            return False

    async def get_chat_history(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieve chat history for a session.

        Args:
            session_id: Session identifier
            limit: Maximum number of messages to retrieve

        Returns:
            List of chat messages
        """
        try:
            async with self.db.execute("""
                SELECT * FROM chat_messages
                WHERE session_id = ?
                ORDER BY created_at ASC
                LIMIT ?
            """, (session_id, limit)) as cursor:
                rows = await cursor.fetchall()

                return [
                    {
                        "id": row["id"],
                        "session_id": row["session_id"],
                        "search_id": row["search_id"],
                        "user_message": row["user_message"],
                        "assistant_message": row["assistant_message"],
                        "timestamp": row["timestamp"],
                        "created_at": row["created_at"]
                    }
                    for row in rows
                ]

        except Exception as e:
            logger.error(f"Error retrieving chat history: {e}", exc_info=True)
            return []

    async def get_full_session(self, session_id: str) -> Dict[str, Any]:
        """
        Get complete session data including searches and chat history.

        Args:
            session_id: Session identifier

        Returns:
            Session data with searches and chat history
        """
        try:
            # Get session info
            async with self.db.execute("""
                SELECT * FROM sessions WHERE session_id = ?
            """, (session_id,)) as cursor:
                session_row = await cursor.fetchone()

            if not session_row:
                return {
                    "session_id": session_id,
                    "exists": False
                }

            # Get searches
            async with self.db.execute("""
                SELECT search_id, search_query, timestamp
                FROM searches
                WHERE session_id = ?
                ORDER BY created_at ASC
            """, (session_id,)) as cursor:
                search_rows = await cursor.fetchall()
                searches = [
                    {
                        "search_id": row["search_id"],
                        "search_query": json.loads(row["search_query"]),
                        "timestamp": row["timestamp"]
                    }
                    for row in search_rows
                ]

            # Get chat history
            chat_history = await self.get_chat_history(session_id)

            return {
                "session_id": session_id,
                "exists": True,
                "created_at": session_row["created_at"],
                "last_activity": session_row["last_activity"],
                "searches": searches,
                "chat_history": chat_history
            }

        except Exception as e:
            logger.error(f"Error retrieving session: {e}", exc_info=True)
            return {
                "session_id": session_id,
                "exists": False,
                "error": str(e)
            }

    async def _ensure_session(self, session_id: str):
        """Ensure a session exists in the database."""
        await self.db.execute("""
            INSERT OR IGNORE INTO sessions (session_id) VALUES (?)
        """, (session_id,))

    async def close(self):
        """Close database connection."""
        if self.db:
            await self.db.close()
            logger.info("Database connection closed")


# Example usage and testing
async def test_database():
    """Test database operations."""
    db = Database("test_profile_search.db")
    await db.initialize()

    # Test save search
    search_id = "test_search_1"
    session_id = "test_session_1"

    await db.save_search(
        search_id=search_id,
        session_id=session_id,
        search_query={"name": "Test Person"},
        results={"linkedin": {"profiles": []}}
    )

    # Test retrieve search
    search = await db.get_search(search_id)
    print(f"Retrieved search: {search['search_id']}")

    # Test save chat message
    await db.save_chat_message(
        session_id=session_id,
        user_message="Hello",
        assistant_message="Hi there!",
        search_id=search_id
    )

    # Test retrieve chat history
    history = await db.get_chat_history(session_id)
    print(f"Chat history: {len(history)} messages")

    # Test get full session
    session = await db.get_full_session(session_id)
    print(f"Session: {session['session_id']}, {len(session['searches'])} searches")

    await db.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_database())
