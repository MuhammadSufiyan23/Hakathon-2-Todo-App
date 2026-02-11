"""
Scheduler service for handling reminders and scheduled tasks
This service would be deployed as a separate microservice in the workers namespace
"""
from fastapi import FastAPI, BackgroundTasks, HTTPException
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlmodel import SQLModel, Field, create_engine, Session, select
from pydantic import BaseModel
import httpx
import uuid

app = FastAPI(title="Scheduler Service")

# Pydantic models for request/response
class ReminderCreate(BaseModel):
    user_id: str
    task_id: str
    reminder_time: str
    reminder_type: str = "due-date"
    notification_channels: List[str] = ["in-app"]
    description: Optional[str] = None

class ReminderResponse(BaseModel):
    id: str
    user_id: str
    task_id: str
    reminder_time: str
    status: str
    reminder_type: str
    notification_channels: List[str]
    created_at: str

class ReminderUpdate(BaseModel):
    reminder_time: Optional[str] = None
    status: Optional[str] = None
    notification_channels: Optional[List[str]] = None

# Mock storage for reminders
reminders_storage: Dict[str, Dict[str, Any]] = {}

class ReminderScheduler:
    def __init__(self):
        self.active_schedules = {}

    async def schedule_reminder(self, reminder_id: str, reminder_time: str, user_id: str, task_id: str):
        """Schedule a reminder to be triggered at the specified time"""
        try:
            # Convert string time to datetime
            reminder_dt = datetime.fromisoformat(reminder_time.replace('Z', '+00:00'))

            # Calculate delay in seconds
            delay_seconds = (reminder_dt - datetime.now(reminder_dt.tzinfo)).total_seconds()

            if delay_seconds <= 0:
                # If time is in the past, trigger immediately
                await self.trigger_reminder(reminder_id, user_id, task_id)
                return

            # Schedule the reminder
            task = asyncio.create_task(self._delayed_trigger(reminder_id, delay_seconds, user_id, task_id))
            self.active_schedules[reminder_id] = task

            logging.info(f"Scheduled reminder {reminder_id} for {reminder_time}")

        except Exception as e:
            logging.error(f"Error scheduling reminder {reminder_id}: {str(e)}")

    async def _delayed_trigger(self, reminder_id: str, delay_seconds: float, user_id: str, task_id: str):
        """Internal method to delay and trigger a reminder"""
        await asyncio.sleep(delay_seconds)
        await self.trigger_reminder(reminder_id, user_id, task_id)

        # Remove from active schedules
        if reminder_id in self.active_schedules:
            del self.active_schedules[reminder_id]

    async def trigger_reminder(self, reminder_id: str, user_id: str, task_id: str):
        """Trigger a reminder and publish to notification service"""
        try:
            # Get reminder details from storage
            if reminder_id not in reminders_storage:
                logging.warning(f"Reminder {reminder_id} not found in storage")
                return

            reminder = reminders_storage[reminder_id]

            # Create event to send to notification service
            reminder_event = {
                "eventId": f"reminder-trigger-{uuid.uuid4()}",
                "source": "/services/scheduler",
                "type": "reminder.due",
                "subject": f"reminder:{reminder_id}",
                "time": datetime.utcnow().isoformat() + "Z",
                "correlationId": reminder_id,
                "data": {
                    "taskId": task_id,
                    "userId": user_id,
                    "reminderType": reminder.get("reminder_type", "due-date"),
                    "dueTime": reminder["reminder_time"],
                    "notificationChannel": reminder.get("notification_channels", ["in-app"]),
                    "taskTitle": f"Task {task_id}",  # In real app, would fetch from task service
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            }

            # In real implementation, this would publish to Dapr pubsub
            # For now, we'll just log it
            logging.info(f"Triggered reminder {reminder_id} for user {user_id}")
            logging.info(f"Event to publish: {json.dumps(reminder_event)}")

        except Exception as e:
            logging.error(f"Error triggering reminder {reminder_id}: {str(e)}")

    async def cancel_reminder(self, reminder_id: str):
        """Cancel a scheduled reminder"""
        if reminder_id in self.active_schedules:
            task = self.active_schedules[reminder_id]
            task.cancel()
            del self.active_schedules[reminder_id]
            logging.info(f"Cancelled reminder {reminder_id}")

# Global scheduler instance
scheduler = ReminderScheduler()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "scheduler-service",
        "active_schedules": len(scheduler.active_schedules)
    }

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    return {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "scheduler-service"
    }

@app.post("/reminders", response_model=ReminderResponse)
async def create_reminder(reminder: ReminderCreate):
    """Create a new reminder"""
    try:
        reminder_id = str(uuid.uuid4())

        reminder_record = {
            "id": reminder_id,
            "user_id": reminder.user_id,
            "task_id": reminder.task_id,
            "reminder_time": reminder.reminder_time,
            "status": "pending",
            "reminder_type": reminder.reminder_type,
            "notification_channels": reminder.notification_channels,
            "description": reminder.description,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }

        # Store the reminder
        reminders_storage[reminder_id] = reminder_record

        # Schedule the reminder
        await scheduler.schedule_reminder(
            reminder_id,
            reminder.reminder_time,
            reminder.user_id,
            reminder.task_id
        )

        return ReminderResponse(**reminder_record)

    except Exception as e:
        logging.error(f"Error creating reminder: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reminders/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(reminder_id: str):
    """Get a specific reminder"""
    if reminder_id not in reminders_storage:
        raise HTTPException(status_code=404, detail="Reminder not found")

    return ReminderResponse(**reminders_storage[reminder_id])

@app.put("/reminders/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(reminder_id: str, reminder_update: ReminderUpdate):
    """Update a specific reminder"""
    if reminder_id not in reminders_storage:
        raise HTTPException(status_code=404, detail="Reminder not found")

    reminder = reminders_storage[reminder_id]

    # Update fields if provided
    if reminder_update.reminder_time:
        reminder["reminder_time"] = reminder_update.reminder_time
        # Reschedule if time changed
        await scheduler.cancel_reminder(reminder_id)
        await scheduler.schedule_reminder(
            reminder_id,
            reminder_update.reminder_time,
            reminder["user_id"],
            reminder["task_id"]
        )

    if reminder_update.status:
        reminder["status"] = reminder_update.status

    if reminder_update.notification_channels:
        reminder["notification_channels"] = reminder_update.notification_channels

    return ReminderResponse(**reminder)

@app.delete("/reminders/{reminder_id}")
async def delete_reminder(reminder_id: str):
    """Delete/cancel a reminder"""
    if reminder_id not in reminders_storage:
        raise HTTPException(status_code=404, detail="Reminder not found")

    # Cancel the scheduled task if it exists
    await scheduler.cancel_reminder(reminder_id)

    # Remove from storage
    del reminders_storage[reminder_id]

    return {"status": "cancelled", "reminder_id": reminder_id}

@app.get("/reminders")
async def list_reminders(user_id: str = None):
    """List reminders for a user"""
    user_reminders = []

    for reminder in reminders_storage.values():
        if user_id is None or reminder["user_id"] == user_id:
            user_reminders.append(ReminderResponse(**reminder))

    return {"reminders": user_reminders, "total": len(user_reminders)}

@app.post("/reminders/{reminder_id}/trigger")
async def manual_trigger_reminder(reminder_id: str):
    """Manually trigger a reminder"""
    if reminder_id not in reminders_storage:
        raise HTTPException(status_code=404, detail="Reminder not found")

    reminder = reminders_storage[reminder_id]

    # Cancel existing schedule
    await scheduler.cancel_reminder(reminder_id)

    # Trigger immediately
    await scheduler.trigger_reminder(reminder_id, reminder["user_id"], reminder["task_id"])

    # Update status
    reminder["status"] = "triggered"
    reminder["triggered_at"] = datetime.utcnow().isoformat() + "Z"

    return {
        "status": "triggered",
        "reminder_id": reminder_id,
        "triggered_at": reminder["triggered_at"]
    }

# Example of how to subscribe to task-update events from Dapr pubsub
@app.get("/dapr/subscribe")
async def dapr_subscribe():
    """Dapr pubsub subscription endpoint"""
    return [
        {
            "pubsubname": "task-update-pubsub",  # This should match the Dapr component name
            "topic": "task-updates",
            "route": "/process-task-update"
        }
    ]

@app.post("/process-task-update")
async def process_task_update_event(event_data: Dict[str, Any]):
    """
    Process task update event from Kafka topic
    This would be called by the Dapr pubsub subscription
    """
    try:
        # Log the received event
        logging.info(f"Processing task update event: {json.dumps(event_data)}")

        # Extract task update data from event
        event_details = event_data.get("data", {})
        action = event_details.get("action")
        task_id = event_details.get("taskId")
        user_id = event_details.get("userId")

        # Handle different types of task updates
        if action == "created":
            # Check if the task has a due date and create a reminder
            due_date = event_details.get("due_date")
            if due_date:
                reminder = ReminderCreate(
                    user_id=user_id,
                    task_id=task_id,
                    reminder_time=due_date,
                    reminder_type="due-date",
                    notification_channels=["in-app"]
                )
                # In real implementation, this would create a reminder
                logging.info(f"Created reminder for new task {task_id}")

        elif action == "updated":
            # Check if due date was updated and update reminders accordingly
            updates = event_details.get("updates", {})
            if "due_date" in updates:
                # Would need to find and update existing reminder
                logging.info(f"Updated reminder for task {task_id}")

        return {
            "status": "processed",
            "event_action": action,
            "task_id": task_id,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logging.error(f"Error processing task update event: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Example of how to use in main application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)