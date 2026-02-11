from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from typing import Optional
import uuid

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    due_date: Optional[datetime] = Field(None, alias="dueDate")
    priority: Optional[str] = Field('medium', alias="priority")
    is_recurring: Optional[bool] = Field(False, alias="isRecurring")
    recurrence_rule: Optional[str] = Field(None, alias="recurrenceRule")

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        if v is not None and v not in ['low', 'medium', 'high']:
            raise ValueError('Priority must be one of: low, medium, high')
        return v

    @field_validator('recurrence_rule')
    @classmethod
    def validate_recurrence_rule(cls, v):
        if v is not None and v not in ['daily', 'weekly', 'monthly']:
            raise ValueError('Recurrence rule must be one of: daily, weekly, monthly')
        return v

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None
    due_date: Optional[datetime] = Field(None, alias="dueDate")
    priority: Optional[str] = Field(None, alias="priority")
    is_recurring: Optional[bool] = Field(None, alias="isRecurring")
    recurrence_rule: Optional[str] = Field(None, alias="recurrenceRule")

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        if v is not None and v not in ['low', 'medium', 'high']:
            raise ValueError('Priority must be one of: low, medium, high')
        return v

    @field_validator('recurrence_rule')
    @classmethod
    def validate_recurrence_rule(cls, v):
        if v is not None and v not in ['daily', 'weekly', 'monthly']:
            raise ValueError('Recurrence rule must be one of: daily, weekly, monthly')
        return v

class TaskOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)  # Allow both snake_case and camelCase

    id: uuid.UUID
    display_id: Optional[int] = Field(None, alias="displayId")  # Simple numeric ID for display
    title: str
    description: Optional[str]
    completed: bool
    due_date: Optional[datetime] = Field(alias="dueDate")
    priority: Optional[str] = Field(alias="priority")
    is_recurring: bool = Field(alias="isRecurring")
    recurrence_rule: Optional[str] = Field(None, alias="recurrenceRule")
    completed_at: Optional[datetime] = Field(None, alias="completedAt")
    user_id: str = Field(alias="userId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")