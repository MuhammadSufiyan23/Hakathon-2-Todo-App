# Data Model and Event Schemas: OCI Full System Integration

**Feature**: 1-oci-integration
**Created**: 2026-02-09

## Database Models (Existing - Maintained)

### Task Model
```typescript
interface Task {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  status: 'pending' | 'in-progress' | 'completed';
  priority: 'low' | 'medium' | 'high';
  due_date?: string; // ISO 8601 format
  created_at: string;
  updated_at: string;
  tags?: string[];
  recurrence_pattern?: string;
}
```

### User Model
```typescript
interface User {
  id: string;
  email: string;
  created_at: string;
  updated_at: string;
}
```

## Event Schemas (New - For Kafka Integration)

### Task Events Schema (`task-events` topic)

#### Task Created Event
```json
{
  "eventId": "uuid",
  "source": "/services/backend",
  "type": "task.created",
  "subject": "task:{taskId}",
  "time": "ISO 8601 timestamp",
  "correlationId": "request-correlation-id",
  "data": {
    "taskId": "string",
    "userId": "string",
    "operation": "create",
    "taskData": {
      "id": "string",
      "user_id": "string",
      "title": "string",
      "description": "string",
      "status": "pending",
      "priority": "low|medium|high",
      "due_date": "ISO 8601",
      "created_at": "ISO 8601",
      "updated_at": "ISO 8601",
      "tags": ["string"],
      "recurrence_pattern": "string"
    },
    "timestamp": "ISO 8601"
  }
}
```

#### Task Updated Event
```json
{
  "eventId": "uuid",
  "source": "/services/backend",
  "type": "task.updated",
  "subject": "task:{taskId}",
  "time": "ISO 8601 timestamp",
  "correlationId": "request-correlation-id",
  "data": {
    "taskId": "string",
    "userId": "string",
    "operation": "update",
    "updates": {
      "field": "value" // Only changed fields
    },
    "previous_state": {
      // Previous task state
    },
    "new_state": {
      // New task state
    },
    "timestamp": "ISO 8601"
  }
}
```

#### Task Completed Event
```json
{
  "eventId": "uuid",
  "source": "/services/backend",
  "type": "task.completed",
  "subject": "task:{taskId}",
  "time": "ISO 8601 timestamp",
  "correlationId": "request-correlation-id",
  "data": {
    "taskId": "string",
    "userId": "string",
    "operation": "complete",
    "completed_at": "ISO 8601",
    "taskData": {
      // Full task data at completion
    },
    "timestamp": "ISO 8601"
  }
}
```

#### Task Deleted Event
```json
{
  "eventId": "uuid",
  "source": "/services/backend",
  "type": "task.deleted",
  "subject": "task:{taskId}",
  "time": "ISO 8601 timestamp",
  "correlationId": "request-correlation-id",
  "data": {
    "taskId": "string",
    "userId": "string",
    "operation": "delete",
    "deleted_at": "ISO 8601",
    "taskData": {
      // Task data at deletion time
    },
    "timestamp": "ISO 8601"
  }
}
```

### Reminder Events Schema (`reminders` topic)

#### Reminder Due Event
```json
{
  "eventId": "uuid",
  "source": "/services/scheduler",
  "type": "reminder.due",
  "subject": "reminder:{taskId}",
  "time": "ISO 8601 timestamp",
  "correlationId": "request-correlation-id",
  "data": {
    "taskId": "string",
    "userId": "string",
    "reminderType": "due-date|custom",
    "dueTime": "ISO 8601",
    "notificationChannel": "email|in-app|push",
    "taskTitle": "string",
    "timestamp": "ISO 8601"
  }
}
```

#### Reminder Created Event
```json
{
  "eventId": "uuid",
  "source": "/services/backend",
  "type": "reminder.created",
  "subject": "reminder:{taskId}",
  "time": "ISO 8601 timestamp",
  "correlationId": "request-correlation-id",
  "data": {
    "taskId": "string",
    "userId": "string",
    "reminderTime": "ISO 8601",
    "reminderConfig": {
      "notifyBeforeHours": number,
      "channels": ["email", "in-app", "push"]
    },
    "timestamp": "ISO 8601"
  }
}
```

### Task Update Events Schema (`task-updates` topic)

#### Real-time Sync Event
```json
{
  "eventId": "uuid",
  "source": "/services/backend",
  "type": "task.sync",
  "subject": "task:{taskId}",
  "time": "ISO 8601 timestamp",
  "correlationId": "request-correlation-id",
  "data": {
    "taskId": "string",
    "userId": "string",
    "action": "created|updated|completed|deleted",
    "syncData": {
      // Data needed for real-time UI updates
    },
    "timestamp": "ISO 8601"
  }
}
```

## Data Transformations

### From Database to Event
- Extract relevant fields from database models
- Format timestamps to ISO 8601
- Add correlation and event IDs
- Include user context for authorization validation

### From Event to Database (for consumers)
- Validate event schema and signatures
- Extract user_id for authorization
- Apply business logic before database updates
- Publish confirmation events

## Event Correlation and Tracing

### Correlation ID Strategy
- Generated at the API gateway level
- Propagated through all services
- Included in all logs and events
- Used for debugging and tracing

### Event Versioning
- Version field in event schema
- Backward compatibility maintained
- Migration strategies for schema changes
- Consumer groups for different versions during transition