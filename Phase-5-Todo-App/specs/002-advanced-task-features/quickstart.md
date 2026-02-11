# Quickstart Guide: Advanced Task Management Features

**Feature**: 002-advanced-task-features
**Date**: 2026-02-09
**Phase**: Phase 1 - Design

## Overview

This guide helps developers quickly implement and test the Phase III-IV advanced task management features. These features extend the existing task system with priorities, tags, search/filter/sort, due dates, reminders, recurring tasks, and activity logging.

---

## Prerequisites

- Python 3.11+ installed
- Node.js 18+ and npm installed
- PostgreSQL database (Neon Serverless or local)
- Existing Phase I-II Todo App running
- Better Auth configured and working

---

## Backend Setup

### 1. Install Dependencies

Add new dependencies to `backend/requirements.txt`:

```txt
# Existing dependencies...
apscheduler==3.10.4
python-dateutil==2.8.2
```

Install:

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run Database Migrations

Create and run the migration:

```bash
# Generate migration (if using Alembic)
alembic revision --autogenerate -m "Add advanced task features"

# Or use the provided migration script
python migrate_add_columns.py

# Apply migration
alembic upgrade head
```

**Manual Migration** (if not using Alembic):

```sql
-- Run the SQL from specs/002-advanced-task-features/data-model.md
-- Section: Database Migration Plan
```

### 3. Update Models

Extend `backend/app/models/task.py`:

```python
from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional
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
    completed: bool = Field(default=False)

    # NEW FIELDS
    priority: Optional[PriorityLevel] = Field(default=None)
    due_date: Optional[datetime] = Field(default=None)
    is_recurring: bool = Field(default=False)
    recurrence_rule: Optional[RecurrenceRule] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

Create new model files:
- `backend/app/models/tag.py`
- `backend/app/models/reminder.py`
- `backend/app/models/activity_log.py`

(See `data-model.md` for complete model definitions)

### 4. Configure APScheduler

Create `backend/app/scheduler/reminder_scheduler.py`:

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timezone
from app.services.reminder_service import ReminderService

scheduler = AsyncIOScheduler()

async def check_reminders():
    """Check for pending reminders and send notifications."""
    reminder_service = ReminderService()
    await reminder_service.process_pending_reminders()

def start_scheduler():
    """Start the reminder scheduler."""
    scheduler.add_job(
        check_reminders,
        trigger=IntervalTrigger(minutes=1),
        id="reminder_checker",
        replace_existing=True
    )
    scheduler.start()

def stop_scheduler():
    """Stop the reminder scheduler."""
    scheduler.shutdown()
```

Update `backend/main.py`:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.scheduler.reminder_scheduler import start_scheduler, stop_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()

app = FastAPI(lifespan=lifespan)
```

### 5. Implement Services

Create service files:

**`backend/app/services/task_service.py`** (extend existing):

```python
from typing import Optional, List
from sqlmodel import select, or_, and_
from app.models.task import Task, PriorityLevel
from app.services.activity_service import ActivityService

class TaskService:
    async def search_tasks(
        self,
        user_id: str,
        search: Optional[str] = None,
        priority: Optional[PriorityLevel] = None,
        completed: Optional[bool] = None,
        tag_names: Optional[List[str]] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        limit: int = 50,
        offset: int = 0
    ) -> List[Task]:
        """Search and filter tasks with advanced options."""
        query = select(Task).where(Task.user_id == user_id)

        # Search filter
        if search:
            query = query.where(
                or_(
                    Task.title.ilike(f"%{search}%"),
                    Task.description.ilike(f"%{search}%")
                )
            )

        # Priority filter
        if priority:
            query = query.where(Task.priority == priority)

        # Completion filter
        if completed is not None:
            query = query.where(Task.completed == completed)

        # Tag filter (requires JOIN)
        if tag_names:
            # Implementation with JOIN to task_tags and tags
            pass

        # Sorting
        sort_column = getattr(Task, sort_by)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Pagination
        query = query.offset(offset).limit(limit)

        # Execute query
        async with get_session() as session:
            result = await session.execute(query)
            return result.scalars().all()

    async def complete_task(self, task_id: int, user_id: str) -> dict:
        """Complete a task and create next instance if recurring."""
        async with get_session() as session:
            task = await session.get(Task, task_id)

            if not task or task.user_id != user_id:
                raise ValueError("Task not found")

            # Mark as completed
            task.completed = True
            task.completed_at = datetime.now(timezone.utc)
            await session.commit()

            # Log activity
            await ActivityService().log_activity(
                user_id=user_id,
                action="task_completed",
                task_id=task_id,
                details={"title": task.title}
            )

            # Create next instance if recurring
            next_instance = None
            if task.is_recurring and task.recurrence_rule:
                next_instance = await self._create_recurring_instance(task, session)

            return {
                "completed_task": task,
                "next_instance": next_instance
            }
```

**`backend/app/services/tag_service.py`**:

```python
from app.models.tag import Tag
from app.models.task_tag import TaskTag

class TagService:
    async def create_tag(self, name: str, user_id: str, color: Optional[str] = None) -> Tag:
        """Create a new tag."""
        # Check for duplicate (case-insensitive)
        # Create tag
        # Return tag
        pass

    async def assign_tag_to_task(self, task_id: int, tag_id: int, user_id: str):
        """Assign a tag to a task."""
        # Validate ownership
        # Check max tags limit (10)
        # Create task_tag entry
        pass
```

**`backend/app/services/reminder_service.py`**:

```python
from datetime import datetime, timezone
from app.models.reminder import Reminder, ReminderStatus

class ReminderService:
    async def process_pending_reminders(self):
        """Process all pending reminders that are due."""
        now = datetime.now(timezone.utc)

        # Query pending reminders where remind_at <= now
        # For each reminder:
        #   - Send notification (console log for Phase III-IV)
        #   - Update status to 'sent'
        #   - Set sent_at timestamp
        #   - Log activity
        pass
```

**`backend/app/services/activity_service.py`**:

```python
from app.models.activity_log import ActivityLog, ActivityAction

class ActivityService:
    async def log_activity(
        self,
        user_id: str,
        action: ActivityAction,
        task_id: Optional[int] = None,
        details: Optional[dict] = None
    ):
        """Log an activity asynchronously."""
        # Create activity log entry
        # Use FastAPI BackgroundTasks for async write
        pass
```

### 6. Update API Routes

Extend `backend/app/api/routes/tasks.py`:

```python
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from typing import Optional, List

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/")
async def list_tasks(
    search: Optional[str] = None,
    priority: Optional[str] = None,
    completed: Optional[bool] = None,
    tag: Optional[List[str]] = Query(None),
    sort_by: str = "created_at",
    sort_order: str = "desc",
    limit: int = 50,
    offset: int = 0,
    user_id: str = Depends(get_current_user)
):
    """List tasks with advanced filtering."""
    task_service = TaskService()
    tasks = await task_service.search_tasks(
        user_id=user_id,
        search=search,
        priority=priority,
        completed=completed,
        tag_names=tag,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset
    )
    return {"tasks": tasks, "total": len(tasks)}

@router.post("/{task_id}/complete")
async def complete_task(
    task_id: int,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user)
):
    """Mark task as complete and create next instance if recurring."""
    task_service = TaskService()
    result = await task_service.complete_task(task_id, user_id)
    return result
```

Create new route files:
- `backend/app/api/routes/tags.py`
- `backend/app/api/routes/reminders.py`
- `backend/app/api/routes/activity.py`

---

## Frontend Setup

### 1. Install Dependencies

No new dependencies required (using existing Next.js, React, TailwindCSS, shadcn/ui).

### 2. Update Types

Extend `frontend/src/types/task.ts`:

```typescript
export type PriorityLevel = 'low' | 'medium' | 'high';
export type RecurrenceRule = 'daily' | 'weekly' | 'monthly';

export interface Task {
  id: number;
  user_id: string;
  title: string;
  description?: string;
  completed: boolean;

  // NEW FIELDS
  priority?: PriorityLevel;
  due_date?: string; // ISO 8601 datetime
  is_recurring: boolean;
  recurrence_rule?: RecurrenceRule;
  completed_at?: string;
  created_at: string;
  updated_at: string;
  tags?: Tag[];
}

export interface Tag {
  id: number;
  name: string;
  color?: string;
  task_count?: number;
}

export interface Reminder {
  id: number;
  task_id: number;
  remind_at: string;
  status: 'pending' | 'sent' | 'failed';
}
```

### 3. Update API Client

Extend `frontend/src/services/api.ts`:

```typescript
export const taskApi = {
  // Existing methods...

  // NEW METHODS
  searchTasks: async (params: {
    search?: string;
    priority?: string;
    completed?: boolean;
    tag?: string[];
    sort_by?: string;
    sort_order?: string;
  }) => {
    const queryString = new URLSearchParams(params as any).toString();
    const response = await fetch(`${API_BASE_URL}/tasks?${queryString}`, {
      headers: { Authorization: `Bearer ${getToken()}` }
    });
    return response.json();
  },

  completeTask: async (taskId: number) => {
    const response = await fetch(`${API_BASE_URL}/tasks/${taskId}/complete`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${getToken()}` }
    });
    return response.json();
  }
};

export const tagApi = {
  listTags: async () => {
    const response = await fetch(`${API_BASE_URL}/tags`, {
      headers: { Authorization: `Bearer ${getToken()}` }
    });
    return response.json();
  },

  createTag: async (data: { name: string; color?: string }) => {
    const response = await fetch(`${API_BASE_URL}/tags`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${getToken()}`
      },
      body: JSON.stringify(data)
    });
    return response.json();
  }
};
```

### 4. Create New Components

**`frontend/src/components/tasks/PriorityBadge.tsx`**:

```typescript
import { Badge } from '@/components/ui/badge';

interface PriorityBadgeProps {
  priority: 'low' | 'medium' | 'high';
}

export function PriorityBadge({ priority }: PriorityBadgeProps) {
  const colors = {
    low: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-red-100 text-red-800'
  };

  return (
    <Badge className={colors[priority]}>
      {priority.toUpperCase()}
    </Badge>
  );
}
```

**`frontend/src/components/tasks/SearchBar.tsx`**:

```typescript
import { Input } from '@/components/ui/input';
import { Search } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useDebouncedCallback } from 'use-debounce';

interface SearchBarProps {
  onSearch: (query: string) => void;
}

export function SearchBar({ onSearch }: SearchBarProps) {
  const [query, setQuery] = useState('');

  const debouncedSearch = useDebouncedCallback((value: string) => {
    onSearch(value);
  }, 300);

  useEffect(() => {
    debouncedSearch(query);
  }, [query, debouncedSearch]);

  return (
    <div className="relative">
      <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
      <Input
        type="text"
        placeholder="Search tasks..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="pl-10"
      />
    </div>
  );
}
```

**`frontend/src/components/tasks/FilterPanel.tsx`**:

```typescript
import { Select } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';

interface FilterPanelProps {
  onFilterChange: (filters: any) => void;
}

export function FilterPanel({ onFilterChange }: FilterPanelProps) {
  // Implement filter UI with priority, status, tags
  return (
    <div className="space-y-4">
      <div>
        <label>Priority</label>
        <Select onValueChange={(value) => onFilterChange({ priority: value })}>
          {/* Options */}
        </Select>
      </div>
      {/* More filters */}
    </div>
  );
}
```

### 5. Implement Polling for Real-Time Updates

**`frontend/src/hooks/usePolling.ts`**:

```typescript
import { useEffect, useRef } from 'react';

export function usePolling(callback: () => void, interval: number = 10000) {
  const savedCallback = useRef(callback);

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    const tick = () => savedCallback.current();
    const id = setInterval(tick, interval);
    return () => clearInterval(id);
  }, [interval]);
}
```

Usage in task list component:

```typescript
import { usePolling } from '@/hooks/usePolling';

export function TaskList() {
  const [tasks, setTasks] = useState([]);

  const fetchTasks = async () => {
    const data = await taskApi.searchTasks({});
    setTasks(data.tasks);
  };

  // Poll every 10 seconds
  usePolling(fetchTasks, 10000);

  useEffect(() => {
    fetchTasks();
  }, []);

  return (/* Task list UI */);
}
```

---

## Quick Testing

### Backend Tests

```bash
cd backend
pytest tests/unit/test_task_service.py -v
pytest tests/integration/test_search_filter.py -v
```

### Frontend Tests

```bash
cd frontend
npm test -- SearchBar.test.tsx
npm test -- FilterPanel.test.tsx
```

### Manual Testing Checklist

- [ ] Create task with priority
- [ ] Create task with due date
- [ ] Create and assign tags to tasks
- [ ] Search tasks by keyword
- [ ] Filter tasks by priority
- [ ] Filter tasks by tag
- [ ] Sort tasks by due date
- [ ] Mark recurring task as complete (verify next instance created)
- [ ] Set reminder on task with due date
- [ ] View activity log for a task
- [ ] Open app in two tabs, verify polling updates

---

## Common Issues

### Issue: APScheduler not starting

**Solution**: Ensure lifespan context manager is properly configured in `main.py`:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()

app = FastAPI(lifespan=lifespan)
```

### Issue: Tags not filtering correctly

**Solution**: Ensure JOIN query is correct:

```python
query = select(Task).join(TaskTag).join(Tag).where(
    and_(Task.user_id == user_id, Tag.name.in_(tag_names))
)
```

### Issue: Reminders not sending

**Solution**: Check scheduler logs and ensure `remind_at` index exists:

```sql
CREATE INDEX idx_reminders_remind_at_status ON reminders(remind_at, status);
```

### Issue: Activity logs impacting performance

**Solution**: Ensure async logging with BackgroundTasks:

```python
background_tasks.add_task(log_activity, user_id, action, task_id, details)
```

---

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Implement backend services and routes
3. Implement frontend components and hooks
4. Write comprehensive tests
5. Deploy and monitor

For detailed implementation guidance, see:
- `data-model.md` - Database schema and models
- `contracts/openapi.yaml` - API specifications
- `research.md` - Technical decisions and rationale

---

## Support

For questions or issues:
- Review the spec: `specs/002-advanced-task-features/spec.md`
- Check the plan: `specs/002-advanced-task-features/plan.md`
- Consult the constitution: `.specify/memory/constitution.md`
