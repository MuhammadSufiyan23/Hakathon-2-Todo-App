<!--
Sync Impact Report:
Version change: 1.0.0 → 1.0.0 (initial creation)
Added sections: Core Principles (6), Additional Constraints, Development Workflow, Governance
Templates requiring updates: N/A (first creation)
Follow-up TODOs: None
-->
# Hackathon II Phase 2 – Full-Stack Todo Web Application Constitution

## Core Principles

### I. Spec-Driven Development
Every feature must begin with a well-defined specification in the @specs/ directory before any implementation begins. Maintain strict separation: specs/ define WHAT and WHY (user stories, acceptance criteria), plan.md defines HOW (technical decisions), and tasks/ break implementation into testable steps. Never implement without approved specs; run sp.clarify if requirements are ambiguous.

### II. Tech Stack Loyalty
Adhere strictly to the designated technology stack: Next.js 16+ App Router with TypeScript and Tailwind CSS for frontend, FastAPI with SQLModel and Neon Serverless PostgreSQL for backend, and Better Auth with JWT for authentication. Use Next.js server components as default, 'use client' only for interactivity, and maintain centralized API clients in /lib/api.ts. Respect monorepo structure with /frontend/, /backend/, and /specs/ directories.

### III. Security & User Isolation (Non-Negotiable)
All endpoints must require valid JWT authentication returning 401 Unauthorized for invalid/missing tokens. Extract user_id from decoded JWT and filter every database query by tasks.user_id == authenticated_user_id. Never accept {user_id} in path/params after authentication - use internal filtering only. Maintain strict user data isolation preventing cross-user data exposure in all operations.

### IV. API & Database Standards
Implement RESTful endpoints following the base pattern: /api/tasks (GET list, POST create), /api/tasks/{id} (GET, PUT, DELETE, PATCH /complete). Use Pydantic models for request/response validation, HTTPException for proper error handling (404 not found, 403 forbidden), and SQLModel for database models with proper indexing on user_id and completed fields. Include auto-managed timestamps (created_at, updated_at).

### V. Code Quality & Type Safety
Maintain full type safety with TypeScript and Python type hints across the entire codebase. Implement descriptive error handling without exposing sensitive information, include comments for authentication logic and JWT filtering, and structure code for easy unit testing with small, focused functions. Follow responsive Tailwind CSS patterns and existing component architecture.

### VI. Phase 3 Preparation & Reusability
Design backend functionality as reusable skills and tools callable via FastAPI endpoints or direct database access for future AI agents and chatbots in Phase 3. Structure backend functions as modular, independent units that can be leveraged by both web UI and future AI interfaces. Prioritize clean, extensible code over quick fixes to facilitate agent integration.

## Additional Constraints

### Security Requirements
- All API endpoints require JWT authentication with proper error responses
- Database queries must filter by authenticated user_id to prevent data leakage
- Never store sensitive credentials in code; use environment variables only
- Implement proper rate limiting and input validation to prevent abuse

### Performance Standards
- API endpoints should respond within 2 seconds under normal load
- Database queries must use appropriate indexes for user_id filtering
- Frontend should implement proper loading states and error handling
- Optimize bundle sizes for faster initial page loads

### Testing Preparation
- Structure code in small, testable functions and components
- Prepare unit test infrastructure for backend API endpoints
- Design frontend components for easy testing and mocking
- Plan integration tests for auth flows and data operations

## Development Workflow

### Implementation Sequence
Follow the strict sequence: sp.constitution → sp.clarify (when ambiguity exists) → sp.plan → sp.tasks → sp.implement. Always reference relevant spec files with @specs/ notation, maintain WHAT/WHY vs HOW separation, clarify ambiguities before proceeding, and verify constitution compliance after each step.

### Review Process
All code changes must demonstrate constitution compliance with the following checklist:
- [ ] Referenced relevant @specs/ files?
- [ ] Maintained WHAT/WHY vs HOW separation?
- [ ] Enforced JWT + user_id filter in all data ops?
- [ ] Used correct stack (Next.js App Router, FastAPI/SQLModel, Tailwind)?
- [ ] Monorepo folders respected?
- [ ] Clarified ambiguities before proceeding?
- [ ] Prepared for Phase 3 reusability?

### Quality Gates
- All code must pass type checking and linting
- Authentication and authorization must be properly implemented
- Database queries must include proper user isolation
- Frontend components must follow responsive design principles
- Code must be structured for future AI agent integration

## Governance

This constitution represents immutable, non-negotiable principles that every agent, skill, spec, plan, task, and code generation must follow. All implementation work must self-check against this constitution before finalizing any output. Amendments require explicit user approval and must be documented with clear rationale. The constitution supersedes all other development practices and serves as the ultimate authority for code quality and architectural decisions.

**Version**: 1.0.0 | **Ratified**: 2026-01-14 | **Last Amended**: 2026-01-14