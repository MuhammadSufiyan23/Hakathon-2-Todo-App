# from fastapi import APIRouter, Depends, HTTPException, Query
# from sqlmodel import Session, select
# from typing import List, Optional
# from datetime import datetime
# import uuid

# # Import models and schemas
# from models import Task, TaskBase
# from schemas import TaskCreate, TaskUpdate, TaskOut
# from db import get_session
# from utils.auth import get_current_user

# # Create API router
# router = APIRouter(
#     prefix="/api/tasks",
#     tags=["tasks"]
# )


# @router.get("/", response_model=List[TaskOut])
# async def get_tasks(
#     current_user: dict = Depends(get_current_user),
#     session: Session = Depends(get_session),
#     status: Optional[str] = Query("all", description="Filter by completion status (all/pending/completed)"),
#     sort: Optional[str] = Query("created", description="Sort by (created/title)"),
#     order: Optional[str] = Query("desc", description="Sort order (asc/desc)")
# ):
#     """
#     Get list of tasks for the current user with optional filtering and sorting
#     """
#     # Build query with user_id filter
#     query = select(Task).where(Task.user_id == current_user["user_id"])

#     # Apply status filter
#     if status == "pending":
#         query = query.where(Task.completed == False)
#     elif status == "completed":
#         query = query.where(Task.completed == True)
#     # "all" status includes all tasks

#     # Apply sorting
#     if sort == "title":
#         if order == "asc":
#             query = query.order_by(Task.title)
#         else:
#             query = query.order_by(Task.title.desc())
#     else:  # Default or "created"
#         if order == "asc":
#             query = query.order_by(Task.created_at)
#         else:
#             query = query.order_by(Task.created_at.desc())

#     # Execute query
#     tasks = session.exec(query).all()
#     return tasks


# # @router.post("/", response_model=TaskOut, status_code=201)
# # async def create_task(
# #     task_data: TaskCreate,
# #     current_user: dict = Depends(get_current_user),
# #     session: Session = Depends(get_session)
# # ):
# #     """
# #     Create a new task for the current user
# #     """
# #     # Create task instance with user_id from JWT
# #     task = Task(
# #         **task_data.model_dump(),
# #         user_id=current_user["user_id"]
# #     )

# #     # Add to session and commit
# #     session.add(task)
# #     session.commit()
# #     session.refresh(task)

# #     return task



# @router.post("/", response_model=TaskOut, status_code=201)
# async def create_task(
#     task_data: TaskCreate,
#     current_user: dict = Depends(get_current_user),
#     session: Session = Depends(get_session)
# ):
#     """
#     Create a new task for the current user
#     """
#     print("Received task data from frontend:", task_data.model_dump())  

#     # Create task instance with user_id from JWT
#     task = Task(
#         **task_data.model_dump(),
#         user_id=current_user["user_id"]
#     )

#     # Add to session and commit
#     session.add(task)
#     session.commit()
#     session.refresh(task)

#     # print("Saved task in database:", task.__dict__)  # Ye line bhi add karo

#     return task


# @router.get("/{id}", response_model=TaskOut)
# async def get_task(
#     id: str,
#     current_user: dict = Depends(get_current_user),
#     session: Session = Depends(get_session)
# ):
#     """
#     Get a specific task by ID for the current user
#     """
#     try:
#         # Convert string ID to UUID
#         task_id = uuid.UUID(id)
#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid task ID format")

#     # Find task by ID and user_id to ensure ownership
#     task = session.exec(
#         select(Task).where(Task.id == task_id, Task.user_id == current_user["user_id"])
#     ).first()

#     if not task:
#         raise HTTPException(status_code=404, detail="Task not found or access denied")

#     return task


# @router.put("/{id}", response_model=TaskOut)
# async def update_task(
#     id: str,
#     task_data: TaskUpdate,
#     current_user: dict = Depends(get_current_user),
#     session: Session = Depends(get_session)
# ):
#     """
#     Update a specific task by ID for the current user
#     """
#     try:
#         # Convert string ID to UUID
#         task_id = uuid.UUID(id)
#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid task ID format")

#     # Find task by ID and user_id to ensure ownership
#     task = session.exec(
#         select(Task).where(Task.id == task_id, Task.user_id == current_user["user_id"])
#     ).first()

#     if not task:
#         raise HTTPException(status_code=404, detail="Task not found or access denied")

#     # Update task with provided data
#     update_data = task_data.model_dump(exclude_unset=True)
#     for field, value in update_data.items():
#         setattr(task, field, value)

#     # Update timestamp
#     task.updated_at = datetime.utcnow()

#     # Commit changes
#     session.add(task)
#     session.commit()
#     session.refresh(task)

#     return task


# @router.delete("/{id}")
# async def delete_task(
#     id: str,
#     current_user: dict = Depends(get_current_user),
#     session: Session = Depends(get_session)
# ):
#     """
#     Delete a specific task by ID for the current user
#     """
#     try:
#         # Convert string ID to UUID
#         task_id = uuid.UUID(id)
#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid task ID format")

#     # Find task by ID and user_id to ensure ownership
#     task = session.exec(
#         select(Task).where(Task.id == task_id, Task.user_id == current_user["user_id"])
#     ).first()

#     if not task:
#         raise HTTPException(status_code=404, detail="Task not found or access denied")

#     # Delete the task
#     session.delete(task)
#     session.commit()

#     return {"message": "Task deleted successfully"}


# @router.patch("/{id}/complete", response_model=TaskOut)
# async def toggle_task_completion(
#     id: str,
#     current_user: dict = Depends(get_current_user),
#     session: Session = Depends(get_session)
# ):
#     """
#     Toggle the completion status of a specific task for the current user
#     """
#     try:
#         # Convert string ID to UUID
#         task_id = uuid.UUID(id)
#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid task ID format")

#     # Find task by ID and user_id to ensure ownership
#     task = session.exec(
#         select(Task).where(Task.id == task_id, Task.user_id == current_user["user_id"])
#     ).first()

#     if not task:
#         raise HTTPException(status_code=404, detail="Task not found or access denied")

#     # Toggle completion status
#     task.completed = not task.completed
#     task.updated_at = datetime.utcnow()

#     # Commit changes
#     session.add(task)
#     session.commit()
#     session.refresh(task)

#     return task


# @router.patch("/{id}/toggle-completion", response_model=TaskOut)
# async def toggle_task_completion_alt(
#     id: str,
#     current_user: dict = Depends(get_current_user),
#     session: Session = Depends(get_session)
# ):
#     """
#     Toggle the completion status of a specific task for the current user (alternative endpoint)
#     """
#     try:
#         # Convert string ID to UUID
#         task_id = uuid.UUID(id)
#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid task ID format")

#     # Find task by ID and user_id to ensure ownership
#     task = session.exec(
#         select(Task).where(Task.id == task_id, Task.user_id == current_user["user_id"])
#     ).first()

#     if not task:
#         raise HTTPException(status_code=404, detail="Task not found or access denied")

#     # Toggle completion status
#     task.completed = not task.completed
#     task.updated_at = datetime.utcnow()

#     # Commit changes
#     session.add(task)
#     session.commit()
#     session.refresh(task)

#     return task







from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
import uuid

from models import Task
from schemas import TaskCreate, TaskUpdate, TaskOut
from db import get_session
from utils.auth import get_current_user

# ❗ IMPORTANT: yahan prefix NAHI hoga
router = APIRouter(
    tags=["tasks"]
)

@router.get("/", response_model=List[TaskOut])
async def get_tasks(
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
    status: Optional[str] = Query("all"),
    sort: Optional[str] = Query("created"),
    order: Optional[str] = Query("desc")
):
    query = select(Task).where(Task.user_id == current_user["user_id"])

    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)

    if sort == "title":
        query = query.order_by(Task.title.asc() if order == "asc" else Task.title.desc())
    else:
        query = query.order_by(Task.created_at.asc() if order == "asc" else Task.created_at.desc())

    return session.exec(query).all()


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
    return task


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

    return task


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

    for key, value in task_data.model_dump(exclude_unset=True).items():
        setattr(task, key, value)

    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)

    return task


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
    return task
