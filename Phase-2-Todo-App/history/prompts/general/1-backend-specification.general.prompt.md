---
id: 1
title: "Backend Specification Creation"
stage: "general"
date: "2026-01-15"
model: "Sonnet 4.5"
surface: "agent"
feature: "none"
branch: "master"
user: "king"
command: "sp.specify"
labels: ["backend", "specification", "fastapi", "sqlmodel", "authentication"]
links:
  spec: "null"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - "specs/api/todo-backend-spec.md"
  - "specs/api/checklists/requirements.md"
tests: []
---

# Backend Specification Creation

## Original Prompt

Focus STRICTLY on creating a complete, detailed backend specification for the Hackathon II Phase 2 Todo Full-Stack Web Application. Ignore frontend, agents, skills, and any unrelated parts – only backend (FastAPI, SQLModel, Neon Postgres, Better Auth JWT integration).

Project references (ALWAYS reference these):
@specs/overview.md
@specs/features/task-crud.md
@specs/api/rest-endpoints.md (REST endpoints, methods, descriptions, request/response models, query params for status/sort)
@specs/database/schema.md (tables: users from Better Auth, tasks with id, user_id FK, title, description, completed, created_at, updated_at; indexes on user_id, completed)
root CLAUDE.md and /backend/CLAUDE.md for FastAPI patterns (main.py entry, models.py, routes/, db.py connection, Pydantic for req/res, HTTPException errors)

Core Goal: The backend MUST be secure, efficient, and fully functional – handle all CRUD operations for tasks with user isolation via JWT, persist data in Neon Postgres, support filtering/sorting, integrate seamlessly with frontend API calls.

Key Non-Negotiable Requirements:
- Use Python FastAPI for API server
- SQLModel for ORM/models/queries (sync or async sessions)
- Neon Serverless PostgreSQL via env DATABASE_URL (postgresql://neondb_owner:npg_exvVPkW2qRc4@ep-spring-firefly-a712cq9y-pooler.ap-southeast-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require)
- Authentication: Better Auth JWT verification middleware
  - Shared secret: BETTER_AUTH_SECRET=3513ab71de9f07764066833058162ab07066be056b085cd636776776b5a5c6d4e9e
  - Extract token from Authorization: Bearer header
  - Decode with PyJWT or similar to get user_id/email
  - Enforce user_id on all task operations (filter queries, check ownership on update/delete)
  - Return 401 Unauthorized if token missing/invalid/expired
- User table managed by Better Auth (id: string, email, name, created_at – no manual handling)
- Task model: As per schema, with auto timestamps
- Error handling: HTTPException for 400 (validation), 401 (auth), 403 (forbidden, wrong user), 404 (not found), 500 (server)
- Environment: .env in backend folder for DATABASE_URL and BETTER_AUTH_SECRET
- Testing prep: Add debug logs (e.g. print SQL queries with echo=True in engine)

API Endpoints to Specify (full details: methods, paths, params, body, response, security):
- GET /api/tasks: List user's tasks, query params: status (all/pending/completed), sort (created/title/due_date – note: due_date if added later)
- POST /api/tasks: Create task, body: {title: str required, description: str optional}
- GET /api/tasks/{id}: Get single task details (check user_id)
- PUT /api/tasks/{id}: Update task, body: {title, description optional}
- DELETE /api/tasks/{id}: Delete task
- PATCH /api/tasks/{id}/complete: Toggle completed bool

Backend Structure:
- main.py: FastAPI app, middleware for JWT, include routers, startup for DB create_all
- db.py: Engine, get_session dependency (Session)
- models.py: SQLModel Task class, Pydantic for TaskCreate/TaskUpdate/TaskOut (with id, timestamps)
- routes/tasks.py: APIRouter for /api/tasks, dependencies on get_session and get_current_user
- utils/auth.py: JWT decode function, get_current_user dependency

Integration with Frontend:
- Frontend calls via http://localhost:3000 (BETTER_AUTH_URL), but backend runs on port 8000 (uvicorn main:app --reload --port 8000)
- CORS middleware: allow origins ["http://localhost:3000"], methods/headers all
- Ensure responses JSON serializable (SQLModel to dict or Pydantic)

Acceptance Criteria:
- Tasks persist in Neon DB after create/update
- Only authenticated user's tasks accessible
- Filters work: status param filters correctly
- Sorting: by created_at desc default, or query param
- Timestamps auto-updated on update
- Validation: title 1-200 chars, description max 1000
- Performance: Indexes used for user_id/completed
- Security: No SQL injection (SQLModel safe), JWT expiry handled (e.g. 7 days)

Generate a detailed, comprehensive specification markdown file:
Place in: specs/api/todo-backend-spec.md

Sections:
- Overview & Architecture
- Environment & Setup (.env, dependencies: pip install fastapi uvicorn sqlmodel pyjwt pydantic)
- Database Connection & Schema
- Models & Pydantic Schemas
- Authentication & JWT Middleware
- API Endpoints (detail each: path, method, params, body, response, errors)
- Error Handling & Logging
- CORS & Security
- Testing & Integration with Frontend
- Edge Cases (e.g. invalid id, no tasks, expiry token)

After spec, suggest next: sp.clarify if needed, then sp.plan for backend implementation.

Execute now – make this the most complete backend spec for seamless frontend integration!

## Response Summary

Successfully created a comprehensive backend specification for the Todo application. The specification includes:

- Detailed architecture overview with FastAPI, SQLModel, and Neon Postgres
- Complete environment setup with dependencies and environment variables
- Database schema definition with proper indexing
- Models and Pydantic schemas for request/response handling
- JWT authentication middleware implementation
- Full API endpoint documentation with methods, parameters, and error handling
- Error handling and logging strategies
- CORS and security configurations
- Frontend integration guidelines
- Edge case considerations

The specification is ready for the next phase: backend implementation planning.