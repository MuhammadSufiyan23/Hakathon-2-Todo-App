"""
Notification service for consuming reminder events and sending notifications
This service would be deployed as a separate microservice in the workers namespace
"""
from fastapi import FastAPI, BackgroundTasks
import asyncio
import json
import logging
from typing import Dict, Any
from datetime import datetime
import httpx
import os

app = FastAPI(title="Notification Service")

# Mock notification providers
class EmailProvider:
    async def send(self, recipient: str, subject: str, body: str):
        print(f"EMAIL SENT to {recipient}: {subject}")
        # In real implementation, would use SMTP or email service API
        return {"status": "sent", "provider": "email"}

class InAppProvider:
    async def send(self, user_id: str, message: str):
        print(f"IN-APP NOTIFICATION for {user_id}: {message}")
        # In real implementation, would use WebSocket or push notification service
        return {"status": "delivered", "provider": "in-app"}

class PushProvider:
    async def send(self, device_token: str, message: str):
        print(f"PUSH NOTIFICATION to {device_token}: {message}")
        # In real implementation, would use Firebase or similar push service
        return {"status": "sent", "provider": "push"}

class NotificationService:
    def __init__(self):
        self.email_provider = EmailProvider()
        self.in_app_provider = InAppProvider()
        self.push_provider = PushProvider()

    async def send_notification(self, notification_data: Dict[str, Any]):
        """Process notification request and send through appropriate channels"""
        user_id = notification_data.get("userId")
        task_title = notification_data.get("taskTitle", "")
        reminder_time = notification_data.get("dueTime", "")
        channels = notification_data.get("notificationChannel", ["in-app"])

        results = {}

        for channel in channels:
            try:
                if channel == "email":
                    result = await self.email_provider.send(
                        f"{user_id}@example.com",  # In real app, would fetch from user profile
                        f"Reminder: {task_title}",
                        f"Your task '{task_title}' is due at {reminder_time}"
                    )
                elif channel == "in-app":
                    result = await self.in_app_provider.send(
                        user_id,
                        f"Task '{task_title}' is due at {reminder_time}"
                    )
                elif channel == "push":
                    # In real app, would fetch device token from user profile
                    result = await self.push_provider.send(
                        f"device_{user_id}",
                        f"Task '{task_title}' is due!"
                    )
                else:
                    result = {"status": "skipped", "reason": f"Unknown channel: {channel}"}

                results[channel] = result

            except Exception as e:
                logging.error(f"Failed to send notification via {channel}: {str(e)}")
                results[channel] = {"status": "failed", "error": str(e)}

        return results

# Global notification service instance
notification_service = NotificationService()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "notification-service"
    }

@app.post("/process-reminder")
async def process_reminder_event(event_data: Dict[str, Any]):
    """
    Process reminder event from Kafka topic
    This would be called by the Dapr pubsub subscription
    """
    try:
        # Log the received event
        logging.info(f"Processing reminder event: {json.dumps(event_data)}")

        # Extract notification data from event
        event_details = event_data.get("data", {})

        # Send notification
        results = await notification_service.send_notification(event_details)

        return {
            "status": "processed",
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logging.error(f"Error processing reminder event: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/stats")
async def get_stats():
    """Get notification service statistics"""
    # In real implementation, would track metrics
    return {
        "total_notifications_sent": 0,
        "delivery_success_rate": 0.0,
        "last_processed": datetime.utcnow().isoformat()
    }

# Example of how to subscribe to Dapr pubsub
@app.get("/dapr/subscribe")
async def dapr_subscribe():
    """Dapr pubsub subscription endpoint"""
    return [
        {
            "pubsubname": "reminder-pubsub",  # This should match the Dapr component name
            "topic": "reminders",
            "route": "/process-reminder"
        }
    ]

# Example of how to use in main application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)