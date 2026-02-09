<!--
Sync Impact Report
==================
- Version change: 0.0.0 → 1.0.0 (initial ratification)
- Added principles:
  - I. Spec-Driven Development
  - II. Technology Constraints
  - III. Core Features Scope
  - IV. Data Model
  - V. Console Interface
  - VI. Code Quality & Structure
- Added sections:
  - Forbidden Practices
  - Success Criteria
- Templates verified: ✅ No constitution-specific updates required (generic templates)
- Follow-up TODOs: None
-->

# Phase I – In-Memory Python Todo Console App Constitution

## Core Principles

### I. Spec-Driven Development

Code MUST be derived from clear written specifications. Spec-Driven Development is the
primary method for this project.

- Features start as written specifications before any code is written.
- Minor manual adjustments are permitted for bug fixes and testing (practical flexibility).
- If implementation deviates from specification, the specification MUST be refined to
  reflect the actual behavior or the implementation MUST be corrected.

### II. Technology Constraints

All technology choices are strictly constrained to ensure simplicity and portability.

- **Language**: Python 3.11+ (recommended 3.12+)
- **Environment**: Console/Terminal only
- **Storage**: In-memory only (no files, no database, no persistence)
- **External services**: Prohibited
- **Third-party libraries**: Prohibited (standard library only)

### III. Core Features Scope

Phase I implements exactly five (5) core features. No additional features are permitted.

1. **Add task**: Create a new task with title and optional description
2. **View all tasks**: Display all tasks with their completion status
3. **Update task**: Modify an existing task's title or description
4. **Delete task**: Remove a task from the system
5. **Mark task complete/incomplete**: Toggle a task's completion status

### IV. Data Model

Each task MUST contain the following attributes:

- **ID**: Unique, stable integer identifier (MUST NOT change after creation)
- **Title**: Required string (cannot be empty)
- **Description**: Optional string (may be empty or None)
- **Completed**: Boolean status (default: False)

Storage: In-memory list or dictionary structure.

### V. Console Interface

The user interface MUST be text-based and menu-driven.

- Clear main menu with numbered options for all features
- Loop back to main menu after every action completes
- Graceful handling of all invalid inputs (never crash)
- Clear, user-friendly error messages
- Task display format: `[✔]/[ ] ID: Title` with description on next line if present
- Welcome message displayed at application start
- Continuous loop until user explicitly selects "Exit"
- Clean exit with confirmation message

### VI. Code Quality & Structure

Code MUST be modular, readable, and extensible.

- **Modularity**: Separate functions for each feature (add, view, update, delete, toggle)
- **Naming**: Readable, meaningful variable and function names
- **Nesting**: Avoid deep nesting; prefer early returns
- **Style**: Follow PEP 8 guidelines
- **Extensibility**: Designed to easily add features in future phases without core changes

## Forbidden Practices

The following are explicitly PROHIBITED in Phase I:

| Category | Prohibited Items |
|----------|------------------|
| Storage | File I/O, databases, any persistence mechanism |
| UI | GUI frameworks, web frameworks |
| Network | Network calls, HTTP requests, sockets |
| Concurrency | Async/await, threads, multiprocessing |
| Dependencies | Any external/third-party libraries |

Violation of any forbidden practice invalidates the implementation.

## Success Criteria

Phase I is considered complete when ALL of the following are satisfied:

- [ ] All 5 core features work correctly as specified
- [ ] Application NEVER crashes on invalid input (graceful error handling)
- [ ] Behavior matches specifications exactly (no undocumented features)
- [ ] Codebase is clean, modular, and extensible for future phases
- [ ] All code follows PEP 8 style guidelines
- [ ] No forbidden practices are present in the codebase

## Governance

This constitution has **supreme authority** for Phase I development. Any conflicting
feature specification, plan, or task MUST align with this document.

**Amendment Procedure**:
1. Proposed changes MUST be documented with rationale
2. Changes require explicit approval before implementation
3. All amendments MUST include a migration plan for existing code
4. Version number MUST be updated according to semantic versioning

**Versioning Policy**:
- MAJOR: Backward-incompatible governance changes or principle removal
- MINOR: New principle added or existing principle materially expanded
- PATCH: Clarifications, wording improvements, non-semantic refinements

**Compliance Review**:
- All code reviews MUST verify compliance with this constitution
- Any complexity beyond minimal viable solution MUST be justified
- Constitution violations block merge approval

**Version**: 1.0.0 | **Ratified**: 2025-12-29 | **Last Amended**: 2025-12-29
