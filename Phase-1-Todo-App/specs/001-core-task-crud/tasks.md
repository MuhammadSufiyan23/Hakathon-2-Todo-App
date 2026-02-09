# Tasks: Core Task CRUD Operations

**Input**: Design documents from `/specs/001-core-task-crud/`
**Prerequisites**: plan.md (complete), spec.md (complete)

**Tests**: No automated tests requested for Phase I. Manual testing via console interaction.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single-file project**: `todo.py` at repository root
- All implementation in single file per plan.md structure decision

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create the application file and establish global state

- [x] T001 Create todo.py file at repository root with module docstring and Python 3.11+ shebang
- [x] T002 Define global task storage list (empty list) in todo.py
- [x] T003 Define global ID counter (starting at 1) in todo.py

**Checkpoint**: Empty application shell ready for feature implementation

---

## Phase 2: Foundational (Core Infrastructure)

**Purpose**: Implement shared utilities and main loop structure that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Implement `get_task_by_id(task_id)` utility function in todo.py - returns task dict or None
- [x] T005 Implement `get_valid_integer_input(prompt)` utility function in todo.py - returns int or None with error handling
- [x] T006 Implement `display_menu()` function in todo.py - prints exact 6-option menu from spec
- [x] T007 Implement `get_menu_choice()` function in todo.py - validates input 1-6, displays error for invalid
- [x] T008 Implement `main()` entry point in todo.py - welcome message, main loop, exit handling
- [x] T009 Add `if __name__ == "__main__": main()` guard in todo.py

**Checkpoint**: Application runs, displays menu, handles invalid choices, exits cleanly. No features yet.

---

## Phase 3: User Story 1 - Add New Task (Priority: P1)

**Goal**: Users can create new tasks with title and optional description

**Independent Test**: Run app → Select option 1 → Enter title → Enter description → Verify success message with ID

### Implementation for User Story 1

- [x] T010 [US1] Implement `add_task()` function in todo.py with section header "--- Add New Task ---"
- [x] T011 [US1] Add title prompt and empty title validation in `add_task()` function in todo.py
- [x] T012 [US1] Add description prompt (optional) in `add_task()` function in todo.py
- [x] T013 [US1] Add task creation logic with ID assignment and counter increment in `add_task()` function in todo.py
- [x] T014 [US1] Add success message display in `add_task()` function in todo.py
- [x] T015 [US1] Wire `add_task()` to menu choice 1 in `main()` function in todo.py

**Checkpoint**: User Story 1 complete - can add tasks with titles and descriptions

---

## Phase 4: User Story 2 - View All Tasks (Priority: P1)

**Goal**: Users can see all tasks with completion status and details

**Independent Test**: Add tasks via US1 → Select option 2 → Verify all tasks display in correct format

### Implementation for User Story 2

- [x] T016 [US2] Implement `view_tasks()` function in todo.py with section header "--- All Tasks ---"
- [x] T017 [US2] Add empty list check with "No tasks yet." message in `view_tasks()` function in todo.py
- [x] T018 [US2] Add task iteration with status marker formatting ([✔]/[ ]) in `view_tasks()` function in todo.py
- [x] T019 [US2] Add conditional description display (indented) in `view_tasks()` function in todo.py
- [x] T020 [US2] Wire `view_tasks()` to menu choice 2 in `main()` function in todo.py

**Checkpoint**: User Stories 1 AND 2 complete - can add and view tasks (MVP functional)

---

## Phase 5: User Story 3 - Update Existing Task (Priority: P2)

**Goal**: Users can modify task titles and descriptions

**Independent Test**: Add task → Select option 3 → Enter ID → Modify fields → View to verify changes

### Implementation for User Story 3

- [x] T021 [US3] Implement `update_task()` function in todo.py with section header "--- Update Task ---"
- [x] T022 [US3] Add task ID prompt with integer validation in `update_task()` function in todo.py
- [x] T023 [US3] Add task lookup with "No task found" error handling in `update_task()` function in todo.py
- [x] T024 [US3] Add current values display in `update_task()` function in todo.py
- [x] T025 [US3] Add new title prompt with blank-keeps-current logic in `update_task()` function in todo.py
- [x] T026 [US3] Add new description prompt with update logic in `update_task()` function in todo.py
- [x] T027 [US3] Add success message display in `update_task()` function in todo.py
- [x] T028 [US3] Wire `update_task()` to menu choice 3 in `main()` function in todo.py

**Checkpoint**: User Story 3 complete - can update existing tasks

---

## Phase 6: User Story 4 - Delete Task (Priority: P2)

**Goal**: Users can permanently remove tasks

**Independent Test**: Add tasks → Select option 4 → Enter ID → View to confirm deletion

### Implementation for User Story 4

- [x] T029 [US4] Implement `delete_task()` function in todo.py with section header "--- Delete Task ---"
- [x] T030 [US4] Add task ID prompt with integer validation in `delete_task()` function in todo.py
- [x] T031 [US4] Add task lookup with "No task found" error handling in `delete_task()` function in todo.py
- [x] T032 [US4] Add task removal from list in `delete_task()` function in todo.py
- [x] T033 [US4] Add success message display in `delete_task()` function in todo.py
- [x] T034 [US4] Wire `delete_task()` to menu choice 4 in `main()` function in todo.py

**Checkpoint**: User Story 4 complete - can delete tasks

---

## Phase 7: User Story 5 - Toggle Task Completion (Priority: P2)

**Goal**: Users can mark tasks complete or incomplete

**Independent Test**: Add task → Select option 5 → Enter ID → View to see checkmark → Toggle again → Verify reverted

### Implementation for User Story 5

- [x] T035 [US5] Implement `toggle_task_completion()` function in todo.py with section header "--- Mark Task Complete/Incomplete ---"
- [x] T036 [US5] Add task ID prompt with integer validation in `toggle_task_completion()` function in todo.py
- [x] T037 [US5] Add task lookup with "No task found" error handling in `toggle_task_completion()` function in todo.py
- [x] T038 [US5] Add completion status toggle logic in `toggle_task_completion()` function in todo.py
- [x] T039 [US5] Add conditional success message (complete/incomplete) in `toggle_task_completion()` function in todo.py
- [x] T040 [US5] Wire `toggle_task_completion()` to menu choice 5 in `main()` function in todo.py

**Checkpoint**: All 5 user stories complete - full CRUD functionality implemented

---

## Phase 8: Polish & Validation

**Purpose**: Final cleanup and verification against specification

- [x] T041 Verify all prompts match exact spec text in todo.py
- [x] T042 Verify all error messages match exact spec text in todo.py
- [x] T043 Verify all success messages match exact spec text in todo.py
- [x] T044 Test empty title edge case (whitespace only) in todo.py
- [x] T045 Test invalid menu choice handling in todo.py
- [x] T046 Test non-integer ID input handling in todo.py
- [x] T047 Test non-existent task ID handling in todo.py
- [x] T048 Verify PEP 8 compliance in todo.py
- [x] T049 Manual end-to-end test of all 5 features in sequence

**Checkpoint**: Application complete and validated against specification

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational
- **User Story 2 (Phase 4)**: Depends on Foundational (can parallel with US1)
- **User Stories 3-5 (Phases 5-7)**: Depend on Foundational (can parallel with each other)
- **Polish (Phase 8)**: Depends on ALL user stories complete

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|------------|-------------------|
| US1 (Add) | Foundational | US2 |
| US2 (View) | Foundational | US1 |
| US3 (Update) | Foundational | US4, US5 |
| US4 (Delete) | Foundational | US3, US5 |
| US5 (Toggle) | Foundational | US3, US4 |

### Within Each User Story

Since all code is in a single file (todo.py), tasks within each story must be sequential:
1. Implement core function logic
2. Add validation and error handling
3. Wire to menu
4. Test independently

---

## Implementation Strategy

### MVP First (Recommended)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T009)
3. Complete Phase 3: User Story 1 - Add Task (T010-T015)
4. Complete Phase 4: User Story 2 - View Tasks (T016-T020)
5. **STOP and VALIDATE**: Can add and view tasks - this is MVP!
6. Continue with remaining user stories

### Full Implementation

1. Setup → Foundational → US1 → US2 → US3 → US4 → US5 → Polish
2. Total: 49 tasks
3. Estimated completion: Sequential execution through all phases

---

## Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| Setup | 3 | Project initialization |
| Foundational | 6 | Core infrastructure |
| US1 (P1) | 6 | Add Task |
| US2 (P1) | 5 | View Tasks |
| US3 (P2) | 8 | Update Task |
| US4 (P2) | 6 | Delete Task |
| US5 (P2) | 6 | Toggle Completion |
| Polish | 9 | Validation |
| **Total** | **49** | |

### Task Distribution by User Story

- US1: 6 tasks (T010-T015)
- US2: 5 tasks (T016-T020)
- US3: 8 tasks (T021-T028)
- US4: 6 tasks (T029-T034)
- US5: 6 tasks (T035-T040)

### MVP Scope

Complete through Phase 4 (T001-T020 = 20 tasks) for minimum viable product with Add and View functionality.

---

## Notes

- All tasks target single file: `todo.py`
- No parallel [P] markers used since all work is in same file
- [Story] labels track which user story each task belongs to
- Each user story is independently testable after implementation
- Commit after each phase or logical task group
- Manual testing only - no automated tests in Phase I
