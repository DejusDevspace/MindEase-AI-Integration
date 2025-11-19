import logging
import uuid
from typing import Optional, Dict, List, Any

from groq import Groq

from mindease.config.settings import settings
from mindease.core.prompts import MINDEASE_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class ChatService:
    """Service for managing chatbot interactions with Groq API."""

    def __init__(self):
        """Initialize the chat service with Groq client."""
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE
        # In-memory conversation history (we would replace with a db or equivalent later on.)
        self.conversations: Dict[str, List] = {}

    def generate_conversation_id(self) -> str:
        """Generate a unique conversation ID."""
        return str(uuid.uuid4())

    def get_or_create_conversation(self, conversation_id: Optional[str]) -> str:
        """Get existing conversation history or create new one."""
        if conversation_id is None:
            conversation_id = self.generate_conversation_id()
            self.conversations[conversation_id] = []
        elif conversation_id not in self.conversations:
            self.conversations[conversation_id] = []

        return conversation_id

    def _build_messages(self, conversation_id: str, user_message: str) -> List:
        """Build message list for API call including conversation history."""
        messages = self.conversations[conversation_id].copy()
        messages.append({"role": "user", "content": user_message})
        return messages

    async def chat(
        self, user_message: str, conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a message to the chatbot and get a response.

        Args:
            user_message: The user's message
            conversation_id: Optional conversation ID for multi-turn chat

        Returns:
            Dictionary with keys: 'message', 'conversation_id', and 'tokens_used'

        Raises:
            ValueError: If API call fails
        """
        try:
            # Get or create conversation
            conv_id = self.get_or_create_conversation(conversation_id)

            # Build messages with history
            messages = self._build_messages(conv_id, user_message)

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

            # Update conversation history
            self.conversations[conv_id].append(
                {"role": "user", "content": user_message}
            )
            self.conversations[conv_id].append(
                {"role": "assistant", "content": assistant_message}
            )

            logger.info(
                f"Chat response generated for conversation {conv_id}. Tokens: {tokens_used}"
            )

            return {
                "message": assistant_message,
                "conversation_id": conv_id,
                "tokens_used": tokens_used
            }

        except Exception as e:
            logger.error(f"Error in chat service: {str(e)}")
            raise ValueError(f"Failed to generate response: {str(e)}")

    def clear_conversation(self, conversation_id: str) -> bool:
        """Clear conversation history."""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info(f"Cleared conversation {conversation_id}")
            return True
        return False


# Global chat service instance
chat_service = ChatService()
