# from fastapi import FastAPI, HTTPException, Request
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
# from fastapi.responses import JSONResponse
# from dotenv import load_dotenv
# import logging
# from sqlmodel import SQLModel
# from db import engine

# # =======================
# # Load ENV
# # =======================
# load_dotenv()

# # =======================
# # Logging
# # =======================
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # =======================
# # Import Models
# # =======================
# from models import Task, User

# # =======================
# # FastAPI App
# # =======================
# app = FastAPI(
#     title="Todo Backend API",
#     version="1.0.0"
# )

# # =======================
# # 🔒 FORCE HTTPS (CRITICAL FIX)
# # =======================
# # app.add_middleware(HTTPSRedirectMiddleware)

# # =======================
# # 🌍 CORS (PRODUCTION READY)
# # =======================
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000", "https://frontend-gamma-pink-23.vercel.app"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # =======================
# # Startup
# # =======================
# @app.on_event("startup")
# async def on_startup():
#     logger.info("Starting up application...")
#     SQLModel.metadata.create_all(engine)
#     logger.info("Database tables created successfully")

# # =======================
# # Exception Handlers
# # =======================
# @app.exception_handler(HTTPException)
# async def http_exception_handler(request: Request, exc: HTTPException):
#     logger.error(f"HTTP Exception {exc.status_code}: {exc.detail}")
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"detail": exc.detail},
#     )

# @app.exception_handler(Exception)
# async def general_exception_handler(request: Request, exc: Exception):
#     logger.error(f"Unhandled Exception: {str(exc)}")
#     import traceback
#     logger.error(traceback.format_exc())
#     return JSONResponse(
#         status_code=500,
#         content={"detail": "Internal server error"},
#     )

# # =======================
# # Request Logger
# # =======================
# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     logger.info(f"Request: {request.method} {request.url.path}")
#     response = await call_next(request)
#     logger.info(f"Response status: {response.status_code}")
#     return response

# # =======================
# # OPTIONS (CORS PREFLIGHT FIX)
# # =======================
# @app.options("/api/auth/signup")
# async def options_auth_signup():
#     return {"detail": "OK"}

# @app.options("/api/auth/login")
# async def options_auth_login():
#     return {"detail": "OK"}

# @app.options("/api/auth/logout")
# async def options_auth_logout():
#     return {"detail": "OK"}

# @app.options("/api/auth/profile")
# async def options_auth_profile():
#     return {"detail": "OK"}

# @app.options("/api/auth/{path:path}")
# async def options_auth_catch_all(path: str):
#     return {"detail": "OK"}

# @app.options("/api/tasks")
# async def options_tasks():
#     return {"detail": "OK"}

# @app.options("/api/tasks/{path:path}")
# async def options_tasks_catch_all(path: str):
#     return {"detail": "OK"}

# # =======================
# # Health Check
# # =======================
# @app.get("/")
# async def health_check():
#     logger.info("Health check endpoint called")
#     return {
#         "status": "healthy",
#         "message": "Todo Backend API is running"
#     }

# # =======================
# # Routes
# # =======================
# from routes.tasks import router as tasks_router
# app.include_router(tasks_router, prefix="/api/tasks", tags=["tasks"])

# from routes.auth import router as auth_router
# app.include_router(auth_router, prefix="/api/auth", tags=["auth"])

# # =======================
# # Local Run
# # =======================
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=7860)


# =========================================================================

# from fastapi import FastAPI, HTTPException, Request
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# from fastapi.middleware.trustedhost import TrustedHostMiddleware
# from dotenv import load_dotenv
# import logging
# from sqlmodel import SQLModel
# from db import engine

# load_dotenv()

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# from models import Task, User

# app = FastAPI(
#     title="Todo Backend API",
#     version="1.0.0"
# )

# # 🔐 SECURITY FIX: Add Trusted Host Middleware to handle HTTPS properly
# app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# # 🔑 IMPORTANT FIX
# app.router.redirect_slashes = True

# # Add custom middleware to handle HTTPS redirects properly
# @app.middleware("http")
# async def force_https_middleware(request: Request, call_next):
#     # Check if we're behind a proxy and the original protocol was HTTPS
#     forwarded_proto = request.headers.get('x-forwarded-proto', '').lower()
#     if forwarded_proto == 'https':
#         # Update the request URL to reflect HTTPS
#         request.scope['scheme'] = 'https'

#     response = await call_next(request)
#     return response

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:3000",
#         "https://frontend-gamma-pink-23.vercel.app"
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.on_event("startup")
# async def startup():
#     SQLModel.metadata.create_all(engine)
#     logger.info("Database ready")

# @app.exception_handler(HTTPException)
# async def http_error(request: Request, exc: HTTPException):
#     return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

# @app.exception_handler(Exception)
# async def server_error(request: Request, exc: Exception):
#     logger.error(str(exc))
#     return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

# @app.middleware("http")
# async def logger_middleware(request: Request, call_next):
#     logger.info(f"{request.method} {request.url.path}")
#     response = await call_next(request)
#     logger.info(f"Status {response.status_code}")
#     return response

# @app.get("/")
# async def health():
#     return {"status": "ok"}

# # ROUTES
# from routes.tasks import router as tasks_router
# from routes.auth import router as auth_router

# app.include_router(tasks_router, prefix="/api/tasks")
# app.include_router(auth_router, prefix="/api/auth")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=7860)



# =======================================================================================



from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from sqlmodel import SQLModel
import logging

from db import engine
from models import Task, User
from routes.tasks import router as tasks_router
from routes.auth import router as auth_router

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
        "https://frontend-gamma-pink-23.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =======================
# Startup
# =======================
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
    logger.info("✅ Database initialized")

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

# =======================
# Local Run (Safe for HF)
# =======================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)








