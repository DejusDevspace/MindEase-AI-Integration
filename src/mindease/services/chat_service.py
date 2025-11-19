import logging
from typing import Optional, Dict, List, Any

from groq import Groq

from mindease.config.settings import settings
from mindease.core.prompts import MINDEASE_SYSTEM_PROMPT
from mindease.db.repository import ConversationRepository

logger = logging.getLogger(__name__)


class ChatService:
    """Service for managing chatbot interactions with Groq API."""

    def __init__(self):
        """Initialize the chat service with Groq client."""
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE
        self.repository = ConversationRepository()

    async def chat(
        self,
        user_message: str,
        user_id: str,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a message to the chatbot and get a response.

        Args:
            user_message: The user's message
            user_id: Unique user identifier
            conversation_id: Optional conversation ID for multi-turn chat

        Returns:
            Dictionary with keys: 'message', 'conversation_id', and 'tokens_used'

        Raises:
            ValueError: If API call fails
        """
        try:
            # Get or create conversation
            if conversation_id is None:
                conv_id = self.repository.create_conversation(user_id)
            else:
                # Verify conversation exists and belongs to user
                if not self.repository.conversation_exists(conversation_id, user_id):
                    conv_id = self.repository.create_conversation(user_id, conversation_id)
                else:
                    conv_id = conversation_id

            # Get conversation history from database
            history = self.repository.get_conversation_history(conv_id, user_id)

            # Build messages for API call
            messages = history.copy()
            messages.append({"role": "user", "content": user_message})

            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": MINDEASE_SYSTEM_PROMPT},
                    *messages,
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )

            # Extract response
            assistant_message = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            # Store messages in database
            self.repository.add_message(
                conv_id, user_id, "user", user_message
            )
            self.repository.add_message(
                conv_id, user_id, "assistant", assistant_message, tokens_used
            )

            logger.info(
                f"Chat response generated for conversation {conv_id}, user {user_id}. Tokens: {tokens_used}"
            )

            return {
                "message": assistant_message,
                "conversation_id": conv_id,
                "tokens_used": tokens_used,
            }

        except Exception as e:
            logger.error(f"Error in chat service: {str(e)}")
            raise ValueError(f"Failed to generate response: {str(e)}")

    def clear_conversation(self, conversation_id: str, user_id: str) -> bool:
        """Clear conversation history."""
        return self.repository.clear_conversation(conversation_id, user_id)

    def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """Delete a conversation and all its messages."""
        return self.repository.delete_conversation(conversation_id, user_id)

    def get_user_conversations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all conversations for a user."""
        return self.repository.get_user_conversations(user_id)


# Global chat service instance
chat_service = ChatService()
