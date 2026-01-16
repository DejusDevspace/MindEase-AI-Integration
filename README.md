# MindEase AI Integration

AI-powered chatbot integration for [MindEase](https://mindeaseproject.vercel.app/), a mental health and emotional well-being support platform for students.

## Overview

This service provides an intelligent chatbot that helps students navigate academic stress and emotional challenges. It integrates with the main MindEase application via a REST API, offering multi-turn conversations with conversation history persistence.

**Key Features:**
- **Empathetic AI Companion**: Designed specifically to support students with academic stress, anxiety, time management, and emotional well-being
- **Multi-turn Conversations**: Maintains conversation history for contextual, natural discussions
- **REST API**: Easy integration with web and mobile clients
- **Conversation Management**: Create, retrieve, and manage user conversations
- **Production-Ready**: Deployed with Docker and health checks

## Architecture

- **Backend**: FastAPI REST API (port 8000)
- **AI Model**: Groq API with Llama 3.3 70B
- **Database**: SQLite with conversation and message persistence
- **UI (Dev)**: Chainlit web interface (port 8001) for testing and development

## Quick Start (Docker)

### Prerequisites
- Docker and Docker Compose
- Groq API key (get one at [console.groq.com](https://console.groq.com))

### Setup

1. Clone the repository:
```bash
git clone https://github.com/DejusDevspace/MindEase-AI-Integration.git
cd MindEase-AI-Integration
```

2. Create `.env` file:
```bash
cp .env.example .env
```

3. Add your Groq API key to `.env`:
```
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
MAX_TOKENS=500
TEMPERATURE=0.7
DEBUG=false
```

4. Start the service:
```bash
docker-compose up
```

The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

## Local Development

### Prerequisites
- Python 3.13+
- `uv` package manager (or `pip`)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/DejusDevspace/MindEase-AI-Integration.git
cd MindEase-AI-Integration
```

2. Create `.env` file:
```bash
cp .env.example .env
# Add your Groq API key
```

3. Install dependencies:
```bash
uv sync
```

4. Run the FastAPI server:
```bash
python main.py
```

Or start the Chainlit interface for testing:
```bash
python main.py chainlit
```

## API Usage

### Chat Endpoint

Send a message and get a response:

```bash
curl -X POST "http://localhost:8000/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "content": "I am stressed about my exams",
    "conversation_id": "conv-id-optional"
  }'
```

**Response:**
```json
{
  "message": "I hear you—exam stress is really tough...",
  "conversation_id": "conv-uuid",
  "tokens_used": 145
}
```

### Clear Conversation

Remove all messages from a conversation (keeps conversation record):

```bash
curl -X DELETE "http://localhost:8000/v1/conversations/{conversation_id}?user_id={user_id}"
```

### Delete Conversation

Delete a conversation and all its messages:

```bash
curl -X DELETE "http://localhost:8000/v1/conversations/{conversation_id}/delete?user_id={user_id}"
```

### Health Check

```bash
curl http://localhost:8000/health
```

## Configuration

Environment variables in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | Required | Your Groq API key |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | LLM model to use |
| `MAX_TOKENS` | `500` | Maximum response length |
| `TEMPERATURE` | `0.7` | Response creativity (0-1) |
| `DEBUG` | `false` | Debug logging |

## About MindEase

MindEase began as a capstone project during an internship at FlexiSAF Edusoft Limited, developed by a cross-functional team tasked with creating innovative solutions to support student well-being. The AI integration service was built to provide students with accessible, compassionate support for managing academic stress and emotional challenges.

## Contact

For questions or issues, please open an issue on [GitHub](https://github.com/DejusDevspace/MindEase-AI-Integration).
