from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
import uuid

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    due_date: Optional[datetime] = Field(None, alias="dueDate")
    priority: Optional[str] = Field('medium', alias="priority")

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None
    due_date: Optional[datetime] = Field(None, alias="dueDate")
    priority: Optional[str] = Field(None, alias="priority")

class TaskOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)  # Allow both snake_case and camelCase

    id: uuid.UUID
    display_id: Optional[int] = Field(None, alias="displayId")  # Simple numeric ID for display
    title: str
    description: Optional[str]
    completed: bool
    due_date: Optional[datetime] = Field(alias="dueDate")
    priority: Optional[str] = Field(alias="priority")
    user_id: str = Field(alias="userId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")