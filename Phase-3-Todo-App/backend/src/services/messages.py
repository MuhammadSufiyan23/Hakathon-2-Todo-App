from sqlmodel import Session, select
try:
    # Try import paths for when running in flattened structure
    from ..models.message import Message, MessageCreate
except ImportError:
    # Fallback for when running with backend directory structure
    from backend.src.models.message import Message, MessageCreate
from typing import List, Optional
from datetime import datetime


def create_message(*, session: Session, message_in: MessageCreate) -> Message:
    """Create a new message record"""
    message = Message.model_validate(message_in)
    message.created_at = datetime.utcnow()
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


def get_messages_by_conversation(*, session: Session, conversation_id: int) -> List[Message]:
    """Get all messages for a specific conversation"""
    statement = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc())
    return session.exec(statement).all()


def get_messages_by_user(*, session: Session, user_id: str) -> List[Message]:
    """Get all messages for a specific user"""
    statement = select(Message).where(Message.user_id == user_id)
    return session.exec(statement).all()


def get_message_by_id(*, session: Session, message_id: int) -> Optional[Message]:
    """Get a message by its ID"""
    statement = select(Message).where(Message.id == message_id)
    return session.exec(statement).first()