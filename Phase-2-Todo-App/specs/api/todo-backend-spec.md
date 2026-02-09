# Todo Backend API Specification

## Overview & Architecture

This specification defines the backend API for the Todo application, built with FastAPI and SQLModel, integrated with Neon Postgres database and Better Auth JWT authentication system. The backend provides secure, scalable task management functionality with user isolation, filtering, and comprehensive CRUD operations.

### Core Components
- **Framework**: FastAPI for high-performance asynchronous API
- **ORM**: SQLModel for database modeling and querying
- **Database**: Neon Serverless PostgreSQL for cloud-native database access
- **Authentication**: Better Auth JWT verification for secure user access
- **Architecture**: Microservice-ready REST API with clean separation of concerns

## Environment & Setup

### Dependencies
Required packages to install:
```bash
pip install fastapi uvicorn sqlmodel pyjwt python-multipart python-jose[cryptography] psycopg2-binary
```

### Environment Variables
Create `.env` file in the backend directory with:
```
DATABASE_URL=postgresql://neondb_owner:npg_exvVPkW2qRc4@ep-spring-firefly-a712cq9y-pooler.ap-southeast-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
BETTER_AUTH_SECRET=3513ab71de9f07764066833058162ab07066be056b085cd636776776b5a5c6d4e9e
BETTER_AUTH_URL=http://localhost:3000
DEBUG=true
```

## Database Connection & Schema

### Connection Configuration
The application connects to Neon PostgreSQL using the DATABASE_URL environment variable. Connection pooling is handled automatically by SQLModel/SQLAlchemy.

### Database Schema
The database contains two primary entities:

#### Users Table (Managed by Better Auth)
- `id`: String (primary key) - Unique identifier from Better Auth
- `email`: String - User's email address
- `name`: String - User's display name
- `created_at`: DateTime - Account creation timestamp

#### Tasks Table (Application Managed)
- `id`: UUID (primary key) - Auto-generated unique identifier
- `user_id`: String (foreign key) - References Better Auth user ID
- `title`: String (1-200 chars) - Task title
- `description`: String (max 1000 chars, optional) - Task description
- `completed`: Boolean - Task completion status (default: false)
- `created_at`: DateTime - Creation timestamp (auto-generated)
- `updated_at`: DateTime - Last update timestamp (auto-updated)

#### Indexes
- Index on `user_id` for efficient user-based queries
- Index on `completed` for efficient filtering
- Composite index on `(user_id, completed)` for combined queries

## Models & Pydantic Schemas

### SQLModel Task Model
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid

class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = False

class Task(TaskBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
```

### Pydantic Request/Response Models
```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None

class TaskOut(TaskBase):
    id: uuid.UUID
    user_id: str
    created_at: datetime
    updated_at: datetime
```

## Authentication & JWT Middleware

### JWT Token Verification
- Extract JWT token from `Authorization: Bearer <token>` header
- Verify token using BETTER_AUTH_SECRET with HS256 algorithm
- Decode token to extract user_id and email
- Enforce user_id on all task operations for user isolation

### Authentication Dependency
```python
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Dict

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, str]:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=["HS256"])
        user_id = payload.get("userId") or payload.get("id")
        email = payload.get("email")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: no user ID")

        return {"user_id": user_id, "email": email}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
```

## API Endpoints

### GET /api/tasks
**Description**: Retrieve list of tasks for the authenticated user
- **Method**: GET
- **Security**: JWT Bearer token required
- **Query Parameters**:
  - `status`: Optional string - Filter by completion status ("all", "pending", "completed"; default: "all")
  - `sort`: Optional string - Sort by ("created", "title"; default: "created")
  - `order`: Optional string - Sort order ("asc", "desc"; default: "desc")
- **Response**: Array of TaskOut objects
- **Errors**:
  - 401: Unauthorized (missing or invalid token)

### POST /api/tasks
**Description**: Create a new task for the authenticated user
- **Method**: POST
- **Security**: JWT Bearer token required
- **Request Body**: TaskCreate object
- **Response**: Created TaskOut object
- **Errors**:
  - 400: Validation error (invalid title/description)
  - 401: Unauthorized (missing or invalid token)

### GET /api/tasks/{id}
**Description**: Retrieve a specific task by ID
- **Method**: GET
- **Path Parameter**: `id` - Task UUID
- **Security**: JWT Bearer token required
- **Response**: TaskOut object
- **Errors**:
  - 401: Unauthorized (missing or invalid token)
  - 403: Forbidden (task belongs to different user)
  - 404: Not found (task does not exist)

### PUT /api/tasks/{id}
**Description**: Update an existing task
- **Method**: PUT
- **Path Parameter**: `id` - Task UUID
- **Security**: JWT Bearer token required
- **Request Body**: TaskUpdate object
- **Response**: Updated TaskOut object
- **Errors**:
  - 400: Validation error (invalid fields)
  - 401: Unauthorized (missing or invalid token)
  - 403: Forbidden (task belongs to different user)
  - 404: Not found (task does not exist)

### DELETE /api/tasks/{id}
**Description**: Delete a specific task
- **Method**: DELETE
- **Path Parameter**: `id` - Task UUID
- **Security**: JWT Bearer token required
- **Response**: Success message
- **Errors**:
  - 401: Unauthorized (missing or invalid token)
  - 403: Forbidden (task belongs to different user)
  - 404: Not found (task does not exist)

### PATCH /api/tasks/{id}/complete
**Description**: Toggle the completion status of a task
- **Method**: PATCH
- **Path Parameter**: `id` - Task UUID
- **Security**: JWT Bearer token required
- **Response**: Updated TaskOut object with toggled completion status
- **Errors**:
  - 401: Unauthorized (missing or invalid token)
  - 403: Forbidden (task belongs to different user)
  - 404: Not found (task does not exist)

## Error Handling & Logging

### HTTP Status Codes
- 200: Success for GET, PUT, PATCH operations
- 201: Created for POST operations
- 204: No Content for DELETE operations
- 400: Bad Request for validation errors
- 401: Unauthorized for authentication failures
- 403: Forbidden for authorization failures (wrong user)
- 404: Not Found for missing resources
- 500: Internal Server Error for unexpected failures

### Error Response Format
```json
{
  "detail": "Error message"
}
```

### Logging
- Log all incoming requests with method, path, and user ID
- Log all database operations for debugging
- Log authentication failures for security monitoring
- Log all errors with stack traces in DEBUG mode

## CORS & Security

### CORS Configuration
- Allow origins: ["http://localhost:3000"] (frontend)
- Allow methods: ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
- Allow headers: ["Content-Type", "Authorization", "X-Requested-With"]
- Allow credentials: true

### Security Measures
- Input validation using Pydantic models
- SQL injection prevention via SQLModel parameterized queries
- JWT token expiration handling (7-day default)
- Rate limiting to prevent abuse (implementation TBD)
- User isolation - users can only access their own tasks

## Testing & Integration with Frontend

### API Integration
- Backend runs on http://localhost:8000 (uvicorn main:app --reload --port 8000)
- Frontend calls backend via configured proxy or direct calls
- All responses are JSON serializable (SQLModel converted to dict)

### Frontend Compatibility
- Support for common HTTP methods (GET, POST, PUT, DELETE, PATCH)
- Consistent response format for easy frontend handling
- Proper error responses that frontend can display to users
- Support for query parameters for filtering and sorting

## Edge Cases

### Invalid ID Handling
- Return 404 when requesting a task with malformed UUID
- Return 404 when requesting a task with valid UUID but non-existent task

### No Tasks Scenario
- GET /api/tasks returns empty array when user has no tasks
- Proper pagination handling when no results exist

### Expired Token Handling
- Return 401 when JWT token has expired
- Frontend should redirect to login page upon receiving 401
- Token refresh mechanism (if implemented) should be transparent to API layer

### Concurrency Handling
- Handle multiple simultaneous requests from same user
- Prevent race conditions during task updates
- Database transactions ensure data consistency

### Large Dataset Handling
- Implement pagination for users with many tasks (future enhancement)
- Optimize queries with proper indexing
- Limit result sets to prevent performance issues