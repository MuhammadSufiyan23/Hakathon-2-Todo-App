import os
from typing import List, Optional
from sqlmodel import Session, select
import sys
import uuid

# Import models - Conversation and Message are not used in this file, only Task is needed
# Use the same import strategy as in main.py to avoid duplicate table definitions
from models import Task  # This will use the models already loaded in main.py
from db import engine  # This will use the db already loaded in main.py


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


def add_task(user_id: str, title: str, description: Optional[str] = None,
             priority: Optional[str] = None, due_date: Optional[str] = None) -> dict:
    """
    MCP tool to add a new task for the user

    Args:
        user_id: User identifier
        title: Task title
        description: Task description (optional)
        priority: Task priority - 'low', 'medium', or 'high' (optional, defaults to 'medium')
        due_date: Due date in ISO format YYYY-MM-DD (optional)
    """
    with Session(engine) as session:
        # Validate priority
        if priority and priority not in ['low', 'medium', 'high']:
            priority = 'medium'  # Default to medium if invalid

        # Parse due_date if provided
        due_date_obj = None
        if due_date:
            try:
                from datetime import datetime
                due_date_obj = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except:
                due_date_obj = None  # Ignore invalid dates

        # Create new task
        task_data = {
            "title": title,
            "description": description,
            "user_id": user_id,
            "completed": False,
            "priority": priority or 'medium',
            "due_date": due_date_obj
        }

        new_task = Task(**task_data)
        session.add(new_task)
        session.commit()
        session.refresh(new_task)

        # Calculate displayId
        display_id = get_task_display_id(session, new_task.id, user_id)

        # ✅ DEBUG LOG
        print(f"[MCP ADD_TASK] UUID: {new_task.id}, displayId: {display_id}, title: {new_task.title}, priority: {new_task.priority}, due_date: {new_task.due_date}")

        return {
            "success": True,
            "task_id": str(new_task.id),
            "display_id": display_id,
            "task_title": new_task.title,
            "priority": new_task.priority,
            "due_date": new_task.due_date.isoformat() if new_task.due_date else None
        }


def list_tasks(user_id: str, status: Optional[str] = "all") -> dict:
    """
    MCP tool to list tasks for the user
    """
    with Session(engine) as session:
        # Build query based on status
        query = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())

        if status == "pending":
            query = query.where(Task.completed == False)
        elif status == "completed":
            query = query.where(Task.completed == True)

        tasks = session.exec(query).all()

        task_list = []
        for index, task in enumerate(tasks, start=1):
            task_list.append({
                "id": str(task.id),
                "display_id": index,  # Simple numeric ID for display
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "priority": task.priority,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None
            })

        return {
            "success": True,
            "tasks": task_list
        }


def complete_task(user_id: str, task_id: str) -> dict:
    """
    MCP tool to mark a task as completed
    Accepts UUID, display_id (numeric), or task title
    """
    with Session(engine) as session:
        task = None

        # Try 1: Parse as UUID
        try:
            uuid_task_id = uuid.UUID(task_id)
            statement = select(Task).where(Task.id == uuid_task_id, Task.user_id == user_id)
            task = session.exec(statement).first()
        except ValueError:
            pass

        # Try 2: Parse as display_id (integer)
        if not task:
            try:
                display_id = int(task_id)
                # Get all tasks in same order as list_tasks
                query = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
                all_tasks = session.exec(query).all()

                if 1 <= display_id <= len(all_tasks):
                    task = all_tasks[display_id - 1]
            except ValueError:
                pass

        # Try 3: Search by title (case-insensitive partial match)
        if not task:
            statement = select(Task).where(
                Task.user_id == user_id,
                Task.title.ilike(f"%{task_id}%")
            )
            matching_tasks = session.exec(statement).all()

            if len(matching_tasks) == 1:
                task = matching_tasks[0]
            elif len(matching_tasks) > 1:
                return {
                    "success": False,
                    "error": f"Multiple tasks match '{task_id}'. Please be more specific or use the task number."
                }

        if not task:
            return {
                "success": False,
                "error": f"Task '{task_id}' not found. Please check the task number or title."
            }

        # Update task as completed
        task.completed = True
        session.add(task)
        session.commit()
        session.refresh(task)

        return {
            "success": True,
            "task_id": str(task.id),
            "task_title": task.title,
            "completed": task.completed
        }


def delete_task(user_id: str, task_id: str) -> dict:
    """
    MCP tool to delete a task for the user
    Accepts UUID, display_id (numeric), or task title
    """
    with Session(engine) as session:
        task = None

        # Try 1: Parse as UUID
        try:
            uuid_task_id = uuid.UUID(task_id)
            statement = select(Task).where(Task.id == uuid_task_id, Task.user_id == user_id)
            task = session.exec(statement).first()
        except ValueError:
            pass

        # Try 2: Parse as display_id (integer)
        if not task:
            try:
                display_id = int(task_id)
                # Get all tasks in same order as list_tasks
                query = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
                all_tasks = session.exec(query).all()

                if 1 <= display_id <= len(all_tasks):
                    task = all_tasks[display_id - 1]
            except ValueError:
                pass

        # Try 3: Search by title (case-insensitive partial match)
        if not task:
            statement = select(Task).where(
                Task.user_id == user_id,
                Task.title.ilike(f"%{task_id}%")
            )
            matching_tasks = session.exec(statement).all()

            if len(matching_tasks) == 1:
                task = matching_tasks[0]
            elif len(matching_tasks) > 1:
                return {
                    "success": False,
                    "error": f"Multiple tasks match '{task_id}'. Please be more specific or use the task number."
                }

        if not task:
            return {
                "success": False,
                "error": f"Task '{task_id}' not found. Please check the task number or title."
            }

        # Delete the task
        task_title = task.title
        session.delete(task)
        session.commit()

        return {
            "success": True,
            "task_id": str(task.id),
            "task_title": task_title
        }


def update_task(user_id: str, task_id: str, title: Optional[str] = None, description: Optional[str] = None) -> dict:
    """
    MCP tool to update a task for the user
    Accepts UUID, display_id (numeric), or task title
    """
    with Session(engine) as session:
        task = None

        # Try 1: Parse as UUID
        try:
            uuid_task_id = uuid.UUID(task_id)
            statement = select(Task).where(Task.id == uuid_task_id, Task.user_id == user_id)
            task = session.exec(statement).first()
        except ValueError:
            pass

        # Try 2: Parse as display_id (integer)
        if not task:
            try:
                display_id = int(task_id)
                # Get all tasks in same order as list_tasks
                query = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
                all_tasks = session.exec(query).all()

                if 1 <= display_id <= len(all_tasks):
                    task = all_tasks[display_id - 1]
            except ValueError:
                pass

        # Try 3: Search by title (case-insensitive partial match)
        if not task:
            statement = select(Task).where(
                Task.user_id == user_id,
                Task.title.ilike(f"%{task_id}%")
            )
            matching_tasks = session.exec(statement).all()

            if len(matching_tasks) == 1:
                task = matching_tasks[0]
            elif len(matching_tasks) > 1:
                return {
                    "success": False,
                    "error": f"Multiple tasks match '{task_id}'. Please be more specific or use the task number."
                }

        if not task:
            return {
                "success": False,
                "error": f"Task '{task_id}' not found. Please check the task number or title."
            }

        # Update task fields if provided
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description

        session.add(task)
        session.commit()
        session.refresh(task)

        updated_fields = {}
        if title is not None:
            updated_fields["title"] = task.title
        if description is not None:
            updated_fields["description"] = task.description

        return {
            "success": True,
            "task_id": str(task.id),
            "task_title": task.title,
            "updated_fields": updated_fields
        }