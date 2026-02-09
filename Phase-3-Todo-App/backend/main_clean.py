from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from sqlmodel import SQLModel
import logging
import os
import sys

# Add the current directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import using absolute paths from the current directory
from db import engine
from models import Task, User
from routes.tasks import router as tasks_router
from routes.auth import router as auth_router
from src.api.chat import router as chat_router

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
# FastAPI App
# =======================
app = FastAPI(
    title="Todo Backend API",
    version="1.0.0"
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
        "https://todosphere-app-23.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        # Check if due_date column exists
        due_date_exists = column_exists(session, 'task', 'due_date', db_url)

        # Check if priority column exists
        priority_exists = column_exists(session, 'task', 'priority', db_url)

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

    logger.info("Database migrations completed successfully!")


# =======================
# Startup
# =======================
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
    logger.info("✅ Database initialized")

    # Run migrations to ensure all required columns exist
    run_database_migrations

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
    uvicorn.run(app, host="0.0.0.0", port=7860)