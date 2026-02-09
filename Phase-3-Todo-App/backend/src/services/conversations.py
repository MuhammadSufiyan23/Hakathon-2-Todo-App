from sqlmodel import Session, select
try:
    # Try import paths for when running in flattened structure
    from ..models.conversation import Conversation, ConversationCreate
except ImportError:
    # Fallback for when running with backend directory structure
    from backend.src.models.conversation import Conversation, ConversationCreate
from typing import List, Optional
from datetime import datetime


def create_conversation(*, session: Session, conversation_in: ConversationCreate) -> Conversation:
    """Create a new conversation record"""
    conversation = Conversation.model_validate(conversation_in)
    conversation.created_at = datetime.utcnow()
    conversation.updated_at = datetime.utcnow()
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


def get_conversation_by_id(*, session: Session, conversation_id: int) -> Optional[Conversation]:
    """Get a conversation by its ID"""
    statement = select(Conversation).where(Conversation.id == conversation_id)
    return session.exec(statement).first()


def get_conversations_by_user(*, session: Session, user_id: str) -> List[Conversation]:
    """Get all conversations for a specific user"""
    statement = select(Conversation).where(Conversation.user_id == user_id)
    return session.exec(statement).all()


def update_conversation_timestamp(*, session: Session, conversation_id: int) -> Conversation:
    """Update the updated_at timestamp for a conversation"""
    conversation = get_conversation_by_id(session=session, conversation_id=conversation_id)
    if conversation:
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
    return conversation