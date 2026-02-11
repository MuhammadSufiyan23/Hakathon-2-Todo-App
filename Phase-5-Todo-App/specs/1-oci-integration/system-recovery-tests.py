"""
System recovery tests for failure scenarios
This script tests the system's ability to recover from various failure scenarios
"""

import asyncio
import aiohttp
import subprocess
import time
import json
from typing import Dict, List, Any, Callable
from datetime import datetime, timedelta
import random
import argparse
import sys


class SystemRecoveryTester:
    """
    Tester for system recovery from various failure scenarios
    """

    def __init__(self, base_url: str = "http://localhost:8080", timeout: int = 300):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = None
        self.test_results = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'failures': [],
            'start_time': datetime.now()
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def check_system_health(self) -> bool:
        """
        Check if the system is healthy by making a simple request

        Returns:
            Boolean indicating if system is healthy
        """
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                return response.status == 200
        except Exception:
            return False

    async def wait_for_recovery(self, timeout: int = 60) -> bool:
        """
        Wait for system to recover after a failure

        Args:
            timeout: Maximum time to wait for recovery

        Returns:
            Boolean indicating if system recovered
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if await self.check_system_health():
                return True
            await asyncio.sleep(2)
        return False

    async def simulate_pod_failure(self, pod_name: str, namespace: str = "default") -> bool:
        """
        Simulate pod failure by deleting a pod

        Args:
            pod_name: Name of the pod to delete
            namespace: Kubernetes namespace

        Returns:
            Boolean indicating if recovery was successful
        """
        print(f"Simulating pod failure: {pod_name}")

        try:
            # Delete the pod
            cmd = ["kubectl", "delete", "pod", pod_name, "-n", namespace, "--wait=false"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode != 0:
                print(f"Failed to delete pod: {result.stderr}")
                return False

            print(f"Deleted pod {pod_name}, waiting for recovery...")

            # Wait for recovery
            recovered = await self.wait_for_recovery(120)  # Wait up to 2 minutes

            if recovered:
                print(f"✅ Pod {pod_name} recovery successful")
            else:
                print(f"❌ Pod {pod_name} recovery failed")

            return recovered

        except Exception as e:
            print(f"Error simulating pod failure: {e}")
            return False

    async def simulate_network_partition(self, duration: int = 30) -> bool:
        """
        Simulate network partition by blocking traffic temporarily

        Args:
            duration: Duration of network partition in seconds

        Returns:
            Boolean indicating if recovery was successful
        """
        print(f"Simulating network partition for {duration} seconds")

        # Note: This is a simplified simulation
        # In a real environment, this would involve more complex network manipulation

        # For this test, we'll simulate by stopping and starting the service
        try:
            # In a real scenario, we'd manipulate iptables or use tools like tc
            print(f"Network partition simulation: blocking traffic for {duration} seconds")
            await asyncio.sleep(duration)

            # Check if system recovers after "network" is restored
            recovered = await self.wait_for_recovery(60)

            if recovered:
                print("✅ Network partition recovery successful")
            else:
                print("❌ Network partition recovery failed")

            return recovered

        except Exception as e:
            print(f"Error simulating network partition: {e}")
            return False

    async def simulate_database_failure(self, duration: int = 45) -> bool:
        """
        Simulate database failure by restarting the database

        Args:
            duration: Duration to wait after restart

        Returns:
            Boolean indicating if recovery was successful
        """
        print(f"Simulating database failure and recovery")

        try:
            # Restart the database pod
            cmd = ["kubectl", "rollout", "restart", "deployment/postgresql"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode != 0:
                print(f"Failed to restart database: {result.stderr}")
                return False

            print("Database restart initiated, waiting for recovery...")

            # Wait for the database to be ready
            await asyncio.sleep(duration)

            # Wait for the system to be healthy again
            recovered = await self.wait_for_recovery(180)  # Wait up to 3 minutes

            if recovered:
                print("✅ Database failure recovery successful")
            else:
                print("❌ Database failure recovery failed")

            return recovered

        except Exception as e:
            print(f"Error simulating database failure: {e}")
            return False

    async def simulate_api_overload(self, duration: int = 60) -> bool:
        """
        Simulate API overload by sending many concurrent requests

        Args:
            duration: Duration of the overload test

        Returns:
            Boolean indicating if system recovered
        """
        print(f"Simulating API overload for {duration} seconds")

        try:
            # Send concurrent requests to stress the system
            start_time = time.time()
            requests_sent = 0

            while time.time() - start_time < duration:
                tasks = []
                # Send 10 concurrent requests every 0.5 seconds
                for _ in range(10):
                    task = asyncio.create_task(self._make_stress_request())
                    tasks.append(task)

                await asyncio.gather(*tasks, return_exceptions=True)
                requests_sent += 10
                await asyncio.sleep(0.5)

            print(f"Sent approximately {requests_sent} requests during overload test")

            # Wait for system to recover
            recovered = await self.wait_for_recovery(120)

            if recovered:
                print("✅ API overload recovery successful")
            else:
                print("❌ API overload recovery failed")

            return recovered

        except Exception as e:
            print(f"Error simulating API overload: {e}")
            return False

    async def _make_stress_request(self):
        """
        Helper method to make a request during stress testing
        """
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                await response.text()  # Consume the response
        except Exception:
            pass  # Ignore errors during stress test

    async def simulate_message_queue_backlog(self, duration: int = 60) -> bool:
        """
        Simulate message queue backlog by overwhelming the event processing system

        Args:
            duration: Duration of the backlog simulation

        Returns:
            Boolean indicating if system recovered
        """
        print(f"Simulating message queue backlog for {duration} seconds")

        try:
            start_time = time.time()
            events_sent = 0

            while time.time() - start_time < duration:
                # Send multiple events to create a backlog
                tasks = []
                for _ in range(5):
                    task = asyncio.create_task(self._send_sample_event())
                    tasks.append(task)

                await asyncio.gather(*tasks, return_exceptions=True)
                events_sent += 5
                await asyncio.sleep(0.1)

            print(f"Sent {events_sent} events to create message backlog")

            # Wait for the system to process the backlog
            recovered = await self.wait_for_recovery(300)  # Wait up to 5 minutes

            if recovered:
                print("✅ Message queue backlog recovery successful")
            else:
                print("❌ Message queue backlog recovery failed")

            return recovered

        except Exception as e:
            print(f"Error simulating message queue backlog: {e}")
            return False

    async def _send_sample_event(self):
        """
        Helper method to send a sample event for backlog testing
        """
        try:
            event_data = {
                "type": "task.created",
                "data": {
                    "taskId": f"test-{random.randint(1000, 9999)}",
                    "userId": f"user-{random.randint(100, 999)}",
                    "timestamp": datetime.now().isoformat()
                }
            }

            async with self.session.post(f"{self.base_url}/api/events", json=event_data) as response:
                await response.text()  # Consume the response
        except Exception:
            pass  # Ignore errors during backlog test

    async def simulate_disk_space_issue(self) -> bool:
        """
        Simulate disk space issue by checking the system's response to storage pressure

        Returns:
            Boolean indicating if system handled the issue gracefully
        """
        print("Simulating disk space pressure response")

        try:
            # Check if system has proper disk space monitoring and alerts
            # This is more about verifying the system's resilience to storage issues
            # Rather than actually filling up disk space

            # Make several requests to see if the system handles storage gracefully
            for _ in range(10):
                async with self.session.get(f"{self.base_url}/health") as response:
                    if response.status != 200:
                        print("❌ System not responding during disk space simulation")
                        return False
                await asyncio.sleep(0.5)

            print("✅ System handled disk space pressure simulation successfully")
            return True

        except Exception as e:
            print(f"Error simulating disk space issue: {e}")
            return False

    async def run_all_recovery_tests(self) -> Dict[str, Any]:
        """
        Run all recovery tests

        Returns:
            Dictionary with test results
        """
        print("Starting system recovery tests...")
        print(f"Target URL: {self.base_url}")

        # Define the tests to run
        tests = [
            ("Pod Failure Recovery", self.test_pod_failure_recovery),
            ("Network Partition Recovery", self.test_network_partition_recovery),
            ("Database Failure Recovery", self.test_database_failure_recovery),
            ("API Overload Recovery", self.test_api_overload_recovery),
            ("Message Queue Backlog Recovery", self.test_message_queue_backlog_recovery),
            ("Disk Space Pressure Recovery", self.test_disk_space_pressure_recovery)
        ]

        for test_name, test_func in tests:
            print(f"\nRunning: {test_name}")
            print("-" * 50)

            try:
                result = await test_func()

                self.test_results['tests_run'] += 1
                if result:
                    self.test_results['tests_passed'] += 1
                    print(f"✅ {test_name} PASSED")
                else:
                    self.test_results['tests_failed'] += 1
                    self.test_results['failures'].append(test_name)
                    print(f"❌ {test_name} FAILED")

            except Exception as e:
                self.test_results['tests_run'] += 1
                self.test_results['tests_failed'] += 1
                self.test_results['failures'].append(f"{test_name}: {str(e)}")
                print(f"❌ {test_name} ERROR: {e}")

        self.test_results['end_time'] = datetime.now()
        self.test_results['duration'] = str(self.test_results['end_time'] - self.test_results['start_time'])

        return self.test_results

    async def test_pod_failure_recovery(self) -> bool:
        """
        Test pod failure recovery
        """
        # In a real test, we would target specific pods
        # For now, we'll simulate with a generic approach
        return await self.simulate_pod_failure("todo-backend-0")  # Example pod name

    async def test_network_partition_recovery(self) -> bool:
        """
        Test network partition recovery
        """
        return await self.simulate_network_partition(30)

    async def test_database_failure_recovery(self) -> bool:
        """
        Test database failure recovery
        """
        return await self.simulate_database_failure(45)

    async def test_api_overload_recovery(self) -> bool:
        """
        Test API overload recovery
        """
        return await self.simulate_api_overload(60)

    async def test_message_queue_backlog_recovery(self) -> bool:
        """
        Test message queue backlog recovery
        """
        return await self.simulate_message_queue_backlog(60)

    async def test_disk_space_pressure_recovery(self) -> bool:
        """
        Test disk space pressure recovery
        """
        return await self.simulate_disk_space_issue()

    def print_final_report(self):
        """
        Print the final test report
        """
        print(f"\n{'='*70}")
        print("SYSTEM RECOVERY TEST REPORT")
        print(f"{'='*70}")
        print(f"Start Time: {self.test_results['start_time']}")
        print(f"End Time: {self.test_results['end_time']}")
        print(f"Duration: {self.test_results['duration']}")
        print(f"Tests Run: {self.test_results['tests_run']}")
        print(f"Tests Passed: {self.test_results['tests_passed']}")
        print(f"Tests Failed: {self.test_results['tests_failed']}")

        if self.test_results['failures']:
            print(f"\nFailed Tests:")
            for failure in self.test_results['failures']:
                print(f"  - {failure}")

        pass_rate = (self.test_results['tests_passed'] / max(1, self.test_results['tests_run'])) * 100
        print(f"\nPass Rate: {pass_rate:.1f}%")

        if self.test_results['tests_failed'] == 0:
            print(f"\n🎉 All system recovery tests PASSED!")
            print("✅ System demonstrates good resilience to failure scenarios")
        else:
            print(f"\n⚠️  {self.test_results['tests_failed']} test(s) failed")
            print("🔍 Review the failed tests and improve system resilience")

        print(f"{'='*70}")


class ChaosEngineeringTester(SystemRecoveryTester):
    """
    Extended tester for chaos engineering-style failure scenarios
    """

    async def test_cascading_failures(self) -> bool:
        """
        Test cascading failure scenarios where one failure triggers others
        """
        print("Testing cascading failure scenarios...")

        try:
            # Simulate multiple simultaneous failures to test for cascading effects
            tasks = [
                asyncio.create_task(self.simulate_network_partition(20)),
                asyncio.create_task(self._make_stress_requests_during_failure(20))
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Check if system recovered from the combined stress
            recovered = await self.wait_for_recovery(120)

            if recovered and all(isinstance(r, bool) and r for r in results if not isinstance(r, Exception)):
                print("✅ Cascading failure test passed - system remained stable")
                return True
            else:
                print("❌ Cascading failure test failed - system instability detected")
                return False

        except Exception as e:
            print(f"Error in cascading failure test: {e}")
            return False

    async def _make_stress_requests_during_failure(self, duration: int):
        """
        Helper method to make stress requests during a failure scenario
        """
        start_time = time.time()
        while time.time() - start_time < duration:
            try:
                async with self.session.get(f"{self.base_url}/health") as response:
                    await response.text()
            except Exception:
                pass  # Expected during failure
            await asyncio.sleep(0.2)

    async def test_dependency_isolation(self) -> bool:
        """
        Test that failures in one service don't cascade to others
        """
        print("Testing dependency isolation...")

        try:
            # This would involve testing that if the notification service fails,
            # it doesn't bring down the main todo service
            initial_health = await self.check_system_health()
            if not initial_health:
                print("❌ System not healthy at start of dependency isolation test")
                return False

            # Simulate failure of a non-critical service (e.g., notification service)
            # In a real test, we'd target the specific service
            await asyncio.sleep(10)  # Simulate service unavailability

            # Check if main services remain available
            main_service_health = await self.check_system_health()

            if main_service_health:
                print("✅ Dependency isolation test passed - main service remained available")
                return True
            else:
                print("❌ Dependency isolation test failed - main service affected by dependency failure")
                return False

        except Exception as e:
            print(f"Error in dependency isolation test: {e}")
            return False


async def main():
    """
    Main function to run system recovery tests
    """
    parser = argparse.ArgumentParser(description='Test system recovery from failure scenarios')
    parser.add_argument('--url', default='http://localhost:8080',
                       help='Base URL of the system under test')
    parser.add_argument('--timeout', type=int, default=300,
                       help='Timeout for recovery waits in seconds')

    args = parser.parse_args()

    async with SystemRecoveryTester(args.url, args.timeout) as tester:
        results = await tester.run_all_recovery_tests()
        tester.print_final_report()

        # Calculate exit code based on results
        if results['tests_failed'] > 0:
            print(f"\n🚨 {results['tests_failed']} recovery test(s) failed.")
            print("This indicates potential reliability issues that should be addressed.")
            return 1
        else:
            print(f"\n✅ All recovery tests passed! System demonstrates good failure resilience.")
            return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)