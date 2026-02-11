"""
Event schema validation for task operations
This module defines and validates event schemas for task operations
"""
from pydantic import BaseModel, ValidationError, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
import json

# Event data models
class TaskData(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    status: str  # pending, in-progress, completed
    priority: str  # low, medium, high
    due_date: Optional[str] = None
    created_at: str
    updated_at: str
    tags: Optional[List[str]] = []
    recurrence_pattern: Optional[str] = None

class TaskEventData(BaseModel):
    taskId: str
    userId: str
    operation: str  # create, update, complete, delete
    taskData: Optional[TaskData] = None
    updates: Optional[Dict[str, Any]] = None
    previous_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    completed_at: Optional[str] = None
    deleted_at: Optional[str] = None
    timestamp: str

class ReminderEventData(BaseModel):
    taskId: str
    userId: str
    reminderType: str  # due-date, custom, recurring
    dueTime: str
    notificationChannel: str  # email, in-app, push
    taskTitle: str
    timestamp: str

class TaskUpdateEventData(BaseModel):
    taskId: str
    userId: str
    action: str  # created, updated, completed, deleted
    syncData: Optional[Dict[str, Any]] = None
    timestamp: str

# Main event model
class Event(BaseModel):
    eventId: str
    source: str
    type: str  # task.created, task.updated, task.completed, task.deleted, reminder.due, reminder.created, task.sync
    subject: str
    time: str
    correlationId: Optional[str] = None
    data: Dict[str, Any]

class EventValidator:
    """Class to validate different types of events"""

    @staticmethod
    def validate_task_created_event(event: Event) -> bool:
        """Validate task.created event"""
        if event.type != "task.created":
            return False

        try:
            # Validate the data structure
            task_data = TaskEventData(**event.data)

            # Additional validation
            if task_data.operation != "create":
                raise ValueError("Operation must be 'create' for task.created event")

            if not task_data.taskData:
                raise ValueError("taskData is required for task.created event")

            return True
        except ValidationError as ve:
            print(f"Validation error: {ve}")
            return False
        except Exception as e:
            print(f"Error validating task.created event: {e}")
            return False

    @staticmethod
    def validate_task_updated_event(event: Event) -> bool:
        """Validate task.updated event"""
        if event.type != "task.updated":
            return False

        try:
            # Validate the data structure
            task_data = TaskEventData(**event.data)

            # Additional validation
            if task_data.operation != "update":
                raise ValueError("Operation must be 'update' for task.updated event")

            if not task_data.updates:
                raise ValueError("updates field is required for task.updated event")

            return True
        except ValidationError as ve:
            print(f"Validation error: {ve}")
            return False
        except Exception as e:
            print(f"Error validating task.updated event: {e}")
            return False

    @staticmethod
    def validate_task_completed_event(event: Event) -> bool:
        """Validate task.completed event"""
        if event.type != "task.completed":
            return False

        try:
            # Validate the data structure
            task_data = TaskEventData(**event.data)

            # Additional validation
            if task_data.operation != "complete":
                raise ValueError("Operation must be 'complete' for task.completed event")

            if not task_data.completed_at:
                raise ValueError("completed_at field is required for task.completed event")

            return True
        except ValidationError as ve:
            print(f"Validation error: {ve}")
            return False
        except Exception as e:
            print(f"Error validating task.completed event: {e}")
            return False

    @staticmethod
    def validate_task_deleted_event(event: Event) -> bool:
        """Validate task.deleted event"""
        if event.type != "task.deleted":
            return False

        try:
            # Validate the data structure
            task_data = TaskEventData(**event.data)

            # Additional validation
            if task_data.operation != "delete":
                raise ValueError("Operation must be 'delete' for task.deleted event")

            if not task_data.deleted_at:
                raise ValueError("deleted_at field is required for task.deleted event")

            return True
        except ValidationError as ve:
            print(f"Validation error: {ve}")
            return False
        except Exception as e:
            print(f"Error validating task.deleted event: {e}")
            return False

    @staticmethod
    def validate_reminder_due_event(event: Event) -> bool:
        """Validate reminder.due event"""
        if event.type != "reminder.due":
            return False

        try:
            # Validate the data structure
            reminder_data = ReminderEventData(**event.data)

            # Additional validation
            if reminder_data.reminderType not in ["due-date", "custom"]:
                raise ValueError("Invalid reminderType")

            if reminder_data.notificationChannel not in ["email", "in-app", "push"]:
                raise ValueError("Invalid notificationChannel")

            return True
        except ValidationError as ve:
            print(f"Validation error: {ve}")
            return False
        except Exception as e:
            print(f"Error validating reminder.due event: {e}")
            return False

    @staticmethod
    def validate_task_sync_event(event: Event) -> bool:
        """Validate task.sync event"""
        if event.type != "task.sync":
            return False

        try:
            # Validate the data structure
            sync_data = TaskUpdateEventData(**event.data)

            # Additional validation
            if sync_data.action not in ["created", "updated", "completed", "deleted"]:
                raise ValueError("Invalid action for task.sync event")

            return True
        except ValidationError as ve:
            print(f"Validation error: {ve}")
            return False
        except Exception as e:
            print(f"Error validating task.sync event: {e}")
            return False

    @staticmethod
    def validate_event_schema(event_json: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate an event against the general schema and specific type"""
        try:
            # First validate the general event structure
            event = Event(**event_json)

            # Then validate the specific event type
            validator_map = {
                "task.created": EventValidator.validate_task_created_event,
                "task.updated": EventValidator.validate_task_updated_event,
                "task.completed": EventValidator.validate_task_completed_event,
                "task.deleted": EventValidator.validate_task_deleted_event,
                "reminder.due": EventValidator.validate_reminder_due_event,
                "task.sync": EventValidator.validate_task_sync_event,
            }

            if event.type in validator_map:
                is_valid = validator_map[event.type](event)
                if not is_valid:
                    return False, f"Validation failed for event type: {event.type}"
            else:
                return False, f"Unknown event type: {event.type}"

            return True, None

        except ValidationError as ve:
            error_msg = f"General event validation failed: {ve}"
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error during validation: {e}"
            return False, error_msg

    @staticmethod
    def create_event(event_type: str, source: str, subject: str, data: Dict[str, Any], correlation_id: Optional[str] = None) -> Event:
        """Helper method to create a properly formatted event"""
        event_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + "Z"

        event = Event(
            eventId=event_id,
            source=source,
            type=event_type,
            subject=subject,
            time=timestamp,
            correlationId=correlation_id,
            data=data
        )

        return event

    @staticmethod
    def validate_idempotency(event: Event, processed_events: set) -> bool:
        """Validate event idempotency by checking if event has been processed before"""
        if event.eventId in processed_events:
            return False  # Event already processed
        return True

# Example usage
if __name__ == "__main__":
    # Example of creating and validating an event
    sample_data = {
        "taskId": "123",
        "userId": "user456",
        "operation": "create",
        "taskData": {
            "id": "123",
            "user_id": "user456",
            "title": "Sample task",
            "status": "pending",
            "priority": "medium",
            "created_at": "2026-02-09T10:00:00Z",
            "updated_at": "2026-02-09T10:00:00Z"
        },
        "timestamp": "2026-02-09T10:00:00Z"
    }

    # Create an event
    event = EventValidator.create_event(
        event_type="task.created",
        source="/services/backend",
        subject="task:123",
        data=sample_data
    )

    # Validate the event
    is_valid, error_msg = EventValidator.validate_event_schema(event.dict())

    print(f"Event is valid: {is_valid}")
    if error_msg:
        print(f"Error: {error_msg}")

    # Print the event
    print(json.dumps(event.dict(), indent=2))