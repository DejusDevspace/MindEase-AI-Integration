import logging
import uuid
from typing import Optional, List, Dict, Any

from mindease.db.database import get_db_connection

logger = logging.getLogger(__name__)


class ConversationRepository:
    """Repository for managing conversations and messages."""

    @staticmethod
    def create_conversation(user_id: str, conversation_id: Optional[str] = None) -> str:
        """
        Create a new conversation for a user.

        Args:
            user_id: Unique user identifier
            conversation_id: Optional conversation ID (will be generated if not provided)

        Returns:
            The conversation ID
        """
        if conversation_id is None:
            conversation_id = str(uuid.uuid4())

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO conversations (conversation_id, user_id)
                VALUES (?, ?)
                """,
                (conversation_id, user_id),
            )
            conn.commit()

        logger.info(f"Created conversation {conversation_id} for user {user_id}")
        return conversation_id

    @staticmethod
    def conversation_exists(conversation_id: str, user_id: str) -> bool:
        """
        Check if a conversation exists for a user.

        Args:
            conversation_id: Conversation ID to check
            user_id: User ID that owns the conversation

        Returns:
            True if conversation exists and belongs to user, False otherwise
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 1 FROM conversations
                WHERE conversation_id = ? AND user_id = ?
                """,
                (conversation_id, user_id),
            )
            return cursor.fetchone() is not None

    @staticmethod
    def add_message(
        conversation_id: str,
        user_id: str,
        role: str,
        content: str,
        tokens_used: Optional[int] = None,
    ) -> None:
        """
        Add a message to a conversation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID
            role: Message role ('user' or 'assistant')
            content: Message content
            tokens_used: Optional token count for the message
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO messages (conversation_id, user_id, role, content, tokens_used)
                VALUES (?, ?, ?, ?, ?)
                """,
                (conversation_id, user_id, role, content, tokens_used),
            )
            conn.commit()

        logger.debug(f"Added {role} message to conversation {conversation_id}")

    @staticmethod
    def get_conversation_history(conversation_id: str, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all messages in a conversation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID

        Returns:
            List of message dictionaries with 'role' and 'content' keys
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT role, content FROM messages
                WHERE conversation_id = ? AND user_id = ?
                ORDER BY created_at ASC
                """,
                (conversation_id, user_id),
            )
            rows = cursor.fetchall()

        return [{"role": row["role"], "content": row["content"]} for row in rows]

    @staticmethod
    def get_user_conversations(user_id: str) -> List[Dict[str, Any]]:
        """
        Get all conversations for a user.

        Args:
            user_id: User ID

        Returns:
            List of conversation dictionaries
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT conversation_id, created_at, updated_at FROM conversations
                WHERE user_id = ?
                ORDER BY updated_at DESC
                """,
                (user_id,),
            )
            rows = cursor.fetchall()

        return [
            {
                "conversation_id": row["conversation_id"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }
            for row in rows
        ]

    @staticmethod
    def clear_conversation(conversation_id: str, user_id: str) -> bool:
        """
        Clear all messages from a conversation (but keep conversation record).

        Args:
            conversation_id: Conversation ID
            user_id: User ID

        Returns:
            True if successful, False if conversation not found
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Check if conversation exists
            cursor.execute(
                """
                SELECT 1 FROM conversations
                WHERE conversation_id = ? AND user_id = ?
                """,
                (conversation_id, user_id),
            )
            if not cursor.fetchone():
                return False

            # Delete messages
            cursor.execute(
                """
                DELETE FROM messages
                WHERE conversation_id = ? AND user_id = ?
                """,
                (conversation_id, user_id),
            )
            conn.commit()

        logger.info(f"Cleared conversation {conversation_id} for user {user_id}")
        return True

    @staticmethod
    def delete_conversation(conversation_id: str, user_id: str) -> bool:
        """
        Delete a conversation and all its messages.

        Args:
            conversation_id: Conversation ID
            user_id: User ID

        Returns:
            True if successful, False if conversation not found
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Check if conversation exists
            cursor.execute(
                """
                SELECT 1 FROM conversations
                WHERE conversation_id = ? AND user_id = ?
                """,
                (conversation_id, user_id),
            )
            if not cursor.fetchone():
                return False

            # Delete messages first (foreign key)
            cursor.execute(
                """
                DELETE FROM messages
                WHERE conversation_id = ? AND user_id = ?
                """,
                (conversation_id, user_id),
            )

            # Delete conversation
            cursor.execute(
                """
                DELETE FROM conversations
                WHERE conversation_id = ? AND user_id = ?
                """,
                (conversation_id, user_id),
            )
            conn.commit()

        logger.info(f"Deleted conversation {conversation_id} for user {user_id}")
        return True
