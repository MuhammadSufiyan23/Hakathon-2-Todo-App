# Todo Backend Implementation Tasks

## Feature: Todo Backend API with FastAPI, SQLModel, Neon Postgres, Better Auth JWT

This document outlines the implementation tasks for the Todo backend API, following the architectural plan and specifications.

## Phase 1: Setup & Environment

### Goal
Initialize the project structure and install all necessary dependencies.

- [ ] T001 Create backend directory structure with subdirectories (main.py, db.py, models.py, schemas.py, routes/tasks.py, utils/auth.py)
- [ ] T002 Install required dependencies: fastapi, uvicorn, sqlmodel, pydantic, pyjwt, python-dotenv, psycopg-binary, python-multipart
- [ ] T003 Create .env file with DATABASE_URL and BETTER_AUTH_SECRET as specified in the plan
- [ ] T004 Create basic requirements.txt file listing all dependencies with versions

## Phase 2: Foundational Components

### Goal
Establish core components that all user stories depend on.

- [ ] T005 Implement database connection in db.py with engine creation and get_session dependency
- [ ] T006 Create startup event handler to initialize tables (SQLModel.metadata.create_all)
- [ ] T007 Implement JWT authentication utilities in utils/auth.py with get_current_user dependency
- [ ] T008 Set up CORS middleware in main.py for localhost:3000 integration
- [ ] T009 Create basic FastAPI app instance with health check endpoint

## Phase 3: Task Model & Schemas [US1]

### Goal
Create the data model and Pydantic schemas for task management.

### Test Criteria
- Task model properly maps to database schema
- Pydantic schemas enforce validation rules
- All required fields and constraints are implemented

### Implementation Tasks
- [ ] T010 [P] [US1] Create SQLModel Task class in models.py with all required fields (id, user_id, title, description, completed, timestamps)
- [ ] T011 [P] [US1] Implement TaskCreate Pydantic schema in schemas.py with required validation (title 1-200 chars, description max 1000)
- [ ] T012 [P] [US1] Implement TaskUpdate Pydantic schema in schemas.py with optional fields
- [ ] T013 [US1] Implement TaskOut Pydantic schema in schemas.py with all fields including id and timestamps
- [ ] T014 [US1] Add proper indexing to Task model (user_id, completed, composite)

## Phase 4: Task Creation Endpoint [US2]

### Goal
Implement the ability to create new tasks for authenticated users.

### Test Criteria
- Only authenticated users can create tasks
- Created tasks are properly associated with user_id
- Validation is enforced on title and description
- Proper response format is returned

### Implementation Tasks
- [ ] T015 [P] [US2] Create POST /api/tasks endpoint in routes/tasks.py
- [ ] T016 [US2] Add dependency injection for get_session and get_current_user to endpoint
- [ ] T017 [US2] Implement task creation logic with user_id association from JWT
- [ ] T018 [US2] Add proper response model using TaskOut schema
- [ ] T019 [US2] Test task creation with valid and invalid inputs

## Phase 5: Task Listing Endpoint [US3]

### Goal
Implement the ability to list tasks with filtering and sorting for authenticated users.

### Test Criteria
- Only authenticated users can list their tasks
- Filtering by status (all/pending/completed) works correctly
- Sorting by created/title works correctly
- Proper pagination if needed

### Implementation Tasks
- [ ] T020 [P] [US3] Create GET /api/tasks endpoint in routes/tasks.py
- [ ] T021 [US3] Add query parameters for status, sort, and order with proper typing
- [ ] T022 [US3] Implement filtering logic based on user_id and status parameter
- [ ] T023 [US3] Implement sorting logic based on sort and order parameters
- [ ] T024 [US3] Return tasks using TaskOut schema with proper response format
- [ ] T025 [US3] Test filtering and sorting functionality

## Phase 6: Individual Task Operations [US4]

### Goal
Implement retrieval, update, and deletion of individual tasks with proper user isolation.

### Test Criteria
- Users can only access their own tasks
- Update operations properly update task properties
- Delete operations permanently remove tasks
- Proper error handling for unauthorized access

### Implementation Tasks
- [ ] T026 [P] [US4] Create GET /api/tasks/{id} endpoint with user ownership check
- [ ] T027 [P] [US4] Create PUT /api/tasks/{id} endpoint with user ownership check
- [ ] T028 [P] [US4] Create DELETE /api/tasks/{id} endpoint with user ownership check
- [ ] T029 [US4] Implement proper error handling (403 for wrong user, 404 for not found)
- [ ] T030 [US4] Test individual task operations with various scenarios

## Phase 7: Task Completion Toggle [US5]

### Goal
Implement the ability to toggle task completion status.

### Test Criteria
- Only task owner can toggle completion status
- Task completion status is properly updated
- Proper response with updated task is returned

### Implementation Tasks
- [ ] T031 [P] [US5] Create PATCH /api/tasks/{id}/complete endpoint
- [ ] T032 [US5] Implement completion toggle logic with user ownership verification
- [ ] T033 [US5] Return updated task using TaskOut schema
- [ ] T034 [US5] Test completion toggle functionality

## Phase 8: Error Handling & Logging [US6]

### Goal
Implement comprehensive error handling and logging for the API.

### Test Criteria
- Proper error responses for all error conditions
- Logging for debugging and monitoring
- Consistent error format across all endpoints

### Implementation Tasks
- [ ] T035 [P] [US6] Implement custom exception handlers for 401/403/404 errors
- [ ] T036 [P] [US6] Add logging for incoming requests and database operations
- [ ] T037 [US6] Ensure consistent error response format across all endpoints
- [ ] T038 [US6] Test error scenarios and validate response formats

## Phase 9: Testing & Integration [US7]

### Goal
Test the complete API functionality and prepare for frontend integration.

### Test Criteria
- All endpoints work as specified
- Authentication and authorization function properly
- API integrates correctly with frontend
- Performance meets requirements

### Implementation Tasks
- [ ] T039 [P] [US7] Test all endpoints manually with curl/Postman
- [ ] T040 [P] [US7] Verify JWT authentication flow works correctly
- [ ] T041 [US7] Test CORS configuration with frontend integration
- [ ] T042 [US7] Verify database persistence works correctly
- [ ] T043 [US7] Run full API test suite to validate all functionality

## Phase 10: Polish & Documentation

### Goal
Finalize the implementation with documentation and best practices.

- [ ] T044 Add comprehensive API documentation with OpenAPI/Swagger
- [ ] T045 Add input sanitization and additional security measures
- [ ] T046 Optimize database queries and add performance improvements
- [ ] T047 Update main.py with proper startup/shutdown events
- [ ] T048 Create README with setup and usage instructions

## Dependencies

1. Phase 1 (Setup) must be completed before any other phase
2. Phase 2 (Foundational) must be completed before any user story phases
3. Each user story phase can be worked on independently after foundational phase

## Parallel Execution Opportunities

### Within each user story:
- [US1] Task model and schemas can be developed in parallel (T010-T012)
- [US2] Endpoint creation and logic implementation can be parallelized
- [US3] Query parameter implementation and filtering logic can be parallelized
- [US4] Individual task endpoints (GET/PUT/DELETE) can be implemented in parallel
- [US7] Manual testing of different endpoints can be parallelized

## Implementation Strategy

1. **MVP Scope**: Complete Phase 1 (Setup), Phase 2 (Foundational), and US2 (Task Creation) for minimal working API
2. **Incremental Delivery**: Add one user story at a time, testing each increment
3. **Security First**: Ensure authentication and authorization work correctly before adding features
4. **Test Early**: Validate database connections and JWT handling early in the process