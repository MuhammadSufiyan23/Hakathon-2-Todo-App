# Frontend Data Model for Beautiful Todo Application

## 1. Task Entity

### Task Interface
```typescript
interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  createdAt: string; // ISO date string
  updatedAt: string; // ISO date string
  userId: string; // From JWT token, not stored in component state
  dueDate?: string; // Optional due date
  priority?: 'low' | 'medium' | 'high'; // Optional priority level
}
```

### Task State Management
- **Local State**: Individual task properties during editing
- **Server State**: Managed by React Query with optimistic updates
- **UI State**: Loading, error, success states for individual operations

## 2. User Session Entity

### Session Interface
```typescript
interface Session {
  user: {
    id: string;
    email: string;
    name: string;
  };
  token: string; // JWT token for API requests
  expiresAt: string; // Expiration timestamp
}
```

### Session State Management
- **Global State**: Managed by Better Auth hooks
- **Persistence**: Handled by Better Auth client
- **Token Refresh**: Automatic refresh mechanism

## 3. Form State Entities

### AuthForm State
```typescript
interface AuthFormState {
  email: string;
  password: string;
  confirmPassword?: string; // For signup only
  loading: boolean;
  error?: string;
  success?: boolean;
}
```

### TaskForm State
```typescript
interface TaskFormState {
  title: string;
  description: string;
  completed: boolean;
  dueDate?: string;
  priority: 'low' | 'medium' | 'high';
  loading: boolean;
  error?: string;
}
```

## 4. UI State Entities

### Filter State
```typescript
interface FilterState {
  status: 'all' | 'pending' | 'completed';
  sortBy: 'createdAt' | 'title' | 'dueDate';
  sortOrder: 'asc' | 'desc';
}
```

### Loading State
```typescript
interface LoadingState {
  tasks: 'idle' | 'loading' | 'success' | 'error';
  form: 'idle' | 'submitting' | 'success' | 'error';
  auth: 'idle' | 'checking' | 'authenticated' | 'unauthenticated';
}
```

## 5. Animation State Entities

### Motion Variant States
```typescript
type MotionVariant = 'hidden' | 'visible' | 'exit' | 'hover' | 'tap';

interface AnimationState {
  current: MotionVariant;
  previous: MotionVariant;
  isAnimating: boolean;
}
```

## 6. API Response Models

### Task API Responses
```typescript
// GET /api/tasks response
interface GetTasksResponse {
  tasks: Task[];
  totalCount: number;
  currentPage: number;
  totalPages: number;
}

// POST /api/tasks response
interface CreateTaskResponse {
  task: Task;
  message: string;
}

// PUT /api/tasks/:id response
interface UpdateTaskResponse {
  task: Task;
  message: string;
}

// DELETE /api/tasks/:id response
interface DeleteTaskResponse {
  message: string;
}
```

## 7. Validation Rules

### Task Validation
- **Title**: Required, minimum 1 character, maximum 200 characters
- **Description**: Optional, maximum 1000 characters
- **Completed**: Boolean, default false
- **Due Date**: Optional, must be valid date string
- **Priority**: Optional, one of 'low', 'medium', 'high'

### Auth Validation
- **Email**: Required, valid email format
- **Password**: Required, minimum 8 characters, must contain uppercase, lowercase, and number
- **Confirm Password**: Required for signup, must match password

## 8. State Transitions

### Task Lifecycle
1. **Initial State**: Empty form with default values
2. **Loading**: Fetching tasks from API
3. **Loaded**: Tasks displayed in list
4. **Editing**: Task form open with pre-filled values
5. **Submitting**: Saving changes to API
6. **Success**: Changes applied with optimistic update
7. **Error**: Error state with rollback if needed

### Authentication Lifecycle
1. **Initial State**: Checking for existing session
2. **Authenticated**: Session exists and valid
3. **Unauthenticated**: No valid session
4. **Authenticating**: Processing sign-in/up
5. **Success**: Session established
6. **Error**: Authentication failed

---
**Model Version**: 1.0
**Created**: 2026-01-14
**Last Updated**: 2026-01-14