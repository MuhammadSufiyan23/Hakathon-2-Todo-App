# Data Model: Advanced Task Management Features

**Feature**: 002-advanced-task-features
**Date**: 2026-02-09
**Phase**: Phase 1 - Design

## Overview

This document defines the data model for Phase III-IV advanced task management features. All entities maintain user isolation through `user_id` filtering and support the existing Better Auth authentication system.

---

## Entity Definitions

### 1. Task (Extended)

**Description**: Core task entity extended with priority, tags, due dates, and recurrence support.

**Table**: `tasks` (existing table, adding new columns)

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Unique task identifier |
| `user_id` | String(255) | NOT NULL, FK to users | Owner of the task |
| `title` | String(255) | NOT NULL | Task title |
| `description` | Text | Nullable | Detailed task description |
| `completed` | Boolean | NOT NULL, Default: false | Completion status |
| `priority` | String(10) | Nullable, Enum | Priority level: 'low', 'medium', 'high' |
| `due_date` | DateTime(TZ) | Nullable | When task is due (UTC) |
| `is_recurring` | Boolean | Nullable, Default: false | Whether task repeats |
| `recurrence_rule` | String(100) | Nullable | Recurrence pattern: 'daily', 'weekly', 'monthly' |
| `completed_at` | DateTime(TZ) | Nullable | When task was completed (UTC) |
| `created_at` | DateTime(TZ) | NOT NULL, Default: now() | Task creation timestamp (UTC) |
| `updated_at` | DateTime(TZ) | NOT NULL, Default: now() | Last update timestamp (UTC) |

**Indexes**:
- `idx_tasks_user_id` (existing)
- `idx_tasks_user_priority` on `(user_id, priority)`
- `idx_tasks_user_due_date` on `(user_id, due_date)`
- `idx_tasks_user_completed` on `(user_id, completed)`

**Validation Rules**:
- `priority` must be one of: 'low', 'medium', 'high', or NULL
- `recurrence_rule` must be one of: 'daily', 'weekly', 'monthly', or NULL
- `is_recurring` can only be true if `recurrence_rule` is not NULL
- `completed_at` can only be set if `completed` is true
- `due_date` must be valid datetime if provided
- `title` length: 1-255 characters
- `description` length: 0-5000 characters

**State Transitions**:
```
[Pending] --complete--> [Completed]
  |                         |
  |                         v
  +-------------------> [Recurring: Create Next Instance]
```

**Relationships**:
- One-to-Many with `task_tags` (a task can have multiple tags)
- One-to-Many with `reminders` (a task can have multiple reminders)
- One-to-Many with `activity_logs` (a task has activity history)

---

### 2. Tag

**Description**: User-defined labels for task categorization.

**Table**: `tags` (new table)

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Unique tag identifier |
| `name` | String(50) | NOT NULL | Tag name |
| `user_id` | String(255) | NOT NULL, FK to users | Owner of the tag |
| `color` | String(7) | Nullable | Hex color code (e.g., '#FF5733') |
| `created_at` | DateTime(TZ) | NOT NULL, Default: now() | Tag creation timestamp (UTC) |

**Indexes**:
- `idx_tags_user_name` on `(user_id, name)` - UNIQUE constraint

**Validation Rules**:
- `name` length: 1-50 characters
- `name` must be unique per user (case-insensitive)
- `name` allowed characters: alphanumeric, spaces, hyphens, underscores
- `color` must match regex: `^#[0-9A-Fa-f]{6}$` if provided

**Relationships**:
- One-to-Many with `task_tags` (a tag can be assigned to multiple tasks)

---

### 3. TaskTag (Junction Table)

**Description**: Many-to-many relationship between tasks and tags.

**Table**: `task_tags` (new table)

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `task_id` | Integer | PK, FK to tasks(id) ON DELETE CASCADE | Reference to task |
| `tag_id` | Integer | PK, FK to tags(id) ON DELETE CASCADE | Reference to tag |

**Indexes**:
- Primary key on `(task_id, tag_id)`
- `idx_task_tags_tag_id` on `tag_id` (for reverse lookups)

**Validation Rules**:
- A task can have maximum 10 tags (enforced at application level)
- Cannot assign the same tag to a task twice

**Relationships**:
- Many-to-One with `tasks`
- Many-to-One with `tags`

---

### 4. Reminder

**Description**: Scheduled notifications for tasks with due dates.

**Table**: `reminders` (new table)

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Unique reminder identifier |
| `task_id` | Integer | NOT NULL, FK to tasks(id) ON DELETE CASCADE | Associated task |
| `user_id` | String(255) | NOT NULL, FK to users | Owner of the reminder |
| `remind_at` | DateTime(TZ) | NOT NULL | When to send reminder (UTC) |
| `status` | String(20) | NOT NULL, Default: 'pending' | Reminder status |
| `created_at` | DateTime(TZ) | NOT NULL, Default: now() | Reminder creation timestamp (UTC) |
| `sent_at` | DateTime(TZ) | Nullable | When reminder was sent (UTC) |

**Indexes**:
- `idx_reminders_remind_at_status` on `(remind_at, status)` - for scheduler queries
- `idx_reminders_task_id` on `task_id`
- `idx_reminders_user_id` on `user_id`

**Validation Rules**:
- `status` must be one of: 'pending', 'sent', 'failed'
- `remind_at` must be in the future when created
- `sent_at` can only be set if `status` is 'sent'
- A task can have multiple reminders (e.g., 1 day before, 1 hour before)

**State Transitions**:
```
[Pending] --scheduler--> [Sent]
    |
    +--error--> [Failed]
```

**Relationships**:
- Many-to-One with `tasks`

---

### 5. ActivityLog

**Description**: Audit trail for all task operations.

**Table**: `activity_logs` (new table)

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Unique log entry identifier |
| `task_id` | Integer | Nullable, FK to tasks(id) ON DELETE SET NULL | Associated task (nullable for deleted tasks) |
| `user_id` | String(255) | NOT NULL, FK to users | User who performed the action |
| `action` | String(50) | NOT NULL | Action type |
| `details` | JSON | Nullable | Additional action details |
| `timestamp` | DateTime(TZ) | NOT NULL, Default: now() | When action occurred (UTC) |

**Indexes**:
- `idx_activity_logs_user_timestamp` on `(user_id, timestamp DESC)`
- `idx_activity_logs_task_timestamp` on `(task_id, timestamp DESC)`
- `idx_activity_logs_action` on `action`

**Validation Rules**:
- `action` must be one of: 'task_created', 'task_updated', 'task_completed', 'task_deleted', 'tag_added', 'tag_removed', 'reminder_set', 'reminder_sent'
- `details` JSON structure varies by action type (see below)

**Action Details Schema**:

```json
// task_created
{
  "title": "string",
  "priority": "string|null",
  "due_date": "datetime|null"
}

// task_updated
{
  "changed_fields": ["field1", "field2"],
  "old_values": {"field1": "old_value"},
  "new_values": {"field1": "new_value"}
}

// task_completed
{
  "title": "string",
  "completed_at": "datetime"
}

// task_deleted
{
  "title": "string",
  "was_completed": "boolean"
}

// tag_added
{
  "tag_name": "string"
}

// tag_removed
{
  "tag_name": "string"
}

// reminder_set
{
  "remind_at": "datetime"
}

// reminder_sent
{
  "reminder_id": "integer",
  "task_title": "string"
}
```

**Relationships**:
- Many-to-One with `tasks` (nullable, preserved after task deletion)

---

## Entity Relationship Diagram

```
┌─────────────────┐
│     users       │
│  (Better Auth)  │
└────────┬────────┘
         │
         │ 1:N
         │
    ┌────┴─────────────────────────────────┐
    │                                      │
    │                                      │
┌───▼──────┐         ┌──────────┐    ┌────▼─────┐
│  tasks   │◄───────►│task_tags │◄───┤   tags   │
│          │   N:M   └──────────┘ N:1└──────────┘
│          │
│          │
│          │ 1:N
│          │
├──────────┤         ┌────────────┐
│          │◄────────┤ reminders  │
│          │   1:N   └────────────┘
│          │
│          │ 1:N
│          │
│          │◄────────┐
└──────────┘         │
                     │
              ┌──────┴────────┐
              │ activity_logs │
              └───────────────┘
```

---

## Database Migration Plan

### Migration 1: Extend Tasks Table

```sql
-- Add new columns to tasks table
ALTER TABLE tasks
  ADD COLUMN priority VARCHAR(10),
  ADD COLUMN due_date TIMESTAMP WITH TIME ZONE,
  ADD COLUMN is_recurring BOOLEAN DEFAULT FALSE,
  ADD COLUMN recurrence_rule VARCHAR(100),
  ADD COLUMN completed_at TIMESTAMP WITH TIME ZONE,
  ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Add indexes
CREATE INDEX idx_tasks_user_priority ON tasks(user_id, priority);
CREATE INDEX idx_tasks_user_due_date ON tasks(user_id, due_date);
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);

-- Add check constraint for priority
ALTER TABLE tasks
  ADD CONSTRAINT chk_tasks_priority
  CHECK (priority IN ('low', 'medium', 'high') OR priority IS NULL);

-- Add check constraint for recurrence_rule
ALTER TABLE tasks
  ADD CONSTRAINT chk_tasks_recurrence_rule
  CHECK (recurrence_rule IN ('daily', 'weekly', 'monthly') OR recurrence_rule IS NULL);
```

### Migration 2: Create Tags and TaskTags Tables

```sql
-- Create tags table
CREATE TABLE tags (
  id SERIAL PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  user_id VARCHAR(255) NOT NULL,
  color VARCHAR(7),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  CONSTRAINT fk_tags_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create unique index on user_id + name (case-insensitive)
CREATE UNIQUE INDEX idx_tags_user_name ON tags(user_id, LOWER(name));

-- Create task_tags junction table
CREATE TABLE task_tags (
  task_id INTEGER NOT NULL,
  tag_id INTEGER NOT NULL,
  PRIMARY KEY (task_id, tag_id),
  CONSTRAINT fk_task_tags_task FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
  CONSTRAINT fk_task_tags_tag FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- Create index for reverse lookups
CREATE INDEX idx_task_tags_tag_id ON task_tags(tag_id);
```

### Migration 3: Create Reminders Table

```sql
-- Create reminders table
CREATE TABLE reminders (
  id SERIAL PRIMARY KEY,
  task_id INTEGER NOT NULL,
  user_id VARCHAR(255) NOT NULL,
  remind_at TIMESTAMP WITH TIME ZONE NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'pending',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  sent_at TIMESTAMP WITH TIME ZONE,
  CONSTRAINT fk_reminders_task FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
  CONSTRAINT fk_reminders_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT chk_reminders_status CHECK (status IN ('pending', 'sent', 'failed'))
);

-- Create indexes
CREATE INDEX idx_reminders_remind_at_status ON reminders(remind_at, status);
CREATE INDEX idx_reminders_task_id ON reminders(task_id);
CREATE INDEX idx_reminders_user_id ON reminders(user_id);
```

### Migration 4: Create ActivityLogs Table

```sql
-- Create activity_logs table
CREATE TABLE activity_logs (
  id SERIAL PRIMARY KEY,
  task_id INTEGER,
  user_id VARCHAR(255) NOT NULL,
  action VARCHAR(50) NOT NULL,
  details JSONB,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  CONSTRAINT fk_activity_logs_task FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL,
  CONSTRAINT fk_activity_logs_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT chk_activity_logs_action CHECK (action IN (
    'task_created', 'task_updated', 'task_completed', 'task_deleted',
    'tag_added', 'tag_removed', 'reminder_set', 'reminder_sent'
  ))
);

-- Create indexes
CREATE INDEX idx_activity_logs_user_timestamp ON activity_logs(user_id, timestamp DESC);
CREATE INDEX idx_activity_logs_task_timestamp ON activity_logs(task_id, timestamp DESC);
CREATE INDEX idx_activity_logs_action ON activity_logs(action);
```

---

## SQLModel Class Definitions

### Task Model (Extended)

```python
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from typing import Optional, List
from enum import Enum

class PriorityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class RecurrenceRule(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(max_length=255, nullable=False, index=True)
    title: str = Field(max_length=255, nullable=False)
    description: Optional[str] = Field(default=None, max_length=5000)
    completed: bool = Field(default=False, nullable=False)
    priority: Optional[PriorityLevel] = Field(default=None)
    due_date: Optional[datetime] = Field(default=None)
    is_recurring: bool = Field(default=False)
    recurrence_rule: Optional[RecurrenceRule] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tags: List["Tag"] = Relationship(back_populates="tasks", link_model="TaskTag")
    reminders: List["Reminder"] = Relationship(back_populates="task")
    activity_logs: List["ActivityLog"] = Relationship(back_populates="task")
```

### Tag Model

```python
class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, nullable=False)
    user_id: str = Field(max_length=255, nullable=False, index=True)
    color: Optional[str] = Field(default=None, max_length=7)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="tags", link_model="TaskTag")
```

### TaskTag Model

```python
class TaskTag(SQLModel, table=True):
    __tablename__ = "task_tags"

    task_id: int = Field(foreign_key="tasks.id", primary_key=True, ondelete="CASCADE")
    tag_id: int = Field(foreign_key="tags.id", primary_key=True, ondelete="CASCADE")
```

### Reminder Model

```python
class ReminderStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"

class Reminder(SQLModel, table=True):
    __tablename__ = "reminders"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", nullable=False, ondelete="CASCADE")
    user_id: str = Field(max_length=255, nullable=False, index=True)
    remind_at: datetime = Field(nullable=False)
    status: ReminderStatus = Field(default=ReminderStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = Field(default=None)

    # Relationships
    task: Optional["Task"] = Relationship(back_populates="reminders")
```

### ActivityLog Model

```python
class ActivityAction(str, Enum):
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_COMPLETED = "task_completed"
    TASK_DELETED = "task_deleted"
    TAG_ADDED = "tag_added"
    TAG_REMOVED = "tag_removed"
    REMINDER_SET = "reminder_set"
    REMINDER_SENT = "reminder_sent"

class ActivityLog(SQLModel, table=True):
    __tablename__ = "activity_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: Optional[int] = Field(default=None, foreign_key="tasks.id", ondelete="SET NULL")
    user_id: str = Field(max_length=255, nullable=False, index=True)
    action: ActivityAction = Field(nullable=False)
    details: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    task: Optional["Task"] = Relationship(back_populates="activity_logs")
```

---

## Data Integrity Rules

### User Isolation
- All queries MUST filter by `user_id` from authenticated session
- Users can only access their own tasks, tags, reminders, and activity logs
- Foreign key constraints maintain referential integrity

### Cascading Deletes
- Deleting a task cascades to: task_tags, reminders
- Deleting a task sets activity_logs.task_id to NULL (preserves audit trail)
- Deleting a tag cascades to: task_tags
- Deleting a user cascades to: tasks, tags, reminders, activity_logs

### Validation at Application Level
- Maximum 10 tags per task
- Tag name uniqueness per user (case-insensitive)
- Recurrence rule validation
- Due date must be valid datetime
- Reminder time must be in future when created

---

## Performance Considerations

### Query Optimization
- Composite indexes on frequently filtered columns (user_id + priority, user_id + due_date)
- Index on remind_at + status for scheduler queries
- Index on timestamp DESC for activity log queries

### Expected Query Patterns
1. **List tasks with filters**: `SELECT * FROM tasks WHERE user_id = ? AND priority = ? AND completed = ?`
2. **Search tasks**: `SELECT * FROM tasks WHERE user_id = ? AND (title ILIKE ? OR description ILIKE ?)`
3. **Get tasks by tag**: `SELECT t.* FROM tasks t JOIN task_tags tt ON t.id = tt.task_id JOIN tags tg ON tt.tag_id = tg.id WHERE tg.name = ? AND t.user_id = ?`
4. **Find pending reminders**: `SELECT * FROM reminders WHERE remind_at <= NOW() AND status = 'pending'`
5. **Get task activity**: `SELECT * FROM activity_logs WHERE task_id = ? ORDER BY timestamp DESC`

### Scalability
- Current design supports 1000+ tasks per user efficiently
- Activity logs may grow large; consider partitioning after 1M records
- Reminder checks run every 1 minute; optimize with indexed queries

---

## Next Steps

With data model complete, proceed to:
1. Generate API contracts (OpenAPI specification)
2. Generate quickstart.md for developers
3. Update agent context with new models
