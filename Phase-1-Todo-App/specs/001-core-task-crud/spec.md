# Feature Specification: Core Task CRUD Operations (Refined & Clarified)

**Feature Branch**: `001-core-task-crud`
**Created**: 2025-12-29
**Status**: Ready for Planning
**Input**: User description: "Core Task CRUD Operations for Phase I In-Memory Python Console Todo Application"

This refined specification removes ambiguities, makes implicit assumptions explicit, ensures comprehensive edge case coverage, and fully complies with the Constitution.

All behaviour must strictly conform to this specification and the Constitution.
No additional features or behaviours are permitted.

## Clarifications

### Session 2025-12-29

- Q: What are the exact UI prompts and messages? → A: User provided complete specification with all exact prompts, headers, error messages, and success messages defined explicitly.
- Q: What is the main menu structure? → A: 6 options (Add, View, Update, Delete, Toggle, Exit) with exact text and numbering.
- Q: How should description updates be handled? → A: Blank input keeps current; empty input (pressing Enter) clears description.

## Global Rules (Apply to All Features)

- The application uses only in-memory storage (list of dictionaries recommended).
- Task IDs are unique positive integers, assigned sequentially starting from 1, and remain stable for the entire session (never reused or renumbered).
- All user input is read via `input()` and stripped of leading/trailing whitespace.
- After any operation (success or failure), the application must return to the main menu without crashing.
- All error messages must be clear, concise, and user-friendly.
- The application must never crash on any user input.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add New Task (Priority: P1)

As a user, I want to add a new task with a title and an optional description so that I can record something I need to do.

**Why this priority**: Adding tasks is the foundational feature - without the ability to create tasks, no other features have value. This must work first for any MVP.

**Independent Test**: Can be fully tested by launching the app, selecting "Add Task" from the menu, entering a title and optionally a description, and verifying the success message displays the assigned task ID.

#### Inputs
- Task title: string (required, must be non-empty after stripping whitespace)
- Task description: string (optional, empty string allowed)

#### Outputs
- Success: "Task {id} added successfully."
- Failure: Clear error message

#### Acceptance Criteria
- Display section header: "--- Add New Task ---"
- Prompt: "Enter task title (required): "
- If title is empty after stripping, display "Error: Title cannot be empty." and abort (no task added).
- Prompt: "Enter task description (optional): "
- Empty input for description is accepted and stored as empty string.
- New task is created with:
  - `id`: next sequential integer (global counter incremented after assignment)
  - `title`: provided title
  - `description`: provided description (empty string if none)
  - `completed`: False
- Task appended to in-memory list (preserves insertion order).
- Display success message with the assigned ID.

#### Edge Cases & Error Conditions
- Title consisting only of whitespace → treated as empty, operation aborted
- Very long title/description → accepted as-is (no truncation or validation of length)
- User cancels input (Ctrl+C/Ctrl+D) → not required to handle in Phase I (Python default behaviour acceptable)

---

### User Story 2 - View All Tasks (Priority: P1)

As a user, I want to see a clear list of all my tasks so that I can review what needs to be done.

**Why this priority**: Viewing tasks is equally critical to adding - users must be able to see their tasks to use the application meaningfully. Co-priority with Add Task.

**Independent Test**: Can be fully tested by adding several tasks via User Story 1, then selecting "View Tasks" and verifying all tasks display with correct format, status markers, and insertion order.

#### Inputs
- None

#### Outputs
- Formatted list of all tasks or empty state message

#### Acceptance Criteria
- Display section header: "--- All Tasks ---"
- If no tasks exist, display exactly: "No tasks yet."
- For each task (in insertion order):
  - Line 1: `{status} {id}: {title}`
    - Where `{status}` is "[✔]" if completed, "[ ]" if incomplete
  - If description is non-empty, Line 2 (indented): "     Description: {description}"
- No extra blank lines between tasks unless needed for readability.

#### Edge Cases & Error Conditions
- Zero tasks → "No tasks yet." message
- Task with empty description → no description line displayed
- Task with very long title or description → displayed in full (no truncation)
- Completed and incomplete tasks mixed → displayed in insertion order, not sorted

---

### User Story 3 - Update Existing Task (Priority: P2)

As a user, I want to modify the title and/or description of an existing task so that I can correct or refine it.

**Why this priority**: Updating is important but secondary - users can work with add/view/delete and toggle before needing to edit. Allows correction of mistakes.

**Independent Test**: Can be fully tested by adding a task, selecting "Update Task", entering the task ID, modifying title and/or description, and verifying changes persist when viewing all tasks.

#### Inputs
- Task ID (integer)
- New title (optional – blank keeps existing)
- New description (optional – blank keeps existing; empty input clears)

#### Outputs
- Success or error message

#### Acceptance Criteria
- Display section header: "--- Update Task ---"
- Prompt: "Enter task ID to update: "
- If input is not integer → "Error: Invalid input. Please enter a number."
- If task not found → "Error: No task found with ID {id}."
- On valid task:
  - Show current values:
    - "Current title: {title}"
    - "Current description: {description}" (empty string shown as blank)
  - Prompt: "Enter new title (leave blank to keep current): "
  - Prompt: "Enter new description (leave blank to keep current): "
- Rules for updates:
  - New title non-blank after strip → replace title
  - New title blank → title unchanged
  - New description provided (including empty input) → replace description (allows clearing)
  - New description blank only if user presses Enter without input → description unchanged
- Display: "Task {id} updated successfully." (even if no fields changed)

#### Edge Cases & Error Conditions
- Non-integer ID input → error, abort
- Non-existent ID → error, abort
- User leaves both fields blank → task unchanged, but success message still shown
- User enters only whitespace for title → treated as blank (title unchanged)
- User enters empty description to clear it → description becomes ""

---

### User Story 4 - Delete Task (Priority: P2)

As a user, I want to permanently remove a task that is no longer needed.

**Why this priority**: Deletion is important for task management but secondary to core add/view functionality. Users need this to clean up their task list.

**Independent Test**: Can be fully tested by adding tasks, selecting "Delete Task", entering a valid ID, verifying success message, and confirming task no longer appears in view.

#### Inputs
- Task ID (integer)

#### Outputs
- Success or error message

#### Acceptance Criteria
- Display section header: "--- Delete Task ---"
- Prompt: "Enter task ID to delete: "
- If input not integer → "Error: Invalid input. Please enter a number."
- If task not found → "Error: No task found with ID {id}."
- On valid task: remove from in-memory list
- Task IDs of remaining tasks must not change
- Display: "Task {id} deleted successfully."

#### Edge Cases & Error Conditions
- Deleting last task → list becomes empty
- Deleting task in middle → order of remaining tasks preserved, IDs unchanged
- Non-integer or non-existent ID → error, no change to list

---

### User Story 5 - Toggle Task Completion (Priority: P2)

As a user, I want to toggle a task's completion status so that I can track progress.

**Why this priority**: Toggling completion is essential for task tracking but comes after the ability to create, view, and manage tasks.

**Independent Test**: Can be fully tested by adding an incomplete task, toggling it to complete, verifying the checkmark appears in view, toggling again, and verifying it reverts to incomplete.

#### Inputs
- Task ID (integer)

#### Outputs
- Success message indicating new status

#### Acceptance Criteria
- Display section header: "--- Mark Task Complete/Incomplete ---"
- Prompt: "Enter task ID: "
- If input not integer → "Error: Invalid input. Please enter a number."
- If task not found → "Error: No task found with ID {id}."
- On valid task: toggle `completed` boolean
  - False → True: "Task {id} marked as complete."
  - True → False: "Task {id} marked as incomplete."

#### Edge Cases & Error Conditions
- Toggling same task twice → returns to original state
- Non-integer or non-existent ID → error, status unchanged

---

### Edge Cases Summary

- Empty task list: "View Tasks" shows friendly "No tasks yet." message
- Empty title on add: Operation aborted with "Error: Title cannot be empty."
- Empty description on add: Stored as empty string (valid)
- Non-existent task ID: Clear error message, no crash
- Non-integer ID input: "Error: Invalid input. Please enter a number."
- Very long titles/descriptions: Handled gracefully (no truncation in Phase I)
- Deleting tasks does not renumber remaining task IDs (stability requirement)
- Update with both fields blank: Task unchanged, success message shown
- Clearing description via update: Providing empty input replaces description with empty string

## Main Menu & Program Flow

- Application starts with welcome message: "Welcome to the Todo List Manager!"
- Main menu displayed with exactly these options:
  1. Add task
  2. View all tasks
  3. Update task
  4. Delete task
  5. Mark task complete/incomplete
  6. Exit
- Prompt: "Enter your choice (1-6): "
- Invalid choice → "Invalid choice. Please enter a number from 1 to 6."
- Option 6 → "Goodbye!" and clean exit
- All other options → execute feature, then return to main menu

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to add a new task with a required title and optional description
- **FR-002**: System MUST reject tasks with empty titles (whitespace-only counts as empty) with message "Error: Title cannot be empty."
- **FR-003**: System MUST assign each task a unique sequential integer ID starting from 1
- **FR-004**: System MUST display all tasks in insertion order with completion status markers (`[✔]` or `[ ]`)
- **FR-005**: System MUST display "No tasks yet." when no tasks exist
- **FR-006**: System MUST allow users to update a task's title and/or description by ID
- **FR-007**: System MUST show current task values before prompting for updates
- **FR-008**: System MUST allow users to delete a task by ID
- **FR-009**: System MUST preserve existing task IDs when other tasks are deleted (no renumbering)
- **FR-010**: System MUST allow users to toggle a task's completion status by ID
- **FR-011**: System MUST display "Error: No task found with ID {id}." for invalid task IDs
- **FR-012**: System MUST display "Error: Invalid input. Please enter a number." for non-integer ID inputs
- **FR-013**: System MUST return to main menu after every operation (success or failure)
- **FR-014**: System MUST never crash on any user input
- **FR-015**: System MUST use only Python standard library (no third-party dependencies)
- **FR-016**: System MUST store all tasks in-memory only (no persistence between sessions)
- **FR-017**: System MUST display section headers before each operation (e.g., "--- Add New Task ---")
- **FR-018**: System MUST display welcome message "Welcome to the Todo List Manager!" on startup
- **FR-019**: System MUST display "Goodbye!" on exit
- **FR-020**: System MUST display "Invalid choice. Please enter a number from 1 to 6." for invalid menu selections

### Key Entities

- **Task**: Represents a single to-do item with the following attributes:
  - **id**: Unique positive integer identifier (assigned sequentially starting from 1, never reused or renumbered)
  - **title**: Required non-empty string describing the task (whitespace-stripped)
  - **description**: Optional string providing additional details (may be empty string)
  - **completed**: Boolean flag indicating completion status (default: False)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can add a new task in under 30 seconds (title + optional description)
- **SC-002**: Users can view all tasks and understand their status at a glance
- **SC-003**: Users can update any task in under 30 seconds
- **SC-004**: Users can delete any task in under 15 seconds
- **SC-005**: Users can toggle task completion in under 10 seconds
- **SC-006**: Application handles 100+ tasks without noticeable performance degradation
- **SC-007**: 100% of invalid inputs result in friendly error messages (no crashes)
- **SC-008**: 100% of operations return user to main menu for next action
- **SC-009**: All 5 core features are fully functional and match this specification
- **SC-010**: All prompts and messages match the exact text specified in this document

## Assumptions

- Users interact via console/terminal with keyboard input
- Single-user application (no concurrent access considerations)
- Task IDs start at 1 and increment by 1 for each new task
- Whitespace-only input for title is treated as empty (invalid)
- Default completion status is incomplete (False)
- No undo/redo functionality required in Phase I
- No search or filter functionality required in Phase I
- No task priority or due date fields required in Phase I
- User cancellation (Ctrl+C/Ctrl+D) may use Python default behaviour

## Out of Scope (Phase I)

- File persistence or database storage
- Multiple user support
- Task categories or tags
- Due dates or priorities
- Search and filter functionality
- Undo/redo operations
- GUI or web interface
- Network features
- Graceful handling of Ctrl+C/Ctrl+D (Python default acceptable)
