# Todo Backend Implementation Plan

## 1. Prerequisites & Setup Steps

### Dependencies to Install
```bash
pip install fastapi uvicorn sqlmodel pydantic pyjwt python-dotenv psycopg-binary python-multipart
```

### Folder Structure
Create the following structure in `/backend/`:
```
/backend/
├── main.py
├── db.py
├── models.py
├── schemas.py
├── routes/
│   └── tasks.py
├── utils/
│   └── auth.py
└── .env
```

### Environment Configuration
Create `.env` file with:
```
DATABASE_URL=postgresql://neondb_owner:npg_exvVPkW2qRc4@ep-spring-firefly-a712cq9y-pooler.ap-southeast-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
BETTER_AUTH_SECRET=3513ab71de9f07764066833058162ab07066be056b085cd636776776b5a5c6d4e9e
BETTER_AUTH_URL=http://localhost:3000
DEBUG=true
```

## 2. High-Level Implementation Phases

### Phase 1: Environment & Dependencies Setup
- Install all required packages
- Create project directory structure
- Configure environment variables
- Verify installation with basic FastAPI hello world

### Phase 2: Database Connection (db.py)
- Create engine with echo=True for debug
- Implement get_session dependency
- Add startup event to create tables (SQLModel.metadata.create_all)
- Test database connection

### Phase 3: Models & Schemas (models.py + schemas.py)
- Create SQLModel Task class with proper fields
- Define Pydantic schemas: TaskCreate, TaskUpdate, TaskOut
- Add validation constraints (title length, description max)
- Include auto timestamps with proper defaults

### Phase 4: Authentication Middleware (utils/auth.py)
- Implement get_current_user dependency
- Create JWT decoder function
- Extract user_id from token payload
- Raise 401 exceptions for invalid tokens
- Use HTTPBearer for token extraction

### Phase 5: API Router & Endpoints (routes/tasks.py)
- Create APIRouter with prefix="/api/tasks"
- Implement all endpoints with proper dependencies
- GET / : Filtered list with query parameters
- POST / : Create with user_id from auth
- GET /{id}: Retrieve single task with ownership check
- PUT /{id}: Update task with ownership check
- DELETE /{id}: Delete task with ownership check
- PATCH /{id}/complete: Toggle completion status with ownership check
- Use proper session handling with commit/refresh

### Phase 6: Main App Setup (main.py)
- Initialize FastAPI app instance
- Configure CORS middleware for localhost:3000
- Include task router
- Add health check endpoint
- Implement startup/shutdown events

### Phase 7: Error Handling & Logging
- Add custom exception handlers for 401/403/404
- Implement logging for debugging
- Ensure proper error response formats
- Add validation error handling

### Phase 8: Testing & Integration Prep
- Start server with uvicorn on port 8000
- Test all endpoints manually
- Verify JWT authentication flow
- Confirm CORS configuration works with frontend
- Document API endpoints for frontend integration

## 3. Key Technical Decisions

- Use sync Session for simplicity (easier debugging for hackathon)
- JWT decode with algorithms=["HS256"] using pyjwt
- Pydantic response_model for automatic serialization
- Query parameters: status (all/pending/completed), sort (created/title), order (asc/desc)
- Timestamps: Field(default_factory=datetime.utcnow) with proper updates
- User ID: Extract from JWT payload["sub"] or "user_id" field
- Error responses: Follow RFC 7807 standard for consistency

## 4. Dependencies List with Versions

- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- sqlmodel==0.0.16
- pydantic==2.5.0
- pyjwt==2.8.0
- python-dotenv==1.0.0
- psycopg-binary==3.1.13
- python-multipart==0.0.6

## 5. Potential Risks & Mitigations

- **Neon connection fail**: Verify URL format, ensure sslmode=require, check pooler availability
- **JWT decode error**: Confirm secret matches frontend, validate token structure
- **Table not created**: Ensure create_all is called in startup event
- **CORS block**: Configure proper origins for development and production
- **Performance on list**: Verify indexes exist on user_id and completed fields
- **Security vulnerabilities**: Sanitize all inputs, use parameterized queries
- **Concurrent access**: Use proper transaction handling in session management

## 6. Estimated Task Breakdown Summary

- Task 1: Environment setup and dependency installation
- Task 2: Database connection and session management
- Task 3: Task model and Pydantic schemas
- Task 4: JWT authentication utilities
- Task 5: Task creation endpoint (POST /api/tasks)
- Task 6: Task listing endpoint (GET /api/tasks) with filters
- Task 7: Individual task endpoints (GET/PUT/DELETE /api/tasks/{id})
- Task 8: Task completion toggle endpoint (PATCH /api/tasks/{id}/complete)
- Task 9: Main app configuration and CORS setup
- Task 10: Error handling and logging
- Task 11: Testing and integration verification

## 7. Constitution & Spec Compliance Checklist

- [x] Referenced all @specs/... files? - Yes, backend spec and related files
- [x] Enforced JWT + user_id filter? - Planned in auth middleware and endpoints
- [x] Used FastAPI + SQLModel + Neon? - Confirmed in plan
- [x] Prepared for frontend calls (CORS, JSON)? - CORS configuration planned
- [x] Security (401/403, no leaks)? - Authentication and authorization planned
- [x] Proper validation and error handling? - Planned in phases
- [x] Database schema compliance? - Matches specification
- [x] API endpoint compliance? - All endpoints as specified