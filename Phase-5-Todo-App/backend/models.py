from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum
import uuid

# Enums for Task model
class PriorityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class RecurrenceRule(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = False
    due_date: Optional[datetime] = Field(default=None, nullable=True)
    priority: Optional[str] = Field(default='medium', max_length=20, nullable=True)
    is_recurring: bool = Field(default=False)
    recurrence_rule: Optional[str] = Field(default=None, max_length=100, nullable=True)
    completed_at: Optional[datetime] = Field(default=None, nullable=True)

class Task(TaskBase, table=True):
    __tablename__ = 'task'

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    user_id: str = Field(nullable=False)  # Better Auth manages users table, so we don't use foreign_key constraint
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class UserBase(SQLModel):
    email: str = Field(unique=True, nullable=False)
    name: Optional[str] = Field(default=None)

class User(UserBase, table=True):
    id: str = Field(default_factory=lambda: f"user_{uuid.uuid4().hex}", primary_key=True)
    password_hash: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

# Tag model
class Tag(SQLModel, table=True):
    __tablename__ = 'tags'

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, nullable=False)
    user_id: str = Field(nullable=False)
    color: Optional[str] = Field(default=None, max_length=7, nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

# TaskTag junction table
class TaskTag(SQLModel, table=True):
    __tablename__ = 'task_tags'

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: uuid.UUID = Field(foreign_key="task.id", nullable=False)
    tag_id: int = Field(foreign_key="tags.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

# Reminder enums and model
class ReminderStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"

class Reminder(SQLModel, table=True):
    __tablename__ = 'reminders'

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: uuid.UUID = Field(foreign_key="task.id", nullable=False)
    user_id: str = Field(nullable=False)
    remind_at: datetime = Field(nullable=False)
    status: str = Field(default=ReminderStatus.PENDING.value, max_length=20, nullable=False)
    sent_at: Optional[datetime] = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

# ActivityLog enums and model
class ActivityAction(str, Enum):
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_DELETED = "task_deleted"
    TASK_COMPLETED = "task_completed"
    TAG_ADDED = "tag_added"
    TAG_REMOVED = "tag_removed"
    REMINDER_SET = "reminder_set"
    REMINDER_SENT = "reminder_sent"

class ActivityLog(SQLModel, table=True):
    __tablename__ = 'activity_logs'

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(nullable=False)
    action: str = Field(max_length=50, nullable=False)
    task_id: Optional[uuid.UUID] = Field(default=None, nullable=True)
    details: Optional[str] = Field(default=None, nullable=True)  # JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)