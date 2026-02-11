# Implementation Plan: Advanced Task Management Features

**Branch**: `002-advanced-task-features` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-advanced-task-features/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This plan implements Phase III-IV intermediate and advanced task management features within the existing FastAPI backend and Next.js frontend. Features include: priorities (low/medium/high), tags (user-defined labels), search/filter/sort capabilities, due dates with overdue indicators, reminders (scheduled notifications), recurring tasks (daily/weekly/monthly patterns), and activity audit logs. Phase V cloud-native features (Kafka, Dapr, Kubernetes) are explicitly deferred and will be implemented in a future phase.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/JavaScript (frontend with Next.js 14+)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, Pydantic, APScheduler (for reminders), Neon Serverless PostgreSQL
- Frontend: Next.js 14 (App Router), React 18+, Better Auth, TailwindCSS, shadcn/ui components
**Storage**: Neon Serverless PostgreSQL (existing database, will add new tables and columns)
**Testing**: pytest (backend), Jest/React Testing Library (frontend)
**Target Platform**: Web application (browser-based), deployed on Vercel (frontend) and cloud platform (backend)
**Project Type**: Web application (separate backend and frontend)
**Performance Goals**:
- Search/filter/sort operations: <500ms for up to 1000 tasks per user
- API response time: <2 seconds for MCP tool operations
- Reminder delivery: within 1 minute of scheduled time
- Recurring task creation: <5 seconds after completion
**Constraints**:
- Must maintain existing Phase I-II backend logic untouched
- Must use existing Better Auth authentication
- Must maintain stateless backend architecture
- Must respect user_id boundaries for all operations
- Phase V features (Kafka, Dapr, Kubernetes) explicitly deferred
**Scale/Scope**:
- Support 100+ concurrent users
- Handle up to 1000 tasks per user efficiently
- 8 new user stories with 26+ functional requirements
- Database schema extensions (4 new tables, 8 new columns)

## Phase V Features (Deferred)

**Note**: Event-Driven Architecture (Kafka), Dapr Components, and Kubernetes Deployment are explicitly deferred to Phase V. This plan focuses exclusively on Phase III-IV features within the existing backend and frontend architecture.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Compliance Items

- **MCP-First Operations**: All task operations will continue to use existing MCP tools (add_task, list_tasks, complete_task, delete_task, update_task). New features will extend these tools with additional parameters.
- **Statelessness Requirement**: Backend remains stateless. No conversational state stored in RAM. All context reconstructed from database per request.
- **User Context & Security**: All operations filtered by authenticated user_id from Better Auth. No cross-user data access.
- **Existing Backend Logic**: Phase I-II backend logic remains untouched. New features are additive only.
- **Database Isolation**: All queries include user_id filtering to maintain data isolation.

### ⚠️ New Requirements (Phase III-IV Specific)

- **Background Scheduler**: APScheduler will be added to backend for reminder checks. This is a new dependency but required for FR-020 (reminder notifications).
- **Database Schema Changes**: Adding 4 new tables (task_tags, reminders, recurring_tasks, activity_logs) and 8 new columns to existing tasks table. Migration strategy required.
- **Polling Mechanism**: Frontend will implement periodic polling (10-second interval) for real-time updates (FR-025, FR-026). This is acceptable for Phase III-IV; WebSocket deferred to Phase V.

### 🔍 Clarifications Needed (Phase 0 Research)

- **APScheduler Integration**: How to integrate APScheduler with FastAPI without blocking the main event loop?
- **Database Migration Strategy**: How to safely migrate existing tasks table with new columns while maintaining backward compatibility?
- **Tag Storage Pattern**: Should tags be stored as JSON array in tasks table or normalized in separate task_tags junction table?
- **Recurring Task Logic**: What's the best pattern for recurrence rule storage and next-instance calculation?
- **Activity Log Performance**: How to efficiently log all operations without impacting API response times?

## Project Structure

### Documentation (this feature)

```text
specs/002-advanced-task-features/
├── spec.md              # Feature specification (already exists)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── openapi.yaml     # API contract definitions
│   └── schemas.json     # Data schemas
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/
│   │   ├── task.py              # Extended with new fields (priority, tags, due_date, etc.)
│   │   ├── tag.py               # NEW: Tag model
│   │   ├── reminder.py          # NEW: Reminder model
│   │   ├── recurring_task.py    # NEW: Recurring task model
│   │   └── activity_log.py      # NEW: Activity log model
│   ├── services/
│   │   ├── task_service.py      # Extended with search/filter/sort
│   │   ├── tag_service.py       # NEW: Tag management
│   │   ├── reminder_service.py  # NEW: Reminder scheduling
│   │   ├── recurring_service.py # NEW: Recurring task logic
│   │   └── activity_service.py  # NEW: Activity logging
│   ├── api/
│   │   └── routes/
│   │       ├── tasks.py         # Extended with new query params
│   │       ├── tags.py          # NEW: Tag endpoints
│   │       └── reminders.py     # NEW: Reminder endpoints
│   ├── scheduler/
│   │   └── reminder_scheduler.py # NEW: APScheduler integration
│   └── migrations/
│       └── versions/
│           └── 002_advanced_features.py # NEW: Database migration
└── tests/
    ├── unit/
    │   ├── test_task_service.py
    │   ├── test_tag_service.py
    │   ├── test_reminder_service.py
    │   └── test_recurring_service.py
    └── integration/
        ├── test_search_filter.py
        ├── test_reminders.py
        └── test_recurring_tasks.py

frontend/
├── src/
│   ├── components/
│   │   ├── tasks/
│   │   │   ├── TaskForm.tsx         # Extended with new fields
│   │   │   ├── TaskCard.tsx         # Extended with priority/tags display
│   │   │   ├── PriorityBadge.tsx    # NEW: Priority indicator
│   │   │   ├── TagChips.tsx         # NEW: Tag display/management
│   │   │   ├── SearchBar.tsx        # NEW: Search input
│   │   │   ├── FilterPanel.tsx      # NEW: Filter sidebar
│   │   │   ├── SortDropdown.tsx     # NEW: Sort selector
│   │   │   ├── ReminderModal.tsx    # NEW: Reminder configuration
│   │   │   ├── RecurringModal.tsx   # NEW: Recurrence configuration
│   │   │   └── ActivityLog.tsx      # NEW: Activity timeline
│   │   └── ui/
│   │       └── (shadcn components)
│   ├── hooks/
│   │   ├── useTaskSearch.ts         # NEW: Search logic
│   │   ├── useTaskFilter.ts         # NEW: Filter logic
│   │   ├── useTaskSort.ts           # NEW: Sort logic
│   │   └── usePolling.ts            # NEW: Real-time polling
│   ├── services/
│   │   └── api.ts                   # Extended with new endpoints
│   └── types/
│       ├── task.ts                  # Extended with new fields
│       ├── tag.ts                   # NEW: Tag types
│       └── reminder.ts              # NEW: Reminder types
└── tests/
    ├── components/
    │   ├── TaskForm.test.tsx
    │   ├── SearchBar.test.tsx
    │   └── FilterPanel.test.tsx
    └── hooks/
        ├── useTaskSearch.test.ts
        └── useTaskFilter.test.ts
```

**Structure Decision**: Web application structure with separate backend (FastAPI) and frontend (Next.js) directories. This matches the existing repository layout and maintains clear separation of concerns. New features are additive - extending existing models/services/components rather than replacing them.

## Complexity Tracking

**Status**: No constitution violations detected. All new requirements are justified by functional requirements and maintain architectural principles.

- APScheduler addition: Required for FR-020 (reminder notifications)
- Database schema changes: Required for all advanced features (FR-014 through FR-026)
- Polling mechanism: Acceptable interim solution for Phase III-IV; WebSocket deferred to Phase V

No additional complexity justification needed.
