from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
)

@app.on_event("startup")
async def on_startup():
    """Create database tables on startup"""
    logger.info("Starting up application...")
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created successfully")

# Custom exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom handler for HTTP exceptions"""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Custom handler for general exceptions"""
    logger.error(f"General Exception: {str(exc)}")
    logger.error(f"Exception type: {type(exc).__name__}")
    import traceback
    logger.error(f"Traceback: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log incoming requests"""
    logger.info(f"Request: {request.method} {request.url.path}")

    try:
        response = await call_next(request)
        # Safely get status code
        status_code = getattr(response, 'status_code', 'unknown')
        logger.info(f"Response status: {status_code}")
        return response
    except Exception as e:
        logger.error(f"Error in middleware: {str(e)}")
        raise

@app.get("/")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check endpoint called")
    return {"status": "healthy", "message": "Todo Backend API is running"}

# Include routes
from routes.tasks import router as tasks_router
app.include_router(tasks_router, prefix="/api/tasks", tags=["tasks"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)