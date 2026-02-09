from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    due_date: Optional[datetime] = Field(None, alias="dueDate")

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None

class TaskOut(TaskCreate):
    id: uuid.UUID
    user_id: str
    completed: bool
    created_at: datetime
    updated_at: datetime