from datetime import datetime, timezone
from typing import Optional
import json
import logging

logger = logging.getLogger("activity-service")

class ActivityService:
    """
    Service for logging user activities and task operations.
    Provides async activity logging for audit trail functionality.
    """

    async def log_activity(
        self,
        user_id: str,
        action: str,
        task_id: Optional[str] = None,
        details: Optional[dict] = None
    ):
        """
        Log an activity asynchronously.

        Args:
            user_id: ID of the user performing the action
            action: Type of action (e.g., 'task_created', 'task_completed')
            task_id: Optional task ID if action is task-related
            details: Optional dictionary with additional details (will be JSON serialized)

        Note: This is a placeholder implementation for Phase III-IV.
        In production, this should use FastAPI BackgroundTasks and write to the database.
        """
        try:
            # Serialize details to JSON if provided
            details_json = json.dumps(details) if details else None

            # Log to console for Phase III-IV (database write will be added when routes are implemented)
            log_message = f"[ACTIVITY] user={user_id} action={action}"
            if task_id:
                log_message += f" task_id={task_id}"
            if details_json:
                log_message += f" details={details_json}"

            logger.info(log_message)

            # TODO: In actual implementation with routes, this will:
            # 1. Create ActivityLog entry in database
            # 2. Use FastAPI BackgroundTasks for async write
            # 3. Handle errors gracefully without blocking main request

        except Exception as e:
            # Activity logging should never break the main operation
            logger.error(f"Failed to log activity: {e}")

    async def get_task_activity(self, task_id: str, user_id: str, limit: int = 50):
        """
        Retrieve activity logs for a specific task.

        Args:
            task_id: ID of the task
            user_id: ID of the user (for authorization)
            limit: Maximum number of logs to return

        Returns:
            List of activity log entries

        Note: Placeholder for Phase III-IV. Will query activity_logs table.
        """
        # TODO: Implement database query when routes are added
        logger.info(f"Fetching activity logs for task {task_id}")
        return []

    async def get_user_activity(self, user_id: str, limit: int = 100):
        """
        Retrieve recent activity logs for a user.

        Args:
            user_id: ID of the user
            limit: Maximum number of logs to return

        Returns:
            List of activity log entries

        Note: Placeholder for Phase III-IV. Will query activity_logs table.
        """
        # TODO: Implement database query when routes are added
        logger.info(f"Fetching activity logs for user {user_id}")
        return []
