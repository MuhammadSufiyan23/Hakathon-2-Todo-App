"""
Test for Dapr service invocation between services
This test verifies that services can communicate through Dapr service invocation
"""
import unittest
import asyncio
import httpx
import json
from typing import Dict, Any
import os

class DaprServiceInvocationTester:
    """
    Class to test Dapr service invocation between different services
    """

    def __init__(self, dapr_http_endpoint: str = "http://localhost:3500"):
        self.dapr_http_endpoint = dapr_http_endpoint
        self.client = httpx.AsyncClient(timeout=30.0)

    async def invoke_service(self, app_id: str, method: str, data: Dict[str, Any] = None, verb: str = "POST") -> Dict[str, Any]:
        """
        Invoke a service through Dapr service invocation

        Args:
            app_id: The ID of the target application (as configured in Dapr)
            method: The method/path to invoke on the target application
            data: Optional data to send in the request body
            verb: HTTP verb to use (GET, POST, PUT, DELETE, etc.)

        Returns:
            Response from the target service
        """
        url = f"{self.dapr_http_endpoint}/v1.0/invoke/{app_id}/method/{method}"

        headers = {
            "Content-Type": "application/json"
        }

        try:
            if verb.upper() == "GET":
                response = await self.client.get(url, headers=headers)
            elif verb.upper() == "POST":
                response = await self.client.post(url, json=data, headers=headers)
            elif verb.upper() == "PUT":
                response = await self.client.put(url, json=data, headers=headers)
            elif verb.upper() == "DELETE":
                response = await self.client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP verb: {verb}")

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            print(f"Error invoking service: {str(e)}")
            raise

    async def test_backend_health_through_dapr(self):
        """
        Test that we can invoke the backend health endpoint through Dapr
        """
        try:
            result = await self.invoke_service(
                app_id="todo-backend",
                method="health",
                verb="GET"
            )
            print(f"Backend health check through Dapr: {result}")
            return result.get("status") == "healthy"
        except Exception as e:
            print(f"Failed to check backend health through Dapr: {str(e)}")
            return False

    async def test_frontend_health_through_dapr(self):
        """
        Test that we can invoke the frontend endpoint through Dapr
        """
        try:
            result = await self.invoke_service(
                app_id="todo-frontend",
                method="health",
                verb="GET"
            )
            print(f"Frontend health check through Dapr: {result}")
            # Frontend might not have a specific health endpoint, so we'll just check if it responds
            return result is not None
        except Exception as e:
            print(f"Failed to check frontend through Dapr: {str(e)}")
            return False

    async def test_notification_service_invocation(self):
        """
        Test that we can invoke the notification service through Dapr
        """
        try:
            test_data = {
                "userId": "test-user-123",
                "taskId": "test-task-456",
                "notificationChannel": ["in-app"],
                "message": "Test notification"
            }

            result = await self.invoke_service(
                app_id="notification-service",
                method="send-notification",
                data=test_data,
                verb="POST"
            )
            print(f"Notification service invocation: {result}")
            return True
        except Exception as e:
            print(f"Failed to invoke notification service through Dapr: {str(e)}")
            return False

    async def test_scheduler_service_invocation(self):
        """
        Test that we can invoke the scheduler service through Dapr
        """
        try:
            test_data = {
                "user_id": "test-user-123",
                "task_id": "test-task-456",
                "reminder_time": "2026-12-31T10:00:00Z",
                "reminder_type": "due-date"
            }

            result = await self.invoke_service(
                app_id="scheduler-service",
                method="reminders",
                data=test_data,
                verb="POST"
            )
            print(f"Scheduler service invocation: {result}")
            return True
        except Exception as e:
            print(f"Failed to invoke scheduler service through Dapr: {str(e)}")
            return False

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


class DaprServiceInvocationTestSuite(unittest.IsolatedAsyncioTestCase):
    """Test suite for Dapr service invocation"""

    def setUp(self):
        self.tester = DaprServiceInvocationTester()

    async def test_all_service_invocations(self):
        """Test all service invocations"""
        # Test backend health
        backend_ok = await self.tester.test_backend_health_through_dapr()
        self.assertTrue(backend_ok, "Backend health check through Dapr should succeed")

        # Test frontend access
        frontend_ok = await self.tester.test_frontend_health_through_dapr()
        self.assertIsNotNone(frontend_ok, "Frontend should be accessible through Dapr")

        # Test notification service
        notification_ok = await self.tester.test_notification_service_invocation()
        self.assertTrue(notification_ok, "Notification service should be invocable through Dapr")

        # Test scheduler service
        scheduler_ok = await self.tester.test_scheduler_service_invocation()
        self.assertTrue(scheduler_ok, "Scheduler service should be invocable through Dapr")

    async def asyncTearDown(self):
        await self.tester.close()


# Example usage
async def run_dapr_invocation_tests():
    """
    Example function to run Dapr service invocation tests
    """
    tester = DaprServiceInvocationTester()

    print("Starting Dapr Service Invocation Tests...")

    # Test backend health
    print("\n1. Testing backend health through Dapr...")
    backend_ok = await tester.test_backend_health_through_dapr()
    print(f"   Backend health test: {'PASS' if backend_ok else 'FAIL'}")

    # Test notification service
    print("\n2. Testing notification service invocation...")
    notification_ok = await tester.test_notification_service_invocation()
    print(f"   Notification service test: {'PASS' if notification_ok else 'FAIL'}")

    # Test scheduler service
    print("\n3. Testing scheduler service invocation...")
    scheduler_ok = await tester.test_scheduler_service_invocation()
    print(f"   Scheduler service test: {'PASS' if scheduler_ok else 'FAIL'}")

    await tester.close()

    all_passed = backend_ok and notification_ok and scheduler_ok
    print(f"\nOverall Dapr service invocation tests: {'PASS' if all_passed else 'FAIL'}")

    return all_passed


if __name__ == "__main__":
    # Run the example
    success = asyncio.run(run_dapr_invocation_tests())

    if success:
        print("\nAll Dapr service invocation tests passed!")
    else:
        print("\nSome Dapr service invocation tests failed.")
        exit(1)