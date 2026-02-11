"""
Load testing script for monitoring stack
This script simulates load on the system to test monitoring capabilities
"""

import asyncio
import aiohttp
import time
import json
import random
from typing import Dict, List, Any
import uuid
from datetime import datetime, timedelta
import logging
import argparse


class MonitoringLoadTester:
    """
    Load tester for monitoring stack validation
    """

    def __init__(self, base_url: str = "http://localhost:8080", duration_minutes: int = 10):
        self.base_url = base_url.rstrip('/')
        self.duration_minutes = duration_minutes
        self.session = None
        self.results = {
            'requests': 0,
            'errors': 0,
            'response_times': [],
            'start_time': None,
            'end_time': None
        }
        self.users = [f"user_{i}" for i in range(1, 101)]  # 100 simulated users
        self.tasks = [f"task_{i}" for i in range(1, 1001)]  # 1000 sample tasks

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        self.results['start_time'] = datetime.now()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
        self.results['end_time'] = datetime.now()

    async def simulate_api_call(self, endpoint: str, method: str = 'GET', payload: Dict = None,
                              headers: Dict = None) -> Dict[str, Any]:
        """
        Simulate an API call to the backend
        """
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()

        try:
            correlation_id = str(uuid.uuid4())
            req_headers = {
                'X-Correlation-ID': correlation_id,
                'Content-Type': 'application/json'
            }

            if headers:
                req_headers.update(headers)

            async with self.session.request(method, url, json=payload, headers=req_headers) as response:
                response_time = time.time() - start_time
                response_text = await response.text()

                result = {
                    'status': response.status,
                    'response_time': response_time,
                    'correlation_id': correlation_id,
                    'endpoint': endpoint,
                    'method': method,
                    'success': 200 <= response.status < 300,
                    'response_body': response_text[:500]  # Limit response size
                }

                self.results['requests'] += 1
                self.results['response_times'].append(response_time)

                if not result['success']:
                    self.results['errors'] += 1
                    result['error_details'] = f"Status: {response.status}, Body: {response_text}"

                return result

        except Exception as e:
            response_time = time.time() - start_time
            self.results['requests'] += 1
            self.results['errors'] += 1
            self.results['response_times'].append(response_time)

            return {
                'status': 0,
                'response_time': response_time,
                'correlation_id': str(uuid.uuid4()),
                'endpoint': endpoint,
                'method': method,
                'success': False,
                'error_details': str(e)
            }

    async def simulate_user_activity(self, user_id: str):
        """
        Simulate a user performing various activities
        """
        activities = [
            self.simulate_get_tasks,
            self.simulate_add_task,
            self.simulate_update_task,
            self.simulate_complete_task,
            self.simulate_get_user_profile
        ]

        while True:
            activity = random.choice(activities)
            try:
                await activity(user_id)
            except Exception as e:
                print(f"Error in user activity for {user_id}: {e}")

            # Random delay between activities (1-5 seconds)
            await asyncio.sleep(random.uniform(1, 5))

    async def simulate_get_tasks(self, user_id: str):
        """Simulate getting tasks for a user"""
        await self.simulate_api_call(f"/api/users/{user_id}/tasks", "GET")

    async def simulate_add_task(self, user_id: str):
        """Simulate adding a new task"""
        task_data = {
            "title": f"Load test task {uuid.uuid4().hex[:8]}",
            "description": f"Task created during load testing by {user_id}",
            "status": "pending",
            "priority": random.choice(["low", "medium", "high"]),
            "due_date": (datetime.now() + timedelta(days=random.randint(1, 30))).isoformat(),
            "user_id": user_id
        }

        await self.simulate_api_call("/api/tasks", "POST", task_data)

    async def simulate_update_task(self, user_id: str):
        """Simulate updating a task"""
        task_id = random.choice(self.tasks)
        update_data = {
            "status": random.choice(["pending", "in-progress", "completed"]),
            "priority": random.choice(["low", "medium", "high"])
        }

        await self.simulate_api_call(f"/api/tasks/{task_id}", "PUT", update_data)

    async def simulate_complete_task(self, user_id: str):
        """Simulate completing a task"""
        task_id = random.choice(self.tasks)
        await self.simulate_api_call(f"/api/tasks/{task_id}/complete", "POST")

    async def simulate_get_user_profile(self, user_id: str):
        """Simulate getting user profile"""
        await self.simulate_api_call(f"/api/users/{user_id}", "GET")

    async def simulate_event_publishing(self):
        """Simulate event publishing for event-driven architecture"""
        event_types = [
            {"type": "task.created", "data": {"taskId": str(uuid.uuid4()), "userId": random.choice(self.users)}},
            {"type": "task.updated", "data": {"taskId": str(uuid.uuid4()), "userId": random.choice(self.users)}},
            {"type": "task.completed", "data": {"taskId": str(uuid.uuid4()), "userId": random.choice(self.users)}},
            {"type": "reminder.sent", "data": {"taskId": str(uuid.uuid4()), "userId": random.choice(self.users)}}
        ]

        event = random.choice(event_types)
        await self.simulate_api_call("/api/events", "POST", event)

    async def run_load_test(self, concurrent_users: int = 20):
        """
        Run the load test with specified number of concurrent users
        """
        print(f"Starting load test with {concurrent_users} concurrent users for {self.duration_minutes} minutes...")
        print(f"Target URL: {self.base_url}")

        # Create tasks for concurrent users
        user_tasks = []
        for i in range(concurrent_users):
            user_id = self.users[i]
            user_task = asyncio.create_task(self.simulate_user_activity(user_id))
            user_tasks.append(user_task)

        # Add some event publishing tasks
        event_tasks = []
        for i in range(5):  # 5 event publishing tasks
            event_task = asyncio.create_task(self.periodic_event_publishing())
            event_tasks.append(event_task)

        # Run for specified duration
        await asyncio.sleep(self.duration_minutes * 60)

        # Cancel all tasks
        for task in user_tasks:
            task.cancel()

        for task in event_tasks:
            task.cancel()

        # Wait for tasks to finish cancellation
        await asyncio.gather(*user_tasks, return_exceptions=True)
        await asyncio.gather(*event_tasks, return_exceptions=True)

    async def periodic_event_publishing(self):
        """Periodically publish events"""
        while True:
            await self.simulate_event_publishing()
            await asyncio.sleep(random.uniform(0.1, 2))  # Random interval between 0.1-2 seconds

    def print_results(self):
        """Print load test results"""
        duration = (self.results['end_time'] - self.results['start_time']).total_seconds()

        print("\n" + "="*60)
        print("LOAD TEST RESULTS")
        print("="*60)
        print(f"Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
        print(f"Total requests: {self.results['requests']}")
        print(f"Total errors: {self.results['errors']}")
        print(f"Success rate: {(1 - self.results['errors']/self.results['requests'])*100:.2f}%")

        if self.results['response_times']:
            avg_response_time = sum(self.results['response_times']) / len(self.results['response_times'])
            max_response_time = max(self.results['response_times'])
            min_response_time = min(self.results['response_times'])

            print(f"Average response time: {avg_response_time:.3f}s")
            print(f"Max response time: {max_response_time:.3f}s")
            print(f"Min response time: {min_response_time:.3f}s")
            print(f"Requests per second: {self.results['requests']/duration:.2f}")

        print("="*60)

    async def test_monitoring_metrics(self):
        """
        Test that monitoring metrics are being collected properly
        """
        print("\nTesting monitoring metrics collection...")

        # Test Prometheus endpoint
        try:
            async with self.session.get(f"{self.base_url.replace(':8080', ':9090')}/api/v1/targets") as response:
                if response.status == 200:
                    print("✓ Prometheus endpoint accessible")
                else:
                    print(f"✗ Prometheus endpoint returned status {response.status}")
        except Exception as e:
            print(f"✗ Prometheus endpoint error: {e}")

        # Test that our simulated traffic is generating metrics
        await asyncio.sleep(2)  # Allow metrics to be collected

        # Test for specific metrics existence
        try:
            async with self.session.get(f"{self.base_url.replace(':8080', ':9090')}/api/v1/query?query=up") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'success':
                        print("✓ Prometheus query API working")
                    else:
                        print("✗ Prometheus query API returned error")
                else:
                    print(f"✗ Prometheus query API returned status {response.status}")
        except Exception as e:
            print(f"✗ Prometheus query API error: {e}")


async def main():
    parser = argparse.ArgumentParser(description='Load test monitoring stack')
    parser.add_argument('--url', default='http://localhost:8080', help='Base URL for the application')
    parser.add_argument('--duration', type=int, default=5, help='Duration of test in minutes')
    parser.add_argument('--users', type=int, default=10, help='Number of concurrent users')

    args = parser.parse_args()

    async with MonitoringLoadTester(args.url, args.duration) as tester:
        print(f"Starting monitoring stack load test...")
        print(f"Target: {args.url}")
        print(f"Duration: {args.duration} minutes")
        print(f"Concurrent users: {args.users}")

        # Start the load test
        load_test_task = asyncio.create_task(tester.run_load_test(args.users))

        # Periodically check monitoring metrics during the test
        async def monitor_metrics():
            while not load_test_task.done():
                await tester.test_monitoring_metrics()
                await asyncio.sleep(30)  # Check every 30 seconds

        monitor_task = asyncio.create_task(monitor_metrics())

        # Wait for load test to complete
        await load_test_task
        monitor_task.cancel()

        # Print final results
        tester.print_results()

        # Final metrics check
        await tester.test_monitoring_metrics()


if __name__ == "__main__":
    asyncio.run(main())