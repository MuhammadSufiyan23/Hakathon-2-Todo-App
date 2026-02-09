from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class ConversationBase(SQLModel):
    user_id: str = Field(index=True)


class Conversation(ConversationBase, table=True):
    """
    Represents a chat session between user and AI assistant with metadata
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    title: Optional[str] = Field(default=None, max_length=200)  # Optional title for conversation context


class ConversationCreate(ConversationBase):
    title: Optional[str] = None


class ConversationRead(ConversationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    title: Optional[str]