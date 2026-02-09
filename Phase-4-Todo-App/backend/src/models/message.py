from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class MessageBase(SQLModel):
    user_id: str = Field(index=True)
    conversation_id: int = Field(index=True, foreign_key="conversation.id")
    role: str = Field(regex="^(user|assistant)$")  # Role must be either "user" or "assistant"
    content: str = Field(max_length=5000)


class Message(MessageBase, table=True):
    """
    Represents individual exchanges in a conversation with role (user/assistant) and content
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MessageCreate(MessageBase):
    pass


class MessageRead(MessageBase):
    id: int
    created_at: datetime