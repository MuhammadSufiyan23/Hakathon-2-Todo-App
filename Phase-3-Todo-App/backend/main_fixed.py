from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import logging
from sqlmodel import SQLModel
from db import engine

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import models to register them with SQLModel
from models import Task

# Create FastAPI app instance
app = FastAPI(title="Todo Backend API", version="1.0.0")

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://todosphere-app-23.vercel.app"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Additional headers for authorization
    allow_origin_regex=r"https?://localhost(:[0-9]+)?",
)

@app.on_event("startup")
async def on_startup():
    """Create database tables on startup"""
    SQLModel.metadata.create_all(engine)

# Include routes
from routes.tasks import router as tasks_router
app.include_router(tasks_router, prefix="/api/tasks", tags=["tasks"])

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Todo Backend API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)