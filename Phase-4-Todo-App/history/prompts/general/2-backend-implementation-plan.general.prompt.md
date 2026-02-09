---
id: 2
title: "Backend Implementation Plan Creation"
stage: "general"
date: "2026-01-15"
model: "Sonnet 4.5"
surface: "agent"
feature: "none"
branch: "master"
user: "king"
command: "sp.plan"
labels: ["backend", "plan", "fastapi", "sqlmodel", "implementation"]
links:
  spec: "null"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - "specs/api/todo-backend-plan.md"
tests: []
---

# Backend Implementation Plan Creation

## Original Prompt

Reference the recently generated backend specification: @specs/api/todo-backend-spec.md
Also reference:
@specs/overview.md
@specs/features/task-crud.md
@specs/api/rest-endpoints.md
@specs/database/schema.md
root CLAUDE.md and /backend/CLAUDE.md for FastAPI + SQLModel patterns

Focus STRICTLY on planning the implementation of the complete backend ONLY (FastAPI server with Neon Postgres persistence, Better Auth JWT auth, full CRUD for tasks with user isolation). Ignore frontend code, UI, agents/skills – we will integrate via API calls later.

Core Objective: Build a production-ready, secure backend that:
- Connects to Neon Postgres using the exact DATABASE_URL from .env
- Verifies JWT tokens using BETTER_AUTH_SECRET
- Enforces user ownership on every task operation
- Supports filtering (?status=pending/completed/all), sorting if added
- Handles all endpoints exactly as specified
- Returns proper JSON responses with Pydantic models
- Runs on port 8000, with CORS for frontend localhost:3000

Plan Structure (Output in clean markdown):
1. Prerequisites & Setup Steps
   - Dependencies to install: pip install fastapi uvicorn sqlmodel pydantic pyjwt python-dotenv psycopg-binary
   - Folder structure in /backend/: main.py, db.py, models.py, routes/tasks.py, schemas.py (for Pydantic), .env
   - .env file: DATABASE_URL=postgresql://neondb_owner:npg_exvVPkW2qRc4@ep-spring-firefly-a712cq9y-pooler.ap-southeast-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
     BETTER_AUTH_SECRET=3513ab71de9f07764066833058162ab07066be056b085cd636776b5a5c6d4e9e

2. High-Level Implementation Phases (sequential order – small, testable steps)
   - Phase 1: Environment & Dependencies Setup
     - Create .env, load with dotenv
     - Install packages
   - Phase 2: Database Connection (db.py)
     - Create engine with echo=True for debug
     - get_session dependency
     - Startup event to create tables (SQLModel.metadata.create_all)
   - Phase 3: Models & Schemas (models.py + schemas.py)
     - SQLModel Task class
     - Pydantic: TaskCreate, TaskUpdate, TaskRead (with id, timestamps)
   - Phase 4: Authentication Middleware (utils/auth.py or in main.py)
     - get_current_user dependency: decode JWT, extract user_id, raise 401 if invalid
     - Use HTTPBearer for token extraction
   - Phase 5: API Router & Endpoints (routes/tasks.py)
     - APIRouter(prefix="/api/tasks")
     - Each endpoint: Depends on get_session + get_current_user
     - GET / : filtered list
     - POST / : create with user_id
     - GET /{id}, PUT /{id}, DELETE /{id}, PATCH /{id}/complete
     - Ownership check on update/delete
     - Use session.exec(select(...)) for queries
     - Commit + refresh on mutations
   - Phase 6: Main App Setup (main.py)
     - FastAPI app
     - CORS middleware: origins=["http://localhost:3000"], allow_credentials=True
     - Include router
     - @app.get("/") health check
   - Phase 7: Error Handling & Logging
     - Custom exception handlers for 401/403/404
     - Print SQL queries (echo=True)
   - Phase 8: Testing & Integration Prep
     - Run: uvicorn main:app --reload --port 8000
     - Test endpoints with curl/Postman: create task, list, edit, delete
     - Verify frontend integration: call from browser (CORS), check JWT header sent

3. Key Technical Decisions
   - Use sync Session for simplicity (Neon supports async too, but sync easier for hackathon)
   - JWT decode with algorithms=["HS256"]
   - Pydantic response_model for each endpoint
   - Query params: status as Optional[str], sort as Optional[str] (implement basic sort if time)
   - Timestamps: Field(default_factory=datetime.utcnow)
   - User ID: str from JWT payload["sub"] or "user_id"

4. Dependencies List with Versions (approximate latest)
   - fastapi
   - uvicorn
   - sqlmodel
   - pydantic
   - pyjwt
   - python-dotenv
   - psycopg-binary (for Neon)

5. Potential Risks & Mitigations
   - Neon connection fail → check URL format, sslmode=require, pooler if used
   - JWT decode error → ensure secret matches frontend, token has "sub"
   - Table not created → call create_all in startup
   - CORS block → add allow_all for dev
   - Performance on list → index on user_id/completed already in schema

6. Estimated Task Breakdown Summary (for sp.tasks next)
   - Small tasks: create db.py, models, auth dependency, each endpoint one by one

7. Constitution & Spec Compliance Checklist
   - [ ] Referenced all @specs/... files?
   - [ ] Enforced JWT + user_id filter?
   - [ ] Used FastAPI + SQLModel + Neon?
   - [ ] Prepared for frontend calls (CORS, JSON)?
   - [ ] Security (401/403, no leaks)?

Output the full plan.md content suggestion (place in specs/api/todo-backend-plan.md or similar).

After plan, suggest: If plan looks good, run sp.clarify if questions, then sp.tasks to break into small backend tasks.

Execute now – create the most detailed and actionable backend implementation plan!

## Response Summary

Successfully created a comprehensive implementation plan for the Todo backend application. The plan includes:

- Detailed prerequisites and setup steps
- Eight sequential implementation phases with specific tasks
- Key technical decisions for the implementation
- Complete dependency list with versions
- Risk mitigation strategies
- Estimated task breakdown for the next phase
- Compliance checklist confirming adherence to specifications

The plan is structured to build a production-ready backend with FastAPI, SQLModel, and Neon Postgres, with proper JWT authentication and user isolation. The plan is ready for the next step: breaking down into specific implementation tasks.