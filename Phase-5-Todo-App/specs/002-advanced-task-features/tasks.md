# Tasks: Advanced Task Management Features

**Input**: Design documents from `/specs/002-advanced-task-features/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

**Tests**: Tests are NOT explicitly requested in the specification, so test tasks are omitted per template guidelines.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/` for application code
- **Frontend**: `frontend/src/` for application code
- Paths follow the web application structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [ ] T001 Install APScheduler dependency in backend/requirements.txt (version 3.10.4)
- [ ] T002 Install python-dateutil dependency in backend/requirements.txt (version 2.8.2)
- [ ] T003 [P] Verify frontend dependencies (no new packages needed for Phase III-IV)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Schema

- [ ] T004 Create database migration script in backend/app/migrations/versions/002_advanced_features.py
- [ ] T005 Add new columns to tasks table (priority, due_date, is_recurring, recurrence_rule, completed_at, created_at, updated_at)
- [ ] T006 [P] Create tags table with schema from data-model.md
- [ ] T007 [P] Create task_tags junction table with foreign keys
- [ ] T008 [P] Create reminders table with schema from data-model.md
- [ ] T009 [P] Create activity_logs table with schema from data-model.md
- [ ] T010 Add database indexes per data-model.md (idx_tasks_user_priority, idx_tasks_user_due_date, etc.)
- [ ] T011 Run database migration and verify schema changes

### Base Models

- [ ] T012 [P] Create PriorityLevel enum in backend/app/models/task.py
- [ ] T013 [P] Create RecurrenceRule enum in backend/app/models/task.py
- [ ] T014 Extend Task model with new fields (priority, due_date, is_recurring, recurrence_rule, completed_at, created_at, updated_at) in backend/app/models/task.py
- [ ] T015 [P] Create Tag model in backend/app/models/tag.py
- [ ] T016 [P] Create TaskTag model in backend/app/models/task_tag.py
- [ ] T017 [P] Create ReminderStatus enum in backend/app/models/reminder.py
- [ ] T018 [P] Create Reminder model in backend/app/models/reminder.py
- [ ] T019 [P] Create ActivityAction enum in backend/app/models/activity_log.py
- [ ] T020 [P] Create ActivityLog model in backend/app/models/activity_log.py

### APScheduler Setup

- [ ] T021 Create scheduler module in backend/app/scheduler/reminder_scheduler.py
- [ ] T022 Implement start_scheduler() function with AsyncIOScheduler
- [ ] T023 Implement stop_scheduler() function
- [ ] T024 Implement check_reminders() async function (placeholder for now)
- [ ] T025 Update backend/main.py with lifespan context manager to start/stop scheduler

### Base Services

- [ ] T026 [P] Create ActivityService in backend/app/services/activity_service.py with log_activity() method
- [ ] T027 Update existing TaskService in backend/app/services/task_service.py to import ActivityService

### Frontend Types

- [ ] T028 [P] Extend Task interface in frontend/src/types/task.ts with new fields (priority, due_date, is_recurring, recurrence_rule, completed_at, created_at, updated_at, tags)
- [ ] T029 [P] Create PriorityLevel type in frontend/src/types/task.ts
- [ ] T030 [P] Create RecurrenceRule type in frontend/src/types/task.ts
- [ ] T031 [P] Create Tag interface in frontend/src/types/tag.ts
- [ ] T032 [P] Create Reminder interface in frontend/src/types/reminder.ts
- [ ] T033 [P] Create ActivityLog interface in frontend/src/types/activity.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Task Priority Management (Priority: P1) 🎯 MVP

**Goal**: Users can assign priority levels (low, medium, high) to tasks and visually distinguish them through color coding

**Independent Test**: Create tasks with different priority levels, filter by priority, and verify visual color coding (red for high, yellow for medium, green for low)

### Backend Implementation for US1

- [ ] T034 [P] [US1] Add priority field validation in backend/app/schemas/task.py (TaskCreate, TaskUpdate schemas)
- [ ] T035 [US1] Update create_task() method in backend/app/services/task_service.py to handle priority field
- [ ] T036 [US1] Update update_task() method in backend/app/services/task_service.py to handle priority field
- [ ] T037 [US1] Add priority filter parameter to list_tasks() method in backend/app/services/task_service.py
- [ ] T038 [US1] Update POST /tasks endpoint in backend/app/api/routes/tasks.py to accept priority
- [ ] T039 [US1] Update PUT /tasks/{task_id} endpoint in backend/app/api/routes/tasks.py to accept priority
- [ ] T040 [US1] Update GET /tasks endpoint in backend/app/api/routes/tasks.py to accept priority query parameter
- [ ] T041 [US1] Add activity logging for priority changes in task update operations

### Frontend Implementation for US1

- [ ] T042 [P] [US1] Create PriorityBadge component in frontend/src/components/tasks/PriorityBadge.tsx with color coding
- [ ] T043 [P] [US1] Create PrioritySelector component in frontend/src/components/tasks/PrioritySelector.tsx (dropdown)
- [ ] T044 [US1] Update TaskForm component in frontend/src/components/tasks/TaskForm.tsx to include priority selector
- [ ] T045 [US1] Update TaskCard component in frontend/src/components/tasks/TaskCard.tsx to display PriorityBadge
- [ ] T046 [US1] Add priority filter to FilterPanel component in frontend/src/components/tasks/FilterPanel.tsx
- [ ] T047 [US1] Update API client in frontend/src/services/api.ts to include priority in task operations

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Search and Filter Tasks (Priority: P2)

**Goal**: Users can quickly find specific tasks among potentially hundreds of items by searching title/description and filtering by status, priority, or tags

**Independent Test**: Create multiple tasks with various attributes, then search for specific keywords and apply different filter combinations to verify correct results

### Backend Implementation for US2

- [ ] T048 [P] [US2] Implement search_tasks() method in backend/app/services/task_service.py with ILIKE queries
- [ ] T049 [US2] Add search parameter to GET /tasks endpoint in backend/app/api/routes/tasks.py
- [ ] T050 [US2] Add completed filter parameter to GET /tasks endpoint in backend/app/api/routes/tasks.py
- [ ] T051 [US2] Add due_date_from and due_date_to filter parameters to GET /tasks endpoint
- [ ] T052 [US2] Optimize database queries with proper indexes for search performance

### Frontend Implementation for US2

- [ ] T053 [P] [US2] Create SearchBar component in frontend/src/components/tasks/SearchBar.tsx with debounced input
- [ ] T054 [P] [US2] Create useDebounce hook in frontend/src/hooks/useDebounce.ts
- [ ] T055 [P] [US2] Create FilterPanel component in frontend/src/components/tasks/FilterPanel.tsx with status and date range filters
- [ ] T056 [US2] Create useTaskSearch hook in frontend/src/hooks/useTaskSearch.ts to manage search state
- [ ] T057 [US2] Create useTaskFilter hook in frontend/src/hooks/useTaskFilter.ts to manage filter state
- [ ] T058 [US2] Update TaskList component to integrate SearchBar and FilterPanel
- [ ] T059 [US2] Update API client in frontend/src/services/api.ts with searchTasks() method

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Tag-Based Organization (Priority: P3)

**Goal**: Users can create custom tags and assign multiple tags to each task for flexible categorization

**Independent Test**: Create tags, assign them to tasks, filter by tags, and manage tag CRUD operations independently

### Backend Implementation for US3

- [ ] T060 [P] [US3] Create TagService in backend/app/services/tag_service.py with CRUD methods
- [ ] T061 [US3] Implement create_tag() method with duplicate name validation (case-insensitive)
- [ ] T062 [US3] Implement list_tags() method filtered by user_id
- [ ] T063 [US3] Implement update_tag() method
- [ ] T064 [US3] Implement delete_tag() method (cascades to task_tags)
- [ ] T065 [US3] Implement assign_tag_to_task() method with max 10 tags validation
- [ ] T066 [US3] Implement remove_tag_from_task() method
- [ ] T067 [US3] Update TaskService to include tags in task queries (JOIN with task_tags and tags)
- [ ] T068 [P] [US3] Create tags router in backend/app/api/routes/tags.py with GET, POST, PUT, DELETE endpoints
- [ ] T069 [US3] Add tag filter parameter to GET /tasks endpoint (supports multiple tags)
- [ ] T070 [US3] Add activity logging for tag_added and tag_removed actions

### Frontend Implementation for US3

- [ ] T071 [P] [US3] Create TagChip component in frontend/src/components/tasks/TagChip.tsx for displaying tags
- [ ] T072 [P] [US3] Create TagInput component in frontend/src/components/tasks/TagInput.tsx with autocomplete
- [ ] T073 [P] [US3] Create TagManager component in frontend/src/components/tasks/TagManager.tsx for CRUD operations
- [ ] T074 [US3] Update TaskForm to include TagInput for assigning tags
- [ ] T075 [US3] Update TaskCard to display TagChips
- [ ] T076 [US3] Add tag filter to FilterPanel component
- [ ] T077 [US3] Create tagApi methods in frontend/src/services/api.ts (listTags, createTag, updateTag, deleteTag)
- [ ] T078 [US3] Create useTagAutocomplete hook in frontend/src/hooks/useTagAutocomplete.ts

**Checkpoint**: User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Task Sorting (Priority: P4)

**Goal**: Users can view their tasks in different orders based on context (creation date, due date, priority)

**Independent Test**: Create tasks with different dates and priorities, then apply each sort option and verify the correct order

### Backend Implementation for US4

- [ ] T079 [US4] Add sort_by and sort_order parameters to list_tasks() method in backend/app/services/task_service.py
- [ ] T080 [US4] Implement dynamic sorting logic (created_at, due_date, priority, updated_at)
- [ ] T081 [US4] Add sort_by and sort_order query parameters to GET /tasks endpoint in backend/app/api/routes/tasks.py

### Frontend Implementation for US4

- [ ] T082 [P] [US4] Create SortDropdown component in frontend/src/components/tasks/SortDropdown.tsx
- [ ] T083 [US4] Create useTaskSort hook in frontend/src/hooks/useTaskSort.ts to manage sort state
- [ ] T084 [US4] Update TaskList component to integrate SortDropdown
- [ ] T085 [US4] Update API client to include sort parameters in searchTasks() method

**Checkpoint**: User Stories 1-4 should all work independently

---

## Phase 7: User Story 5 - Due Date Management (Priority: P5)

**Goal**: Users can assign due dates to tasks and see which tasks are overdue at a glance

**Independent Test**: Create tasks with various due dates (past, present, future), verify date picker functionality, and confirm overdue task highlighting

### Backend Implementation for US5

- [ ] T086 [P] [US5] Add due_date field validation in backend/app/schemas/task.py (datetime format)
- [ ] T087 [US5] Update create_task() and update_task() methods to handle due_date field
- [ ] T088 [US5] Create get_overdue_tasks() method in backend/app/services/task_service.py
- [ ] T089 [US5] Add due_date to task response schemas
- [ ] T090 [US5] Add activity logging for due_date changes

### Frontend Implementation for US5

- [ ] T091 [P] [US5] Create DatePicker component in frontend/src/components/tasks/DatePicker.tsx
- [ ] T092 [P] [US5] Create OverdueBadge component in frontend/src/components/tasks/OverdueBadge.tsx (red indicator)
- [ ] T093 [US5] Update TaskForm to include DatePicker for due_date
- [ ] T094 [US5] Update TaskCard to display due date and OverdueBadge if overdue
- [ ] T095 [US5] Create isOverdue() utility function in frontend/src/utils/dateUtils.ts
- [ ] T096 [US5] Add overdue visual styling (red border/background) to TaskCard

**Checkpoint**: User Stories 1-5 should all work independently

---

## Phase 8: User Story 6 - Reminder Notifications (Priority: P6)

**Goal**: Users can set reminder times and receive notifications before tasks are due

**Independent Test**: Set reminders on tasks with due dates, wait for reminder time, and verify notification delivery (console log for Phase III-IV)

### Backend Implementation for US6

- [ ] T097 [P] [US6] Create ReminderService in backend/app/services/reminder_service.py
- [ ] T098 [US6] Implement create_reminder() method with validation (remind_at must be future)
- [ ] T099 [US6] Implement list_reminders() method filtered by user_id
- [ ] T100 [US6] Implement delete_reminder() method
- [ ] T101 [US6] Implement process_pending_reminders() method in ReminderService
- [ ] T102 [US6] Update check_reminders() function in backend/app/scheduler/reminder_scheduler.py to call process_pending_reminders()
- [ ] T103 [US6] Implement send_reminder() method (console log for Phase III-IV)
- [ ] T104 [US6] Update reminder status to 'sent' after successful delivery
- [ ] T105 [P] [US6] Create reminders router in backend/app/api/routes/reminders.py with GET, POST, DELETE endpoints
- [ ] T106 [US6] Add activity logging for reminder_set and reminder_sent actions

### Frontend Implementation for US6

- [ ] T107 [P] [US6] Create ReminderModal component in frontend/src/components/tasks/ReminderModal.tsx
- [ ] T108 [P] [US6] Create ReminderList component in frontend/src/components/tasks/ReminderList.tsx
- [ ] T109 [US6] Add reminder button to TaskCard component
- [ ] T110 [US6] Implement reminder time presets (1 hour, 1 day, 1 week before due date)
- [ ] T111 [US6] Create reminderApi methods in frontend/src/services/api.ts (createReminder, listReminders, deleteReminder)
- [ ] T112 [US6] Display active reminders on TaskCard

**Checkpoint**: User Stories 1-6 should all work independently

---

## Phase 9: User Story 7 - Recurring Task Automation (Priority: P7)

**Goal**: Users can create tasks that repeat on a schedule, and the system automatically creates the next instance when completed

**Independent Test**: Create a recurring task, complete it, and verify that a new instance is automatically created with the correct next due date

### Backend Implementation for US7

- [ ] T113 [P] [US7] Create RecurringService in backend/app/services/recurring_service.py
- [ ] T114 [US7] Implement calculate_next_due_date() method using python-dateutil.relativedelta
- [ ] T115 [US7] Implement create_recurring_instance() method (copies task metadata, calculates new due_date)
- [ ] T116 [US7] Update complete_task() method in TaskService to check is_recurring flag
- [ ] T117 [US7] Integrate RecurringService into complete_task() workflow
- [ ] T118 [US7] Update POST /tasks/{task_id}/complete endpoint to return both completed task and next instance
- [ ] T119 [US7] Add validation: is_recurring requires recurrence_rule and due_date
- [ ] T120 [US7] Add activity logging for recurring task creation

### Frontend Implementation for US7

- [ ] T121 [P] [US7] Create RecurringModal component in frontend/src/components/tasks/RecurringModal.tsx
- [ ] T122 [P] [US7] Create RecurrenceBadge component in frontend/src/components/tasks/RecurrenceBadge.tsx
- [ ] T123 [US7] Add recurring toggle and recurrence_rule selector to TaskForm
- [ ] T124 [US7] Display RecurrenceBadge on TaskCard for recurring tasks
- [ ] T125 [US7] Update completeTask() API method to handle next instance response
- [ ] T126 [US7] Display notification when next recurring instance is created

**Checkpoint**: User Stories 1-7 should all work independently

---

## Phase 10: User Story 8 - Activity Audit Log (Priority: P8)

**Goal**: Users can track all changes to tasks for accountability and history

**Independent Test**: Perform various task operations and verify that each action appears in the activity log with correct details

### Backend Implementation for US8

- [ ] T127 [US8] Ensure ActivityService.log_activity() is called in all task operations (create, update, complete, delete)
- [ ] T128 [US8] Ensure ActivityService.log_activity() is called for tag operations (tag_added, tag_removed)
- [ ] T129 [US8] Ensure ActivityService.log_activity() is called for reminder operations (reminder_set, reminder_sent)
- [ ] T130 [US8] Implement get_task_activity() method in ActivityService
- [ ] T131 [US8] Implement get_user_activity() method in ActivityService
- [ ] T132 [P] [US8] Create activity router in backend/app/api/routes/activity.py
- [ ] T133 [US8] Implement GET /tasks/{task_id}/activity endpoint
- [ ] T134 [US8] Implement GET /activity endpoint (user-level activity)
- [ ] T135 [US8] Add pagination support (limit, offset) to activity endpoints

### Frontend Implementation for US8

- [ ] T136 [P] [US8] Create ActivityLog component in frontend/src/components/tasks/ActivityLog.tsx
- [ ] T137 [P] [US8] Create ActivityItem component in frontend/src/components/tasks/ActivityItem.tsx
- [ ] T138 [US8] Create ActivityTimeline component in frontend/src/components/tasks/ActivityTimeline.tsx
- [ ] T139 [US8] Add activity tab/section to task detail view
- [ ] T140 [US8] Create activityApi methods in frontend/src/services/api.ts (getTaskActivity, getUserActivity)
- [ ] T141 [US8] Format activity details based on action type (task_created, task_updated, etc.)

**Checkpoint**: User Stories 1-8 should all work independently

---

## Phase 11: User Story 9 - Real-Time Task Updates (Priority: P9)

**Goal**: Users working across multiple devices or browser tabs see task changes reflected automatically

**Independent Test**: Open the app in two browser tabs, make changes in one tab, and verify the other tab updates within the polling interval

### Backend Implementation for US9

- [ ] T142 [US9] Verify GET /tasks endpoint returns updated_at timestamp for all tasks
- [ ] T143 [US9] Add ETag or Last-Modified headers to task responses (optional optimization)

### Frontend Implementation for US9

- [ ] T144 [P] [US9] Create usePolling hook in frontend/src/hooks/usePolling.ts
- [ ] T145 [US9] Implement polling logic with configurable interval (default 10 seconds)
- [ ] T146 [US9] Integrate usePolling hook into TaskList component
- [ ] T147 [US9] Add visual indicator when tasks are being refreshed
- [ ] T148 [US9] Implement optimistic UI updates to prevent flicker during polling
- [ ] T149 [US9] Add user preference to enable/disable polling

**Checkpoint**: All user stories (1-9) should now be independently functional

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T150 [P] Add error handling for all API endpoints in backend/app/api/routes/
- [ ] T151 [P] Add input validation for all request schemas in backend/app/schemas/
- [ ] T152 [P] Add loading states to all frontend components
- [ ] T153 [P] Add error messages and toast notifications in frontend
- [ ] T154 [P] Optimize database queries with EXPLAIN ANALYZE
- [ ] T155 [P] Add API response caching where appropriate
- [ ] T156 [P] Implement proper error boundaries in frontend/src/components/
- [ ] T157 [P] Add accessibility attributes (ARIA labels) to all interactive components
- [ ] T158 [P] Test responsive design on mobile devices
- [ ] T159 [P] Add keyboard shortcuts for common actions
- [ ] T160 Run quickstart.md validation checklist
- [ ] T161 Update API documentation with new endpoints
- [ ] T162 Code cleanup and remove console.log statements
- [ ] T163 Final security review (SQL injection, XSS, CSRF protection)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-11)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5 → P6 → P7 → P8 → P9)
- **Polish (Phase 12)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational - No dependencies on other stories
- **User Story 3 (P3)**: Can start after Foundational - No dependencies on other stories
- **User Story 4 (P4)**: Can start after Foundational - No dependencies on other stories
- **User Story 5 (P5)**: Can start after Foundational - No dependencies on other stories
- **User Story 6 (P6)**: Depends on US5 (requires due_date field) - Should start after US5
- **User Story 7 (P7)**: Depends on US5 (requires due_date field) - Should start after US5
- **User Story 8 (P8)**: Can start after Foundational - No dependencies on other stories (logs all operations)
- **User Story 9 (P9)**: Can start after Foundational - No dependencies on other stories

### Within Each User Story

- Backend tasks before frontend tasks (API must exist before UI can call it)
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- **Setup (Phase 1)**: All 3 tasks can run in parallel
- **Foundational (Phase 2)**:
  - T006-T009 (table creation) can run in parallel
  - T012-T020 (model creation) can run in parallel after T004-T011
  - T028-T033 (frontend types) can run in parallel
- **Within User Stories**: Tasks marked [P] can run in parallel
- **Across User Stories**: US1, US2, US3, US4, US5, US8, US9 can all be worked on in parallel by different team members after Foundational phase completes
- **US6 and US7**: Can start in parallel after US5 completes

---

## Parallel Example: User Story 1

```bash
# Backend models and schemas (parallel):
Task T034: "Add priority field validation in backend/app/schemas/task.py"

# Frontend components (parallel after backend is done):
Task T042: "Create PriorityBadge component in frontend/src/components/tasks/PriorityBadge.tsx"
Task T043: "Create PrioritySelector component in frontend/src/components/tasks/PrioritySelector.tsx"
```

---

## Parallel Example: User Story 3

```bash
# Backend service methods (parallel):
Task T061: "Implement create_tag() method"
Task T062: "Implement list_tags() method"
Task T063: "Implement update_tag() method"
Task T064: "Implement delete_tag() method"

# Frontend components (parallel after backend is done):
Task T071: "Create TagChip component"
Task T072: "Create TagInput component"
Task T073: "Create TagManager component"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T033) - CRITICAL
3. Complete Phase 3: User Story 1 (T034-T047)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

**MVP Scope**: Priority management only - users can assign and filter by priority

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (Priority) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (Search/Filter) → Test independently → Deploy/Demo
4. Add User Story 3 (Tags) → Test independently → Deploy/Demo
5. Add User Story 4 (Sort) → Test independently → Deploy/Demo
6. Add User Story 5 (Due Dates) → Test independently → Deploy/Demo
7. Add User Story 6 (Reminders) → Test independently → Deploy/Demo
8. Add User Story 7 (Recurring) → Test independently → Deploy/Demo
9. Add User Story 8 (Activity Log) → Test independently → Deploy/Demo
10. Add User Story 9 (Real-Time) → Test independently → Deploy/Demo
11. Polish (Phase 12) → Final release

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers after Foundational phase completes:

**Team A**: US1 (Priority) + US4 (Sort)
**Team B**: US2 (Search/Filter) + US3 (Tags)
**Team C**: US5 (Due Dates) → US6 (Reminders) → US7 (Recurring)
**Team D**: US8 (Activity Log) + US9 (Real-Time)

Stories complete and integrate independently.

---

## Task Count Summary

- **Phase 1 (Setup)**: 3 tasks
- **Phase 2 (Foundational)**: 30 tasks
- **Phase 3 (US1 - Priority)**: 14 tasks
- **Phase 4 (US2 - Search/Filter)**: 12 tasks
- **Phase 5 (US3 - Tags)**: 19 tasks
- **Phase 6 (US4 - Sort)**: 7 tasks
- **Phase 7 (US5 - Due Dates)**: 11 tasks
- **Phase 8 (US6 - Reminders)**: 16 tasks
- **Phase 9 (US7 - Recurring)**: 14 tasks
- **Phase 10 (US8 - Activity Log)**: 15 tasks
- **Phase 11 (US9 - Real-Time)**: 6 tasks
- **Phase 12 (Polish)**: 14 tasks

**Total**: 163 tasks

**Parallelizable Tasks**: 52 tasks marked with [P]

**MVP Scope**: 47 tasks (Setup + Foundational + US1)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Phase V features (Kafka, Dapr, Kubernetes) are NOT included - deferred per plan.md
- Tests are NOT included per specification (not explicitly requested)
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
