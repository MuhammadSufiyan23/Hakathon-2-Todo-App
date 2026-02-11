

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
import uuid

from models import Task
from schemas import TaskCreate, TaskUpdate, TaskOut
from db import get_session
from utils.auth import get_current_user

# Import ActivityService for activity logging
try:
    from backend.src.services.activity_service import ActivityService
except ImportError:
    try:
        from src.services.activity_service import ActivityService
    except ImportError:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from src.services.activity_service import ActivityService


def get_task_display_id(session: Session, task_id: uuid.UUID, user_id: str) -> int:
    """
    Calculate the display ID for a task based on its position in the user's task list.
    Tasks are ordered by created_at descending (newest first).
    """
    query = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
    all_tasks = session.exec(query).all()

    for index, task in enumerate(all_tasks, start=1):
        if task.id == task_id:
            return index

    return 0  # Fallback if task not found

# ❗ IMPORTANT: yahan prefix NAHI hoga
router = APIRouter(
    tags=["tasks"]
)

@router.get("/", response_model=List[TaskOut])
async def get_tasks(
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
    status: Optional[str] = Query("all"),
    priority: Optional[str] = Query(None),  # New: priority filter
    sort: Optional[str] = Query("created"),
    order: Optional[str] = Query("desc")
):
    query = select(Task).where(Task.user_id == current_user["user_id"])

    # Status filter
    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)

    # Priority filter (US1)
    if priority and priority in ['low', 'medium', 'high']:
        query = query.where(Task.priority == priority)

    # Sorting
    if sort == "title":
        query = query.order_by(Task.title.asc() if order == "asc" else Task.title.desc())
    elif sort == "priority":
        # Sort by priority: high > medium > low
        priority_order = {"high": 1, "medium": 2, "low": 3}
        # For now, use created_at as fallback (proper priority sorting requires CASE statement)
        query = query.order_by(Task.created_at.asc() if order == "asc" else Task.created_at.desc())
    else:
        query = query.order_by(Task.created_at.asc() if order == "asc" else Task.created_at.desc())

    tasks = session.exec(query).all()

    # Add displayId to each task (camelCase for frontend compatibility)
    tasks_with_display_id = []
    for index, task in enumerate(tasks, start=1):
        task_dict = task.model_dump()
        task_dict['displayId'] = index
        tasks_with_display_id.append(task_dict)

    return tasks_with_display_id


@router.post("/", response_model=TaskOut, status_code=201)
async def create_task(
    task_data: TaskCreate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    task = Task(
        **task_data.model_dump(),
        user_id=current_user["user_id"]
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    # Log activity
    activity_service = ActivityService()
    await activity_service.log_activity(
        user_id=current_user["user_id"],
        action="task_created",
        task_id=str(task.id),
        details={"title": task.title, "priority": task.priority}
    )

    # Calculate and add displayId
    display_id = get_task_display_id(session, task.id, current_user["user_id"])
    task_dict = task.model_dump()
    task_dict['displayId'] = display_id

    # ✅ DEBUG LOG
    print(f"[CREATE TASK] UUID: {task.id}, displayId: {display_id}, title: {task.title}")

    return task_dict


@router.get("/{id}", response_model=TaskOut)
async def get_task(
    id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    try:
        task_id = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task ID")

    task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == current_user["user_id"])
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Calculate and add displayId
    display_id = get_task_display_id(session, task.id, current_user["user_id"])
    task_dict = task.model_dump()
    task_dict['displayId'] = display_id

    return task_dict


@router.put("/{id}", response_model=TaskOut)
async def update_task(
    id: str,
    task_data: TaskUpdate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    task_id = uuid.UUID(id)

    task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == current_user["user_id"])
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Track changes for activity logging
    changes = {}
    old_priority = task.priority

    for key, value in task_data.model_dump(exclude_unset=True).items():
        if hasattr(task, key):
            old_value = getattr(task, key)
            if old_value != value:
                changes[key] = {"old": old_value, "new": value}
            setattr(task, key, value)

    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)

    # Log activity if priority changed
    if "priority" in changes:
        activity_service = ActivityService()
        await activity_service.log_activity(
            user_id=current_user["user_id"],
            action="task_updated",
            task_id=str(task.id),
            details={
                "title": task.title,
                "field": "priority",
                "old_value": changes["priority"]["old"],
                "new_value": changes["priority"]["new"]
            }
        )

    # Calculate and add displayId
    display_id = get_task_display_id(session, task.id, current_user["user_id"])
    task_dict = task.model_dump()
    task_dict['displayId'] = display_id

    return task_dict


@router.delete("/{id}")
async def delete_task(
    id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    task_id = uuid.UUID(id)

    task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == current_user["user_id"])
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()
    return {"message": "Task deleted"}


@router.patch("/{id}/toggle-completion", response_model=TaskOut)
async def toggle_task_completion(
    id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    task_id = uuid.UUID(id)

    task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == current_user["user_id"])
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    # Calculate and add displayId
    display_id = get_task_display_id(session, task.id, current_user["user_id"])
    task_dict = task.model_dump()
    task_dict['displayId'] = display_id

    return task_dict
