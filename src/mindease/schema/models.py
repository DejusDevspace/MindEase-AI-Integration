from typing import Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """User chat message."""

    user_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Unique user identifier",
    )
    content: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="The user's message",
    )
    conversation_id: Optional[str] = Field(
        None, description="Optional conversation ID for multi-turn chat"
    )


class ChatResponse(BaseModel):
    """Chatbot response."""

    message: str = Field(..., description="The chatbot's response")
    conversation_id: str = Field(
        ..., description="Conversation ID for tracking multi-turn chat"
    )
    tokens_used: int = Field(..., description="Number of tokens used in response")


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
