
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session
from typing import Dict, Any, List
from pydantic import BaseModel
from datetime import datetime
import jwt
from dotenv import load_dotenv
import os

from db import get_session
from utils.auth import get_current_user, security, BETTER_AUTH_SECRET
from src.models.conversation import ConversationCreate
from src.models.message import MessageCreate
from src.services.conversations import (
    create_conversation,
    get_conversation_by_id,
    update_conversation_timestamp
)
from src.services.messages import (
    create_message,
    get_messages_by_conversation
)
from src.agents.runner import get_agent_runner

router = APIRouter()

class ChatReplyResponse(BaseModel):
    reply: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: int | None = None

class SimpleChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: List[Dict[str, Any]]
    timestamp: str

@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat_endpoint(
    user_id: str,
    chat_request: ChatRequest,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session)
) -> ChatResponse:
    """
    Chat endpoint that handles conversation flow, interacts with the AI agent,
    and manages request/response cycles.
    """
    # Normalize user IDs for comparison - handle potential 'user_' prefixes
    normalized_current_user_id = current_user["user_id"]
    normalized_path_user_id = user_id

    # Remove 'user_' prefix if it exists in either ID for comparison
    if normalized_current_user_id.startswith('user_'):
        normalized_current_user_id = normalized_current_user_id[5:]
    if normalized_path_user_id.startswith('user_'):
        normalized_path_user_id = normalized_path_user_id[5:]

    # Verify that the user_id in the path matches the authenticated user
    if normalized_current_user_id != normalized_path_user_id:
        raise HTTPException(
            status_code=403,
            detail=f"Access denied: Cannot access another user's chat. Expected: {normalized_current_user_id}, Got: {normalized_path_user_id}"
        )

    # Create or retrieve conversation using the original user_id (after normalization check)
    conversation_id = chat_request.conversation_id

    if conversation_id is None:
        # Create a new conversation
        conversation_create = ConversationCreate(user_id=user_id)
        conversation = create_conversation(session=session, conversation_in=conversation_create)
        conversation_id = conversation.id
    else:
        convo = get_conversation_by_id(session=session, conversation_id=chat_request.conversation_id)
        if not convo or convo.user_id != user_id:
            raise HTTPException(status_code=404, detail="Conversation not found")
        conversation_id = convo.id

    create_message(session=session, message_in=MessageCreate(
        user_id=user_id,
        conversation_id=conversation_id,
        role="user",
        content=chat_request.message
    ))

    history = get_messages_by_conversation(session=session, conversation_id=conversation_id)
    formatted_history = [{"role": m.role, "content": m.content} for m in history[:-1]]

    # Run the AI agent
    agent_runner = get_agent_runner()
    try:
        result = agent_runner.run_agent(
            user_input=chat_request.message,
            user_id=user_id,
            conversation_history=formatted_history
        )
    except Exception as e:
        # Log the actual error for debugging
        print(f"Agent error: {str(e)}")
        # Return a generic error response without exposing internal details
        error_message = {
            "response": "I'm currently experiencing some difficulties. Please try again later.",
            "tool_calls": [],
            "success": False
        }
        # Create assistant error message in the conversation
        assistant_message = MessageCreate(
            user_id=user_id,
            conversation_id=conversation_id,
            role="assistant",
            content=error_message["response"]
        )
        create_message(session=session, message_in=assistant_message)

        # Update conversation timestamp
        update_conversation_timestamp(session=session, conversation_id=conversation_id)

        # Commit all changes
        session.commit()

        # Return the response
        return ChatResponse(
            conversation_id=conversation_id,
            response=error_message["response"],
            tool_calls=error_message.get("tool_calls", []),
            timestamp=datetime.utcnow().isoformat()
        )


    create_message(session=session, message_in=MessageCreate(
        user_id=user_id,
        conversation_id=conversation_id,
        role="assistant",
        content=result["response"]
    ))

    update_conversation_timestamp(session=session, conversation_id=conversation_id)
    session.commit()

    return ChatResponse(
        conversation_id=conversation_id,
        response=result["response"],
        tool_calls=result.get("tool_calls", []),
        timestamp=datetime.utcnow().isoformat()
    )


@router.post("/chat", response_model=ChatReplyResponse)
async def simple_chat_endpoint(
    chat_request: SimpleChatRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> ChatReplyResponse:
    """
    Simple chat endpoint that accepts a message and returns a reply.
    Requires Authorization Bearer token.
    """
    # Validate JWT token and extract user info
    try:
        token = credentials.credentials
        payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=["HS256"])

        user_id = payload.get("userId") or payload.get("sub")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: no user ID found")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=401, detail="Invalid token signature")
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    except Exception:
        raise HTTPException(status_code=401, detail="Authentication error")

    # Create a temporary conversation for this request
    conversation_create = ConversationCreate(user_id=user_id)
    conversation = create_conversation(session=session, conversation_in=conversation_create)
    conversation_id = conversation.id

    # Add the user message to the conversation
    create_message(session=session, message_in=MessageCreate(
        user_id=user_id,
        conversation_id=conversation_id,
        role="user",
        content=chat_request.message
    ))

    # Get conversation history (though it will just be the current message since it's a new conversation)
    history = get_messages_by_conversation(session=session, conversation_id=conversation_id)
    formatted_history = [{"role": m.role, "content": m.content} for m in history[:-1]]  # Exclude current message

    # Run the AI agent
    agent_runner = get_agent_runner()
    try:
        result = agent_runner.run_agent(
            user_input=chat_request.message,
            user_id=user_id,
            conversation_history=formatted_history
        )

        # Add the assistant response to the conversation
        create_message(session=session, message_in=MessageCreate(
            user_id=user_id,
            conversation_id=conversation_id,
            role="assistant",
            content=result["response"]
        ))

        # Update conversation timestamp
        update_conversation_timestamp(session=session, conversation_id=conversation_id)

        # Commit all changes
        session.commit()

        # Return the response in the expected format
        return ChatReplyResponse(reply=result["response"])

    except Exception as e:
        # Log the actual error for debugging
        print(f"Agent error: {str(e)}")
        # Return a generic error response without exposing internal details
        error_response = "I'm currently experiencing some difficulties. Please try again later."

        # Add error response to the conversation
        create_message(session=session, message_in=MessageCreate(
            user_id=user_id,
            conversation_id=conversation_id,
            role="assistant",
            content=error_response
        ))

        # Update conversation timestamp
        update_conversation_timestamp(session=session, conversation_id=conversation_id)

        # Commit all changes
        session.commit()

        return ChatReplyResponse(reply=error_response)
