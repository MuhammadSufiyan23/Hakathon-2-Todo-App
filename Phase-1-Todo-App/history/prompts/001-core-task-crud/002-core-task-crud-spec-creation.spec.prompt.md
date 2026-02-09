---
id: 002
title: Core Task CRUD Specification Creation
stage: spec
date: 2025-12-29
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-core-task-crud
branch: 001-core-task-crud
user: king
command: /sp.specify
labels: ["spec", "crud", "todo-app", "phase-1", "python"]
links:
  spec: specs/001-core-task-crud/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-core-task-crud/spec.md
  - specs/001-core-task-crud/checklists/requirements.md
tests:
  - none
---

## Prompt

# Feature Specification: Core Task CRUD Operations
## Phase I – In-Memory Python Console Todo Application

This document specifies the five core features required by the Constitution for Phase I.
All behaviour must strictly conform to this specification and the Constitution.

---

### 1. Add Task

#### User Story
As a user, I want to add a new task with a title and an optional description so that I can record something I need to do.

#### Inputs
- Task title (required, non-empty string)
- Task description (optional, may be empty string)

#### Outputs
- Success message confirming the task has been added, including the assigned task ID
- On failure, a clear error message

#### Acceptance Criteria
- User is prompted for a title.
- If title is empty (after stripping whitespace), display error "Title cannot be empty" and abort the operation (do not add task).
- User is then prompted for a description (explicitly stated as optional).
- A new task is created with:
  - Unique sequential integer ID (starting from 1, stable within session)
  - Provided title
  - Provided description (empty string if none entered)
  - Completion status set to incomplete (False)
- Task is appended to the in-memory task list.
- Success message displayed: e.g., "Task {id} added successfully."

#### Edge Cases & Error Conditions
- Empty title → operation aborted, no task added
- User presses Enter without input for description → description stored as empty string
- No crash on very long input strings (handled gracefully by Python input)

---

### 2. View Tasks

#### User Story
As a user, I want to see all my tasks so that I can review what needs to be done.

#### Inputs
- None (triggered directly from menu)

#### Outputs
- Formatted list of all current tasks
- Message if no tasks exist

#### Acceptance Criteria
- Displays a clear header (e.g., "--- All Tasks ---")
- If no tasks exist, displays "No tasks yet."
- For each task, displays on one or more lines:
  - Completion status marker: `[✔]` if completed, `[ ]` if incomplete
  - Task ID
  - Task title
  - If description is non-empty, display it indented on the following line (e.g., "     Description: ...")
- Tasks displayed in the order they were added (insertion order).

#### Edge Cases & Error Conditions
- Empty task list → friendly message shown
- Tasks with empty descriptions → no description line shown
- Very long titles/descriptions → displayed as-is (no truncation required in Phase I)

---

### 3. Update Task

#### User Story
As a user, I want to modify the title and/or description of an existing task so that I can correct or refine it.

#### Inputs
- Task ID to update
- New title (optional – blank means keep existing)
- New description (optional – blank means replace with empty string)

#### Outputs
- Success message with updated task ID
- Error message if task not found or invalid ID

#### Acceptance Criteria
- User is prompted for task ID.
- If ID is invalid (non-integer or not found), display appropriate error and abort.
- Current title and description are shown for reference.
- User is prompted for new title (instruction: "leave blank to keep current").
- User is prompted for new description (instruction: "leave blank to keep current").
- If new title provided (non-blank after strip), replace title.
- If new title blank, title remains unchanged.
- If new description provided (including empty input), replace description (allows clearing).
- Success message: e.g., "Task {id} updated successfully."

#### Edge Cases & Error Conditions
- Non-existent task ID → "No task found with ID X"
- Invalid ID input (non-integer) → "Invalid input. Please enter a number."
- User enters blank for both → task remains completely unchanged, but success message still shown
- User clears description → description becomes empty string

---

### 4. Delete Task

#### User Story
As a user, I want to permanently remove a task that is no longer needed.

#### Inputs
- Task ID to delete

#### Outputs
- Success message with deleted task ID
- Error message if task not found or invalid ID

#### Acceptance Criteria
- User is prompted for task ID.
- If ID is invalid or task not found, display error and abort.
- Task is removed from the in-memory list.
- Task IDs of remaining tasks remain unchanged (stability requirement).
- Success message: e.g., "Task {id} deleted successfully."

#### Edge Cases & Error Conditions
- Non-existent task ID → clear error message
- Invalid ID input → clear error message
- Deleting the last task → list becomes empty
- Deleting a task does not renumber existing task IDs

---

### 5. Mark Task Complete / Incomplete

#### User Story
As a user, I want to toggle a task's completion status so that I can track progress.

#### Inputs
- Task ID to mark

#### Outputs
- Success message indicating new status and task ID
- Error message if task not found or invalid ID

#### Acceptance Criteria
- User is prompted for task ID.
- If ID is invalid or task not found, display error and abort.
- Task's completed status is toggled:
  - Incomplete → Complete
  - Complete → Incomplete
- Success message reflects new status: e.g., "Task {id} marked as complete." or "Task {id} marked as incomplete."

#### Edge Cases & Error Conditions
- Non-existent task ID → clear error message
- Invalid ID input → clear error message
- Toggling twice returns to original state

---

### General Requirements (Apply to All Features)
- After successful or failed operation, control returns to the main menu.
- All user-facing messages are concise, clear, and friendly.
- Application never crashes on invalid input.
- No persistence – all tasks lost on exit.
- Implementation must use only standard Python library.

This specification is complete and authoritative for Phase I core CRUD features.

## Response snapshot

Created feature specification for Core Task CRUD Operations:
- Branch: `001-core-task-crud`
- Spec file: `specs/001-core-task-crud/spec.md`
- 5 user stories covering Add, View, Update, Delete, Toggle operations
- 16 functional requirements (FR-001 through FR-016)
- 9 measurable success criteria
- Quality checklist passed all 16 validation items
- No [NEEDS CLARIFICATION] markers - spec is complete and ready for planning

## Outcome

- Impact: Complete feature specification created for Phase I Todo App core CRUD features
- Tests: N/A - specification document
- Files: specs/001-core-task-crud/spec.md, specs/001-core-task-crud/checklists/requirements.md
- Next prompts: /sp.plan to create implementation plan
- Reflection: User-provided spec was comprehensive; transformed into structured template format with all acceptance scenarios

## Evaluation notes (flywheel)

- Failure modes observed: None - user provided detailed specification
- Graders run and results (PASS/FAIL): Quality checklist PASS (16/16)
- Prompt variant (if applicable): user-provided-detailed-spec
- Next experiment: Verify spec-to-plan transformation maintains all requirements
