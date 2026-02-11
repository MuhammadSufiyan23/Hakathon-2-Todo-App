from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from sqlmodel import SQLModel
from contextlib import asynccontextmanager
import logging

import os
import sys

# Add the backend directory to Python path to enable proper imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Also add parent directory in case we need to import from there
parent_dir = os.path.dirname(backend_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import models first to ensure they're registered only once
from models import Task, User, Tag, TaskTag, Reminder, ActivityLog  # Import models first to register them with SQLModel

# Try different import strategies for other components
try:
    # Try absolute imports (when installed as package)
    from backend.db import engine
    from backend.routes.tasks import router as tasks_router  # This will reuse already-loaded models
    from backend.routes.auth import router as auth_router
    from backend.src.api.chat import router as chat_router
except ImportError:
    try:
        # Try relative imports (when running as module)
        from .db import engine
        from .routes.tasks import router as tasks_router  # This will reuse already-loaded models
        from .routes.auth import router as auth_router
        from .src.api.chat import router as chat_router
    except ImportError:
        # Direct imports when running from the backend directory
        from db import engine
        from routes.tasks import router as tasks_router  # This will reuse already-loaded models
        from routes.auth import router as auth_router
        from src.api.chat import router as chat_router

# Import scheduler
try:
    from backend.scheduler.reminder_scheduler import start_scheduler, stop_scheduler
except ImportError:
    try:
        from .scheduler.reminder_scheduler import start_scheduler, stop_scheduler
    except ImportError:
        from scheduler.reminder_scheduler import start_scheduler, stop_scheduler

# =======================
# Load ENV
# =======================
load_dotenv()

# =======================
# Logging
# =======================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("todo-backend")

# =======================
# Database Migration Helper
# =======================
def run_database_migrations():
    """Run database migrations to ensure all required columns exist."""
    from sqlmodel import Session
    from sqlalchemy import text

    # Determine database type
    db_url = str(engine.url)
    db_type = "PostgreSQL" if ('postgresql' in db_url or 'postgres' in db_url) else "SQLite"

    logger.info(f"Running database migrations for {db_type}...")

    def column_exists(session, table_name, column_name, db_url):
        """Check if a column exists in a table."""
        if 'postgresql' in db_url or 'postgres' in db_url:
            result = session.execute(text(f"""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = '{table_name}' AND column_name = '{column_name}'
            """))
            return result.fetchone() is not None
        else:
            # SQLite: Get table info and check if column exists
            result = session.execute(text(f"PRAGMA table_info({table_name})"))
            columns_info = result.fetchall()
            column_names = [row[1] for row in columns_info]  # Column name is at index 1 in PRAGMA result
            return column_name in column_names

    with Session(engine) as session:
        # Check if columns exist
        due_date_exists = column_exists(session, 'task', 'due_date', db_url)
        priority_exists = column_exists(session, 'task', 'priority', db_url)
        is_recurring_exists = column_exists(session, 'task', 'is_recurring', db_url)
        recurrence_rule_exists = column_exists(session, 'task', 'recurrence_rule', db_url)
        completed_at_exists = column_exists(session, 'task', 'completed_at', db_url)

        # Add due_date column if it doesn't exist
        if not due_date_exists:
            logger.info("Adding due_date column to task table...")
            if 'postgresql' in db_url or 'postgres' in db_url:
                session.execute(text("ALTER TABLE task ADD COLUMN due_date TIMESTAMP WITH TIME ZONE"))
            else:
                session.execute(text("ALTER TABLE task ADD COLUMN due_date DATETIME"))
            session.commit()
            logger.info("[SUCCESS] due_date column added successfully")

        # Add priority column if it doesn't exist
        if not priority_exists:
            logger.info("Adding priority column to task table...")
            if 'postgresql' in db_url or 'postgres' in db_url:
                session.execute(text("ALTER TABLE task ADD COLUMN priority VARCHAR(20) DEFAULT 'medium'"))
            else:
                session.execute(text("ALTER TABLE task ADD COLUMN priority TEXT DEFAULT 'medium'"))
            session.commit()
            logger.info("[SUCCESS] priority column added successfully")

        # Add is_recurring column if it doesn't exist
        if not is_recurring_exists:
            logger.info("Adding is_recurring column to task table...")
            if 'postgresql' in db_url or 'postgres' in db_url:
                session.execute(text("ALTER TABLE task ADD COLUMN is_recurring BOOLEAN DEFAULT FALSE"))
            else:
                session.execute(text("ALTER TABLE task ADD COLUMN is_recurring INTEGER DEFAULT 0"))
            session.commit()
            logger.info("[SUCCESS] is_recurring column added successfully")

        # Add recurrence_rule column if it doesn't exist
        if not recurrence_rule_exists:
            logger.info("Adding recurrence_rule column to task table...")
            if 'postgresql' in db_url or 'postgres' in db_url:
                session.execute(text("ALTER TABLE task ADD COLUMN recurrence_rule VARCHAR(100)"))
            else:
                session.execute(text("ALTER TABLE task ADD COLUMN recurrence_rule TEXT"))
            session.commit()
            logger.info("[SUCCESS] recurrence_rule column added successfully")

        # Add completed_at column if it doesn't exist
        if not completed_at_exists:
            logger.info("Adding completed_at column to task table...")
            if 'postgresql' in db_url or 'postgres' in db_url:
                session.execute(text("ALTER TABLE task ADD COLUMN completed_at TIMESTAMP WITH TIME ZONE"))
            else:
                session.execute(text("ALTER TABLE task ADD COLUMN completed_at DATETIME"))
            session.commit()
            logger.info("[SUCCESS] completed_at column added successfully")

    logger.info("Database migrations completed successfully!")

# =======================
# Lifespan Context Manager
# =======================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan: startup and shutdown events."""
    # Startup
    logger.info("🚀 Starting application...")

    # Create all tables - models will be registered during import
    SQLModel.metadata.create_all(engine)
    logger.info("✅ Database initialized")

    # Run migrations to ensure all required columns exist
    run_database_migrations()

    # Start the reminder scheduler
    start_scheduler()

    yield

    # Shutdown
    logger.info("🛑 Shutting down application...")
    stop_scheduler()
    logger.info("✅ Application shutdown complete")

# =======================
# FastAPI App
# =======================
app = FastAPI(
    title="Todo Backend API",
    version="1.0.0",
    lifespan=lifespan
)

# =======================
# 🔐 Proxy / HTTPS SAFE FIX (HF + Vercel)
# =======================
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

app.router.redirect_slashes = True

@app.middleware("http")
async def proxy_https_fix(request: Request, call_next):
    if request.headers.get("x-forwarded-proto") == "https":
        request.scope["scheme"] = "https"
    return await call_next(request)

# =======================
# 🌍 CORS
# =======================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://todosphere-app-23.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =======================
# Exception Handlers
# =======================
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"❌ Server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# =======================
# Request Logger
# =======================
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"➡️ {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"⬅️ Status {response.status_code}")
    return response

# =======================
# Health Check
# =======================
@app.get("/")
def health_check():
    return {"status": "ok"}

# =======================
# Routes
# =======================
app.include_router(tasks_router, prefix="/api/tasks", tags=["tasks"])
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(chat_router, prefix="/api", tags=["chat"])

# =======================
# Local Run (Safe for HF)
# =======================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)