from fastapi import APIRouter
from sqlmodel import Session
from typing import List

# Import models and schemas
from models import Task
from schemas import TaskOut

# Create API router
router = APIRouter()

@router.get("/", response_model=List[TaskOut])
async def get_tasks(session: Session = None):
    """
    Get list of tasks for the current user with optional filtering and sorting
    """
    return []

# Add a simple test endpoint
@router.get("/test")
async def test_endpoint():
    return {"message": "Test endpoint works"}

if __name__ == "__main__":
    print("Minimal routes file loaded successfully")