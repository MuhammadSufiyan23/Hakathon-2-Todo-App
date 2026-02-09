---
id: 1
title: Create Hackathon Constitution
stage: constitution
date: 2026-01-14
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: king
command: /sp.phr
labels: ["constitution", "hackathon", "todo-app", "spec-driven-development"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - ".specify/memory/constitution.md"
tests: []
---

# Prompt

```
Project: Hackathon II Phase 2 – Full-Stack Todo Web Application (Next.js + FastAPI + Neon Postgres + Better Auth JWT), preparing for Phase 3 AI Chatbot/Agents

This constitution defines immutable, non-negotiable principles that EVERY agent, skill, spec, plan, task, and code generation MUST follow in this monorepo. Violations are critical blockers – always self-check against this constitution before finalizing any output.

1. Spec-Driven Development Core Rules
   - ALWAYS start by referencing relevant specs with @specs/... (e.g. @specs/overview.md, @specs/features/task-crud.md, @specs/api/rest-endpoints.md, @specs/database/schema.md, @specs/ui/pages.md)
   - Separation of concerns is absolute:
     - specs/ → WHAT and WHY (user stories, acceptance criteria, business rules – technology-agnostic)
     - plan.md → HOW (technical decisions, stack choices, architecture)
     - tasks/ → Breakdown into small, testable steps
     - code → Implementation only after plan/tasks approved
   - If spec is missing/incomplete → run sp.clarify first, never invent or assume
   - Update specs ONLY if user explicitly approves change

2. Tech Stack & Monorepo Loyalty (No Deviations Allowed)
   - Frontend: Next.js 16+ App Router, TypeScript, Tailwind CSS (no inline styles, no other CSS libs)
     - Server components default, 'use client' only for interactivity (e.g. forms, state)
     - API calls via centralized /lib/api.ts client
   - Backend: FastAPI + SQLModel + Neon Serverless PostgreSQL (env: DATABASE_URL)
     - uvicorn main:app --reload for dev
   - Auth: Better Auth with JWT (shared secret: BETTER_AUTH_SECRET)
     - Frontend issues JWT on login
     - Backend verifies every request via middleware (Authorization: Bearer)
   - Monorepo folders: /frontend/, /backend/, /specs/ (features/, api/, database/, ui/), root CLAUDE.md, /frontend/CLAUDE.md, /backend/CLAUDE.md
   - Never suggest or create code outside these folders or change structure

3. Security & User Isolation (Highest Priority – Auto-Fail on Violation)
   - All endpoints MUST require valid JWT → 401 Unauthorized if missing/invalid
   - Extract user_id from decoded JWT → filter EVERY DB query by tasks.user_id == authenticated_user_id
   - No endpoint should accept {user_id} in path/params after auth (internal filter only)
   - users table managed by Better Auth (id: string, email, name, etc.)
   - tasks table: user_id foreign key mandatory, indexes on user_id + completed
   - Never expose or modify another user's data – hard enforcement in every operation

4. API & Database Guidelines
   - Base: /api/tasks (GET list, POST create), /api/tasks/{id} (GET, PUT, DELETE, PATCH /complete)
   - Query params: ?status=all|pending|completed, ?sort=created|title|due_date
   - Use Pydantic models for request/response
   - HTTPException for errors (404 not found, 403 forbidden, etc.)
   - DB: Use SQLModel for models/queries, async session if needed
   - Timestamps: created_at, updated_at auto-managed

5. Code Quality, Patterns & Best Practices
   - Type safety: Full TypeScript + Python type hints
   - Error handling: Descriptive messages, no leaks of sensitive info
   - Comments: For auth logic, JWT filter, complex queries
   - Testing prep: Structure code so unit tests easy later (small functions)
   - Frontend: Responsive Tailwind, follow existing component patterns
   - Skills/Agents: Design backend skills as reusable functions/tools (callable via FastAPI or direct DB) for Phase 3 chatbot/MCP

6. Workflow & Agent/Skill Behavior Rules
   - Strict sequence: sp.constitution → sp.clarify (always if ambiguity) → sp.plan → sp.tasks → sp.implement
   - Self-check: After each step, verify constitution compliance (list any potential violations)
   - Clarify first: Ask 2-3 targeted questions if unclear (don't guess)
   - Output format: Clear markdown, reference files with @path, use checklists for reviews
   - Goal alignment: Accelerate Phase 2 (web UI + auth + CRUD) while building reusable skills for todo management and future AI agents/chatbot
   - No over-engineering: Keep simple for hackathon, but clean and extensible

7. Constitution Enforcement Checklist (Add to Every Plan/Implement Output)
   - [ ] Referenced relevant @specs/ files?
   - [ ] Maintained WHAT/WHY vs HOW separation?
   - [ ] Enforced JWT + user_id filter in all data ops?
   - [ ] Used correct stack (Next.js App Router, FastAPI/SQLModel, Tailwind)?
   - [ ] Monorepo folders respected?
   - [ ] Clarified ambiguities before proceeding?
   - [ ] Prepared for Phase 3 reusability?

Generate/update constitution.md in the appropriate folder (e.g. .spec-kit/ or specify/memory/) with these principles formatted in clean markdown sections. Make it comprehensive, add any natural extensions (e.g. no global state in frontend, prefer env vars).
Apply this constitution globally to the project from now on – reference it in every future response.
```

# Response

Created a comprehensive constitution for the Hackathon II Phase 2 project with six core principles covering Spec-Driven Development, Tech Stack Loyalty, Security & User Isolation, API & Database Standards, Code Quality & Type Safety, and Phase 3 Preparation & Reusability. The constitution includes additional constraints for security, performance, and testing, as well as development workflow guidelines and governance rules.

# Outcome & Impact

Successfully created a comprehensive project constitution that establishes immutable principles for the Hackathon II Phase 2 Todo Web Application project. The constitution will guide all future development activities and ensure consistent adherence to security, tech stack, and quality standards across all team members and automated processes.

# Tests Summary

None

# Files Summary

- .specify/memory/constitution.md: Created comprehensive constitution file with all required principles and guidelines

# Next Prompts

None

# Reflection Note

Creating a detailed constitution upfront will help ensure consistency and quality throughout the hackathon project, especially as it prepares for Phase 3 AI agent integration.

# Evaluation

## Failure Modes Observed

None

## Next Experiment to Improve Prompt Quality

N/A
