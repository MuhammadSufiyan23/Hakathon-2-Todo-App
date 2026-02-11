# Research Findings: Advanced Task Management Features

**Feature**: 002-advanced-task-features
**Date**: 2026-02-09
**Phase**: Phase 0 - Research

## Overview

This document consolidates research findings for the five technical clarifications identified during the Constitution Check phase. Each section provides a decision, rationale, and alternatives considered.

---

## 1. APScheduler Integration with FastAPI

### Decision

Use **AsyncIOScheduler** with FastAPI's lifespan context manager for reminder scheduling.

### Rationale

- **AsyncIOScheduler** integrates natively with FastAPI's async event loop without blocking
- FastAPI's lifespan context manager (introduced in FastAPI 0.93+) provides clean startup/shutdown hooks
- Scheduler runs in the same process, avoiding complexity of separate worker processes for Phase III-IV
- Suitable for moderate load (100+ concurrent users) without requiring external message queues

### Implementation Pattern

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start scheduler
    scheduler.start()
    scheduler.add_job(
        check_reminders,
        trigger=IntervalTrigger(minutes=1),
        id="reminder_checker",
        replace_existing=True
    )
    yield
    # Shutdown: Stop scheduler
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)
```

### Alternatives Considered

1. **BackgroundScheduler (threading-based)**
   - Rejected: Uses threads which don't integrate well with async FastAPI
   - Could cause blocking issues with async database operations

2. **Celery + Redis**
   - Rejected for Phase III-IV: Adds significant infrastructure complexity
   - Deferred to Phase V when Kafka/Dapr are introduced
   - Overkill for simple periodic reminder checks

3. **FastAPI BackgroundTasks**
   - Rejected: Not suitable for periodic/scheduled tasks
   - Only works for one-off background tasks triggered by requests

### Performance Considerations

- Reminder check interval: 1 minute (configurable)
- Expected load: <1000 active reminders per check
- Database query optimization: Index on `remind_at` timestamp
- Non-blocking: Async job execution prevents blocking API requests

---

## 2. Database Migration Strategy

### Decision

Use **Alembic** with nullable columns and default values for backward compatibility.

### Rationale

- Alembic is the standard migration tool for SQLAlchemy/SQLModel
- Adding nullable columns allows safe migration without requiring data backfill
- Default values can be applied at application level for new records
- Supports rollback if issues are detected

### Migration Strategy

**Phase 1: Add New Columns (Nullable)**
```python
# Migration: Add new columns to tasks table
op.add_column('tasks', sa.Column('priority', sa.String(10), nullable=True))
op.add_column('tasks', sa.Column('due_date', sa.DateTime(timezone=True), nullable=True))
op.add_column('tasks', sa.Column('is_recurring', sa.Boolean(), nullable=True, server_default='false'))
op.add_column('tasks', sa.Column('recurrence_rule', sa.String(100), nullable=True))
op.add_column('tasks', sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True))
op.add_column('tasks', sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.func.now()))
op.add_column('tasks', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.func.now()))
```

**Phase 2: Create New Tables**
```python
# Create tags table
op.create_table('tags',
    sa.Column('id', sa.Integer(), primary_key=True),
    sa.Column('name', sa.String(50), nullable=False),
    sa.Column('user_id', sa.String(255), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
)

# Create task_tags junction table
op.create_table('task_tags',
    sa.Column('task_id', sa.Integer(), sa.ForeignKey('tasks.id', ondelete='CASCADE')),
    sa.Column('tag_id', sa.Integer(), sa.ForeignKey('tags.id', ondelete='CASCADE')),
    sa.PrimaryKeyConstraint('task_id', 'tag_id')
)

# Create reminders table
op.create_table('reminders',
    sa.Column('id', sa.Integer(), primary_key=True),
    sa.Column('task_id', sa.Integer(), sa.ForeignKey('tasks.id', ondelete='CASCADE')),
    sa.Column('user_id', sa.String(255), nullable=False),
    sa.Column('remind_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
)

# Create activity_logs table
op.create_table('activity_logs',
    sa.Column('id', sa.Integer(), primary_key=True),
    sa.Column('task_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.String(255), nullable=False),
    sa.Column('action', sa.String(50), nullable=False),
    sa.Column('details', sa.JSON(), nullable=True),
    sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now())
)
```

**Phase 3: Add Indexes**
```python
# Performance indexes
op.create_index('idx_tasks_user_priority', 'tasks', ['user_id', 'priority'])
op.create_index('idx_tasks_user_due_date', 'tasks', ['user_id', 'due_date'])
op.create_index('idx_tags_user_name', 'tags', ['user_id', 'name'], unique=True)
op.create_index('idx_reminders_remind_at', 'reminders', ['remind_at', 'status'])
op.create_index('idx_activity_logs_task_timestamp', 'activity_logs', ['task_id', 'timestamp'])
```

### Alternatives Considered

1. **Direct SQL Scripts**
   - Rejected: Less maintainable, no version tracking
   - Alembic provides better rollback and history management

2. **Non-nullable Columns with Backfill**
   - Rejected: Requires data migration for existing tasks
   - Adds complexity and risk for Phase III-IV
   - Nullable columns are acceptable for optional features

3. **Separate Database for New Features**
   - Rejected: Violates single source of truth principle
   - Complicates queries and transactions

### Rollback Strategy

- Each migration includes `downgrade()` function
- Test rollback in development before production deployment
- Database backup before migration execution

---

## 3. Tag Storage Pattern

### Decision

Use **normalized many-to-many relationship** with separate `tags` and `task_tags` tables.

### Rationale

- Enables tag reusability across tasks (user types "work" once, reuses everywhere)
- Supports efficient filtering by tag (single JOIN vs JSON array scanning)
- Allows tag-level operations (rename tag affects all tasks)
- Better query performance with proper indexes
- Supports tag autocomplete/suggestions naturally

### Schema Design

```
tags
├── id (PK)
├── name (unique per user)
├── user_id (FK to users)
├── color (optional, for UI)
└── created_at

task_tags (junction table)
├── task_id (FK to tasks, CASCADE DELETE)
└── tag_id (FK to tags, CASCADE DELETE)
```

### Query Patterns

**Filter tasks by tag:**
```sql
SELECT t.* FROM tasks t
JOIN task_tags tt ON t.id = tt.task_id
JOIN tags tg ON tt.tag_id = tg.id
WHERE tg.name = 'work' AND t.user_id = ?
```

**Get all tags for a task:**
```sql
SELECT tg.* FROM tags tg
JOIN task_tags tt ON tg.id = tt.tag_id
WHERE tt.task_id = ?
```

### Alternatives Considered

1. **JSON Array in Tasks Table**
   - Rejected: Poor query performance for filtering
   - No tag reusability (user must retype tag names)
   - Difficult to rename tags globally
   - Limited indexing support

2. **PostgreSQL Array Column**
   - Rejected: Better than JSON but still limited
   - No referential integrity
   - Harder to manage tag lifecycle
   - Less portable to other databases

3. **Tags as Comma-Separated String**
   - Rejected: Worst option, no query performance
   - No data integrity

### Performance Optimization

- Composite index on `(user_id, name)` in tags table (unique constraint)
- Composite index on `(task_id, tag_id)` in task_tags table
- Limit: 10 tags per task (enforced at application level)

---

## 4. Recurring Task Logic

### Decision

Use **simplified recurrence rules** with enum-based patterns and `python-dateutil` for date calculations.

### Rationale

- Phase III-IV requires only basic patterns: daily, weekly, monthly
- `python-dateutil.rrule` provides robust date arithmetic with timezone support
- Simpler than full iCalendar RRULE specification
- Extensible to more complex patterns in Phase V if needed

### Recurrence Rule Storage

```python
# Enum for recurrence frequency
class RecurrenceFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"  # Reserved for Phase V

# Store in tasks table
recurrence_rule: Optional[str]  # Format: "daily" | "weekly" | "monthly"
```

### Next Instance Calculation

```python
from dateutil.relativedelta import relativedelta
from datetime import datetime, timezone

def calculate_next_due_date(current_due_date: datetime, recurrence_rule: str) -> datetime:
    """Calculate next due date based on recurrence rule."""
    if recurrence_rule == "daily":
        return current_due_date + relativedelta(days=1)
    elif recurrence_rule == "weekly":
        return current_due_date + relativedelta(weeks=1)
    elif recurrence_rule == "monthly":
        return current_due_date + relativedelta(months=1)
    else:
        raise ValueError(f"Unknown recurrence rule: {recurrence_rule}")
```

### Recurring Task Workflow

1. User marks recurring task as complete
2. Backend creates activity log entry
3. Backend creates new task instance:
   - Copy: title, description, priority, tags, recurrence_rule
   - New: due_date (calculated), completed=False, completed_at=None
   - Preserve: user_id, is_recurring=True
4. Return both completed task and new instance to frontend

### Alternatives Considered

1. **Full iCalendar RRULE Specification**
   - Rejected for Phase III-IV: Overly complex for basic needs
   - Supports advanced patterns (BYDAY, BYMONTH, etc.) not required yet
   - Can be added in Phase V if needed

2. **Cron Expression Format**
   - Rejected: Designed for scheduling, not task recurrence
   - Less intuitive for end users
   - Doesn't handle "next occurrence" naturally

3. **Store Next Due Date Only**
   - Rejected: Loses recurrence pattern information
   - Can't modify recurrence rule retroactively
   - Harder to display recurrence info to user

### Edge Cases Handled

- **Timezone**: All dates stored in UTC, converted to user timezone for display
- **DST Transitions**: `dateutil.relativedelta` handles DST automatically
- **Month-End Dates**: Monthly recurrence on Jan 31 → Feb 28/29 (handled by relativedelta)
- **Stopping Recurrence**: User can edit task and set `is_recurring=False`

---

## 5. Activity Log Performance

### Decision

Use **asynchronous database writes** with background tasks for activity logging.

### Rationale

- Activity logging is non-critical for request success
- Async writes prevent blocking API responses
- Database writes are batched naturally by connection pool
- Simple implementation without external queue infrastructure

### Implementation Pattern

```python
from fastapi import BackgroundTasks

async def log_activity(
    user_id: str,
    action: str,
    task_id: Optional[int] = None,
    details: Optional[dict] = None
):
    """Log activity asynchronously."""
    async with get_db_session() as session:
        log_entry = ActivityLog(
            user_id=user_id,
            action=action,
            task_id=task_id,
            details=details,
            timestamp=datetime.now(timezone.utc)
        )
        session.add(log_entry)
        await session.commit()

@router.post("/tasks")
async def create_task(
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user)
):
    # Create task (synchronous, critical path)
    task = await task_service.create_task(task_data, user_id)

    # Log activity (asynchronous, non-blocking)
    background_tasks.add_task(
        log_activity,
        user_id=user_id,
        action="task_created",
        task_id=task.id,
        details={"title": task.title}
    )

    return task
```

### Database Optimization

**Indexes:**
```python
# Composite index for user activity queries
CREATE INDEX idx_activity_logs_user_timestamp ON activity_logs(user_id, timestamp DESC);

# Index for task-specific activity queries
CREATE INDEX idx_activity_logs_task_timestamp ON activity_logs(task_id, timestamp DESC);
```

**Partitioning (Future Enhancement):**
- Consider time-based partitioning if activity logs grow beyond 1M records
- Partition by month for efficient archival

### Alternatives Considered

1. **Synchronous Logging**
   - Rejected: Adds 10-50ms to every API request
   - Impacts user experience for non-critical feature
   - Risk of request failure if logging fails

2. **Database Triggers**
   - Rejected: Harder to maintain and debug
   - Limits flexibility (can't log application-level context)
   - Performance impact on every write operation

3. **External Logging Service (e.g., Elasticsearch)**
   - Rejected for Phase III-IV: Adds infrastructure complexity
   - Overkill for activity logging needs
   - Can be added in Phase V if analytics requirements grow

4. **Message Queue (Kafka/RabbitMQ)**
   - Rejected for Phase III-IV: Deferred to Phase V
   - FastAPI BackgroundTasks sufficient for current scale
   - Will migrate to Kafka in Phase V for event-driven architecture

### Retention Strategy

- **Short-term**: Keep all activity logs in primary database
- **Long-term** (Phase V): Archive logs older than 90 days to cold storage
- **Compliance**: Activity logs support audit requirements

### Error Handling

- Activity logging failures are logged but don't fail the main request
- Retry logic: FastAPI BackgroundTasks retries once on failure
- Monitoring: Track activity log write failures via metrics

---

## Summary of Decisions

| Area | Decision | Key Benefit |
|------|----------|-------------|
| APScheduler Integration | AsyncIOScheduler with lifespan context | Non-blocking, native async integration |
| Database Migration | Alembic with nullable columns | Safe, backward-compatible, rollback support |
| Tag Storage | Normalized many-to-many tables | Query performance, tag reusability |
| Recurring Task Logic | Enum-based with dateutil.rrule | Simple, robust date handling, extensible |
| Activity Log Performance | Async writes with BackgroundTasks | Non-blocking, simple, no external dependencies |

---

## Next Steps

With research complete, proceed to Phase 1:
1. Generate `data-model.md` with entity definitions
2. Generate API contracts in `contracts/` directory
3. Generate `quickstart.md` for developer onboarding
4. Update agent context with new technologies

All decisions maintain Phase III-IV scope (no Kafka, Dapr, or Kubernetes) while remaining compatible with Phase V cloud-native migration.
