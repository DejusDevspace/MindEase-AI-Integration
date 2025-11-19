import chainlit as cl
from mindease.services.chat_service import chat_service


@cl.on_chat_start
async def on_chat_start():
    """Initialize chat session."""
    conversation_id = chat_service.generate_conversation_id()
    cl.user_session.set("conversation_id", conversation_id)

    await cl.Message(
        content="👋 Hi! I'm MindEase, your supportive AI companion. "
        "I'm here to help you navigate academic stress and support your emotional well-being. "
        "\n\nFeel free to share what's on your mind—whether it's exam anxiety, time management struggles, "
        "or just needing someone to talk to. I'm listening and I'm here to support you. 💙"
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming messages."""
    user_message = message.content
    conversation_id = cl.user_session.get("conversation_id")

    # Show loading indicator
    msg = cl.Message(content="")
    await msg.send()

    try:
        # Get response from chat service
        response = await chat_service.chat(
            user_message=user_message,
            conversation_id=conversation_id,
        )

        # Get user conversation ID from response (if available)
        updated_conversation_id = response.get("conversation_id", "")

        # Update conversation ID if new
        if updated_conversation_id != conversation_id:
            cl.user_session.set("conversation_id", updated_conversation_id)

        # Update message with response
        msg.content = response.get("message")
        await msg.update()

    except Exception as e:
        msg.content = (
            "I'm sorry, I encountered an error while trying to respond. "
            "Please try again in a moment. 💙"
        )
        await msg.update()
        print(f"Error: {str(e)}")
