# Implementation Plan: Core Task CRUD Operations

**Branch**: `001-core-task-crud` | **Date**: 2025-12-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-core-task-crud/spec.md`

## Summary

Implement a console-based Todo List Manager application in Python that provides five core CRUD operations: add task, view all tasks, update task, delete task, and toggle task completion. The application uses in-memory storage only (no persistence), runs in a continuous menu loop, and handles all invalid inputs gracefully without crashing.

## Technical Context

**Language/Version**: Python 3.11+ (recommended 3.12+)
**Primary Dependencies**: None (standard library only per Constitution)
**Storage**: In-memory list of dictionaries
**Testing**: Manual testing via console interaction (no automated tests in Phase I)
**Target Platform**: Any system with Python 3.11+ and terminal access
**Project Type**: Single-file console application
**Performance Goals**: Handle 100+ tasks without noticeable degradation
**Constraints**: No file I/O, no databases, no third-party libraries, no GUI
**Scale/Scope**: Single-user, single-session, in-memory only

## Constitution Check

*GATE: All items must pass before implementation.*

| Principle | Status | Verification |
|-----------|--------|--------------|
| I. Spec-Driven Development | PASS | Implementation derived from spec.md |
| II. Technology Constraints | PASS | Python 3.11+, stdlib only, no persistence |
| III. Core Features Scope | PASS | Exactly 5 features (add, view, update, delete, toggle) |
| IV. Data Model | PASS | Task with id, title, description, completed |
| V. Console Interface | PASS | Menu-driven, graceful error handling |
| VI. Code Quality & Structure | PASS | Modular functions, PEP 8, extensible |

**Forbidden Practices Check**: No file I/O, no databases, no GUI, no network, no async, no third-party libraries.

## Application Flow

### Startup Sequence

1. Application entry point invoked
2. Initialize empty task storage (in-memory list)
3. Initialize ID counter starting at 1
4. Display welcome message: "Welcome to the Todo List Manager!"
5. Enter main menu loop

### Main Menu Loop

The application operates in a continuous loop until the user selects Exit:

1. Display main menu with 6 numbered options
2. Prompt user for choice (1-6)
3. Validate input is an integer between 1 and 6
4. If invalid: display error message and re-display menu
5. If valid: dispatch to corresponding feature handler
6. After feature completes (success or error): return to step 1
7. If Exit selected: display "Goodbye!" and terminate cleanly

### Feature Dispatch

Menu choice maps to feature handlers:
- Choice 1 → Add Task handler
- Choice 2 → View Tasks handler
- Choice 3 → Update Task handler
- Choice 4 → Delete Task handler
- Choice 5 → Toggle Completion handler
- Choice 6 → Exit application

## Core Modules and Functions

### Module Organization

For Phase I simplicity and Constitution compliance, a single-file structure is appropriate. The application will be organized into logical sections within one Python file:

1. **Global State Section**: Task storage list and ID counter
2. **Utility Functions Section**: Input validation helpers, task lookup
3. **Feature Functions Section**: One function per CRUD operation
4. **Menu Functions Section**: Menu display and input handling
5. **Main Entry Point**: Application initialization and loop control

### Function Inventory

**Utility Functions**:
- `get_task_by_id(task_id)`: Find and return a task by ID, or None if not found
- `get_valid_integer_input(prompt)`: Safely read integer input with error handling

**Feature Functions** (one per user story):
- `add_task()`: Handle User Story 1 - Add New Task
- `view_tasks()`: Handle User Story 2 - View All Tasks
- `update_task()`: Handle User Story 3 - Update Existing Task
- `delete_task()`: Handle User Story 4 - Delete Task
- `toggle_task_completion()`: Handle User Story 5 - Toggle Complete/Incomplete

**Menu Functions**:
- `display_menu()`: Print the main menu options
- `get_menu_choice()`: Get and validate user's menu selection
- `main()`: Entry point with initialization and main loop

## Data Structures

### Task Storage

Tasks are stored in a Python list containing dictionaries. Each dictionary represents one task with the following structure:

**Task Dictionary Keys**:
- `id` (int): Unique identifier, assigned sequentially, never reused
- `title` (str): Task title, required, non-empty after strip
- `description` (str): Task description, may be empty string
- `completed` (bool): Completion status, default False

**Storage Characteristics**:
- List maintains insertion order (Python 3.7+ guarantee)
- Lookup by ID requires iteration (acceptable for 100+ tasks)
- No indexing by ID position (IDs are stable, not sequential after deletions)

### ID Counter

A global integer counter tracks the next available task ID:
- Starts at 1
- Increments after each task creation
- Never decrements or resets (IDs are never reused)
- Survives task deletions (gaps in ID sequence are expected)

## Control Flow Details

### Add Task Flow

1. Display section header "--- Add New Task ---"
2. Prompt for title with message "Enter task title (required): "
3. Read input and strip whitespace
4. If empty after strip: display error, return to menu
5. Prompt for description with message "Enter task description (optional): "
6. Read input (empty is valid)
7. Create task dictionary with current counter value as ID
8. Increment ID counter
9. Append task to storage list
10. Display success message with assigned ID
11. Return to menu

### View Tasks Flow

1. Display section header "--- All Tasks ---"
2. If task list is empty: display "No tasks yet.", return to menu
3. For each task in list (insertion order):
   - Format status marker: "[✔]" if completed, "[ ]" if not
   - Display: "{status} {id}: {title}"
   - If description non-empty: display indented "     Description: {description}"
4. Return to menu

### Update Task Flow

1. Display section header "--- Update Task ---"
2. Prompt for task ID with message "Enter task ID to update: "
3. Attempt to parse as integer
4. If not integer: display "Error: Invalid input. Please enter a number.", return to menu
5. Look up task by ID
6. If not found: display "Error: No task found with ID {id}.", return to menu
7. Display current title: "Current title: {title}"
8. Display current description: "Current description: {description}"
9. Prompt for new title with message "Enter new title (leave blank to keep current): "
10. Read and strip input
11. If non-empty: update task title
12. Prompt for new description with message "Enter new description (leave blank to keep current): "
13. Read input (do not strip - allow clearing)
14. Update task description (even if empty - allows clearing)
15. Display "Task {id} updated successfully."
16. Return to menu

### Delete Task Flow

1. Display section header "--- Delete Task ---"
2. Prompt for task ID with message "Enter task ID to delete: "
3. Attempt to parse as integer
4. If not integer: display error, return to menu
5. Look up task by ID
6. If not found: display "Error: No task found with ID {id}.", return to menu
7. Remove task from list
8. Display "Task {id} deleted successfully."
9. Return to menu

### Toggle Completion Flow

1. Display section header "--- Mark Task Complete/Incomplete ---"
2. Prompt for task ID with message "Enter task ID: "
3. Attempt to parse as integer
4. If not integer: display error, return to menu
5. Look up task by ID
6. If not found: display "Error: No task found with ID {id}.", return to menu
7. Toggle completed boolean (True ↔ False)
8. If now True: display "Task {id} marked as complete."
9. If now False: display "Task {id} marked as incomplete."
10. Return to menu

## Error Handling Strategy

### Design Principle

All errors are handled gracefully with user-friendly messages. The application never crashes regardless of input.

### Input Validation Approach

**Integer Input Validation**:
- Use try/except around int() conversion
- On ValueError: display specific error message
- Return to menu without state changes

**Empty Input Handling**:
- Strip whitespace from all inputs
- For required fields (title): reject if empty after strip
- For optional fields (description): accept empty as valid

**Task Lookup Validation**:
- Always validate task exists before operations
- Display consistent "No task found with ID {id}." message
- Return to menu without state changes

### Error Message Consistency

All error messages follow the format "Error: {specific message}." to maintain consistency:
- "Error: Title cannot be empty."
- "Error: Invalid input. Please enter a number."
- "Error: No task found with ID {id}."
- "Invalid choice. Please enter a number from 1 to 6."

### Recovery Strategy

After any error:
1. Display appropriate error message
2. Make no changes to application state
3. Return immediately to main menu
4. Allow user to retry or choose different action

## Project Structure

### Source Code Layout

```text
todo.py              # Single-file application (all code)
```

### Documentation Layout

```text
specs/001-core-task-crud/
├── spec.md          # Feature specification (complete)
├── plan.md          # This implementation plan
├── tasks.md         # Task breakdown (to be generated)
└── checklists/
    └── requirements.md  # Quality checklist
```

**Structure Decision**: Single-file architecture chosen for Phase I simplicity. The Constitution's modularity requirement is satisfied through well-organized functions within the single file. Future phases may refactor into multiple modules if complexity warrants.

## Complexity Tracking

No Constitution violations or complexity justifications required. The implementation follows the simplest viable approach:

- Single file (no module complexity)
- List storage (no data structure complexity)
- Direct functions (no class hierarchy)
- Synchronous execution (no async complexity)
- Standard library only (no dependency complexity)
