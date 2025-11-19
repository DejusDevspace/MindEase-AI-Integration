import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from mindease.services.chat_service import chat_service
from mindease.schema.models import ChatMessage, ChatResponse
from mindease.db.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle app startup and shutdown."""
    logger.info("MindEase chatbot starting up...")
    init_db()
    yield
    logger.info("MindEase chatbot shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="MindEase Chatbot API",
    description="AI-powered chatbot for academic stress and emotional well-being",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "mindease-chatbot"}


@app.post("/v1/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatMessage) -> ChatResponse:
    """
    Chat endpoint for MindEase chatbot.

    Args:
        request: ChatMessage containing user_id, message content and optional conversation_id

    Returns:
        ChatResponse with assistant message and conversation ID

    Raises:
        HTTPException: If chat generation fails
    """
    try:
        logger.info(
            f"Received chat request from user {request.user_id} (conversation: {request.conversation_id})"
        )

        # Generate response
        response = await chat_service.chat(
            user_message=request.content,
            user_id=request.user_id,
            conversation_id=request.conversation_id,
        )

        response_message = response.get("message")
        conversation_id = response.get("conversation_id")
        tokens_used = response.get("tokens_used")

        logger.info(f"Successfully generated response for conversation {conversation_id}")

        return ChatResponse(
            message=response_message,
            conversation_id=conversation_id,
            tokens_used=tokens_used,
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="Failed to process your message. Please try again.",
        )
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again later.",
        )


@app.delete("/v1/conversations/{conversation_id}")
async def clear_conversation(conversation_id: str, user_id: str):
    """
    Clear conversation history (remove messages but keep conversation).

    Args:
        conversation_id: ID of conversation to clear
        user_id: User ID that owns the conversation

    Returns:
        Status message
    """
    success = chat_service.clear_conversation(conversation_id, user_id)
    if success:
        logger.info(f"Cleared conversation {conversation_id} for user {user_id}")
        return {"status": "success", "message": "Conversation cleared"}
    else:
        raise HTTPException(
            status_code=404, detail="Conversation not found"
        )


@app.delete("/v1/conversations/{conversation_id}/delete")
async def delete_conversation(conversation_id: str, user_id: str):
    """
    Delete a conversation and all its messages.

    Args:
        conversation_id: ID of conversation to delete
        user_id: User ID that owns the conversation

    Returns:
        Status message
    """
    success = chat_service.delete_conversation(conversation_id, user_id)
    if success:
        logger.info(f"Deleted conversation {conversation_id} for user {user_id}")
        return {"status": "success", "message": "Conversation deleted"}
    else:
        raise HTTPException(
            status_code=404, detail="Conversation not found"
        )


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "MindEase Chatbot API",
        "version": "0.1.0",
        "endpoints": {
            "chat": "/v1/chat",
            "health": "/health",
            "docs": "/docs",
            "openapi": "/openapi.json",
        },
    }
