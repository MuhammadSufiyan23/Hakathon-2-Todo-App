"""MCP Tools Implementation for Todo App

This module implements the stateless MCP tools for the todo application as specified.
Each tool operates independently and only interacts with the database through the shared
database connection.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from sqlmodel import select, Session, SQLModel
from backend.models import Task
from backend.db import engine


def initialize_database():
    """Initialize the database tables if they don't exist"""
    SQLModel.metadata.create_all(engine)


import uuid


def list_tasks(user_id: str) -> List[Dict[str, Any]]:
    """Retrieve all tasks for a specific user.

    Args:
        user_id: The user identifier

    Returns:
        List of task dictionaries with id, title, description, priority, completed status
    """
    initialize_database()  # Ensure tables exist

    with Session(engine) as session:
        statement = select(Task).where(Task.user_id == user_id)
        tasks = session.exec(statement).all()

        result = []
        for task in tasks:
            result.append({
                "id": str(task.id),  # Convert UUID to string for JSON serialization
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "completed": task.completed
            })

        return result


def add_task(user_id: str, title: str, description: Optional[str] = None, priority: str = "medium") -> Dict[str, Any]:
    """Add a new task for a user.

    Args:
        user_id: The user identifier
        title: The task title
        description: Optional task description
        priority: Task priority ('low', 'medium', 'high'), defaults to 'medium'

    Returns:
        Dictionary with success status and created task data
    """
    initialize_database()  # Ensure tables exist

    if priority not in ["low", "medium", "high"]:
        raise ValueError(f"Invalid priority '{priority}'. Must be 'low', 'medium', or 'high'.")

    with Session(engine) as session:
        new_task = Task(
            title=title,
            description=description,
            priority=priority,
            completed=False,
            user_id=user_id
        )
        session.add(new_task)
        session.commit()
        session.refresh(new_task)

        return {
            "id": str(new_task.id),  # Convert UUID to string for JSON serialization
            "title": new_task.title,
            "description": new_task.description,
            "priority": new_task.priority,
            "completed": new_task.completed
        }


def update_task(task_id: str, user_id: str, title: Optional[str] = None,
                description: Optional[str] = None, priority: Optional[str] = None) -> Dict[str, Any]:
    """Update an existing task for a user.

    Args:
        task_id: The ID of the task to update
        user_id: The user identifier
        title: New task title (optional)
        description: New task description (optional)
        priority: New task priority (optional)

    Returns:
        Dictionary with success status and updated task data
    """
    initialize_database()  # Ensure tables exist

    # Convert task_id string to UUID
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        raise ValueError(f"Invalid task ID format: {task_id}")

    with Session(engine) as session:
        # Verify the task belongs to the user
        statement = select(Task).where(Task.id == task_uuid, Task.user_id == user_id)
        task = session.exec(statement).first()

        if not task:
            raise ValueError(f"Task {task_id} not found for user {user_id}")

        # Update fields if provided
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if priority is not None:
            if priority not in ["low", "medium", "high"]:
                raise ValueError(f"Invalid priority '{priority}'. Must be 'low', 'medium', or 'high'.")
            task.priority = priority

        session.add(task)
        session.commit()
        session.refresh(task)

        return {
            "id": str(task.id),  # Convert UUID to string for JSON serialization
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "completed": task.completed
        }


def delete_task(task_id: str, user_id: str) -> Dict[str, Any]:
    """Delete a task for a user.

    Args:
        task_id: The ID of the task to delete
        user_id: The user identifier

    Returns:
        Dictionary with success status
    """
    initialize_database()  # Ensure tables exist

    # Convert task_id string to UUID
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        raise ValueError(f"Invalid task ID format: {task_id}")

    with Session(engine) as session:
        # Verify the task belongs to the user
        statement = select(Task).where(Task.id == task_uuid, Task.user_id == user_id)
        task = session.exec(statement).first()

        if not task:
            raise ValueError(f"Task {task_id} not found for user {user_id}")

        session.delete(task)
        session.commit()

        return {
            "success": True,
            "deleted_task_id": task_id
        }


def complete_task(task_id: str, user_id: str, completed: bool = True) -> Dict[str, Any]:
    """Mark a task as completed or not completed for a user.

    Args:
        task_id: The ID of the task to update
        user_id: The user identifier
        completed: Whether the task is completed (default True)

    Returns:
        Dictionary with success status and updated task data
    """
    initialize_database()  # Ensure tables exist

    # Convert task_id string to UUID
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        raise ValueError(f"Invalid task ID format: {task_id}")

    with Session(engine) as session:
        # Verify the task belongs to the user
        statement = select(Task).where(Task.id == task_uuid, Task.user_id == user_id)
        task = session.exec(statement).first()

        if not task:
            raise ValueError(f"Task {task_id} not found for user {user_id}")

        task.completed = completed
        session.add(task)
        session.commit()
        session.refresh(task)

        return {
            "id": str(task.id),  # Convert UUID to string for JSON serialization
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "completed": task.completed
        }