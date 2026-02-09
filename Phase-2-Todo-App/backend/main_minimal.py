from fastapi import FastAPI, Request
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
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    """Create database tables on startup"""
    SQLModel.metadata.create_all(engine)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log incoming requests"""
    logger.info(f"{request.method} {request.url.path}")

    response = await call_next(request)

    # Safely get status code
    status_code = getattr(response, 'status_code', 'unknown')
    logger.info(f"Response status: {status_code}")
    return response

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Todo Backend API is running"}

# Temporarily exclude routes to test if they're causing the issue
# from routes.tasks import router as tasks_router
# app.include_router(tasks_router, prefix="/api/tasks", tags=["tasks"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)