"""
Horizontal scaling tests under various load conditions
This script tests the system's ability to scale horizontally under different load conditions
"""

import asyncio
import aiohttp
import subprocess
import json
import time
import statistics
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import argparse
import sys
import random
from dataclasses import dataclass


@dataclass
class LoadTestConfig:
    """Configuration for load testing"""
    duration_minutes: int = 5
    initial_concurrent_users: int = 10
    peak_concurrent_users: int = 100
    ramp_up_time: int = 60  # seconds
    target_response_time: float = 0.5  # seconds
    max_error_rate: float = 0.01  # 1%
    hpa_threshold_cpu: int = 70  # percentage
    hpa_threshold_memory: int = 70  # percentage


class HorizontalScalingTester:
    """
    Tester for horizontal scaling capabilities under various load conditions
    """

    def __init__(self, base_url: str = "http://localhost:8080", config: LoadTestConfig = None):
        self.base_url = base_url.rstrip('/')
        self.config = config or LoadTestConfig()
        self.session = None
        self.metrics_collector = MetricsCollector()
        self.scaling_results = {
            'initial_pods': 0,
            'peak_pods': 0,
            'final_pods': 0,
            'scaling_events': 0,
            'requests_per_second': 0,
            'avg_response_time': 0,
            'p95_response_time': 0,
            'error_rate': 0,
            'cpu_utilization': [],
            'memory_utilization': [],
            'start_time': datetime.now()
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_pod_count(self, deployment_name: str, namespace: str = "default") -> int:
        """Get the current number of pods for a deployment"""
        try:
            cmd = ["kubectl", "get", "deployment", deployment_name, "-n", namespace, "-o", "jsonpath={.status.readyReplicas}"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode == 0:
                count_str = result.stdout.strip()
                return int(count_str) if count_str.isdigit() else 0
            else:
                print(f"Error getting pod count: {result.stderr}")
                return 0
        except Exception as e:
            print(f"Exception getting pod count: {e}")
            return 0

    async def get_resource_utilization(self, namespace: str = "default") -> Dict[str, Any]:
        """Get current resource utilization for the namespace"""
        try:
            # Get CPU and memory usage for pods
            cmd = ["kubectl", "top", "pods", "-n", namespace, "--no-headers"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            cpu_usage = []
            memory_usage = []

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 3:
                            # Format: NAME CPU(cores) MEMORY(bytes)
                            cpu_str = parts[1]
                            mem_str = parts[2]

                            # Parse CPU (e.g., "100m" = 100 milliCPUs = 0.1 CPU)
                            cpu_val = 0
                            if cpu_str.endswith('m'):
                                cpu_val = int(cpu_str[:-1]) / 1000
                            elif cpu_str.isdigit():
                                cpu_val = int(cpu_str)

                            # Parse memory (e.g., "100Mi" = 100 MiB)
                            mem_val = 0
                            if mem_str.endswith('Mi'):
                                mem_val = int(mem_str[:-2])
                            elif mem_str.endswith('Ki'):
                                mem_val = int(mem_str[:-2]) / 1024
                            elif mem_str.endswith('Gi'):
                                mem_val = int(mem_str[:-2]) * 1024

                            cpu_usage.append(cpu_val)
                            memory_usage.append(mem_val)

            return {
                'cpu_avg': statistics.mean(cpu_usage) if cpu_usage else 0,
                'cpu_max': max(cpu_usage) if cpu_usage else 0,
                'memory_avg': statistics.mean(memory_usage) if memory_usage else 0,
                'memory_max': max(memory_usage) if memory_usage else 0
            }
        except Exception as e:
            print(f"Exception getting resource utilization: {e}")
            return {
                'cpu_avg': 0,
                'cpu_max': 0,
                'memory_avg': 0,
                'memory_max': 0
            }

    async def make_authenticated_request(self, endpoint: str, method: str = 'GET',
                                       data: Dict = None, token: str = None) -> Dict[str, Any]:
        """Make an authenticated request to the API"""
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'

        url = f"{self.base_url}{endpoint}"
        start_time = time.time()

        try:
            async with self.session.request(method, url, json=data, headers=headers) as response:
                response_time = time.time() - start_time
                response_text = await response.text()

                return {
                    'status': response.status,
                    'response_time': response_time,
                    'success': 200 <= response.status < 300,
                    'response_text': response_text[:200]  # Limit response size
                }
        except Exception as e:
            response_time = time.time() - start_time
            return {
                'status': 0,
                'response_time': response_time,
                'success': False,
                'error': str(e)
            }

    async def simulate_user_activity(self, user_id: str, auth_token: str, duration: int):
        """Simulate a user performing various activities for a duration"""
        end_time = time.time() + duration
        request_count = 0
        results = []

        while time.time() < end_time:
            # Randomly select an activity
            activity = random.choice([
                self._get_tasks,
                self._create_task,
                self._update_task,
                self._complete_task,
                self._get_user_profile
            ])

            try:
                result = await activity(auth_token)
                results.append(result)
                request_count += 1
            except Exception as e:
                results.append({
                    'status': 0,
                    'response_time': 0,
                    'success': False,
                    'error': str(e)
                })

            # Random delay between requests (simulate realistic user behavior)
            await asyncio.sleep(random.uniform(0.5, 2.0))

        return results

    async def _get_tasks(self, auth_token: str) -> Dict[str, Any]:
        """Simulate getting tasks"""
        return await self.make_authenticated_request('/api/tasks', 'GET', token=auth_token)

    async def _create_task(self, auth_token: str) -> Dict[str, Any]:
        """Simulate creating a task"""
        task_data = {
            "title": f"Load test task {uuid.uuid4().hex[:8]}",
            "description": "Task created during horizontal scaling test",
            "status": "pending",
            "priority": random.choice(["low", "medium", "high"]),
            "due_date": (datetime.now() + timedelta(days=random.randint(1, 30))).isoformat()
        }
        return await self.make_authenticated_request('/api/tasks', 'POST', task_data, auth_token)

    async def _update_task(self, auth_token: str) -> Dict[str, Any]:
        """Simulate updating a task"""
        # Use a random task ID for this simulation
        task_id = f"task_{random.randint(1, 1000)}"
        update_data = {
            "status": random.choice(["pending", "in-progress", "completed"]),
            "priority": random.choice(["low", "medium", "high"])
        }
        return await self.make_authenticated_request(f'/api/tasks/{task_id}', 'PUT', update_data, auth_token)

    async def _complete_task(self, auth_token: str) -> Dict[str, Any]:
        """Simulate completing a task"""
        task_id = f"task_{random.randint(1, 1000)}"
        return await self.make_authenticated_request(f'/api/tasks/{task_id}/complete', 'POST', token=auth_token)

    async def _get_user_profile(self, auth_token: str) -> Dict[str, Any]:
        """Simulate getting user profile"""
        return await self.make_authenticated_request('/api/users/profile', 'GET', token=auth_token)

    async def register_and_authenticate_users(self, num_users: int) -> List[str]:
        """Register and authenticate multiple users"""
        import uuid
        auth_tokens = []

        for i in range(num_users):
            user_data = {
                "username": f"loadtest_user_{uuid.uuid4().hex[:8]}",
                "email": f"loadtest{i}@example.com",
                "password": "SecurePassword123!"
            }

            # Register user
            try:
                async with self.session.post(f"{self.base_url}/api/users/register", json=user_data) as response:
                    if response.status == 201:
                        response_data = await response.json()
                        user_id = response_data.get('user_id') or response_data.get('id')
                    else:
                        print(f"Failed to register user {i}: {response.status}")
                        continue
            except Exception as e:
                print(f"Error registering user {i}: {e}")
                continue

            # Login user
            login_data = {
                "username": user_data["username"],
                "password": user_data["password"]
            }

            try:
                async with self.session.post(f"{self.base_url}/api/users/login", json=login_data) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        token = response_data.get('access_token') or response_data.get('token')
                        if token:
                            auth_tokens.append(token)
                    else:
                        print(f"Failed to login user {i}: {response.status}")
            except Exception as e:
                print(f"Error logging in user {i}: {e}")

        return auth_tokens

    async def run_scaling_test(self, deployment_name: str = "todo-backend") -> Dict[str, Any]:
        """Run the horizontal scaling test"""
        print(f"Starting horizontal scaling test for deployment: {deployment_name}")
        print(f"Duration: {self.config.duration_minutes} minutes")
        print(f"Initial users: {self.config.initial_concurrent_users}")
        print(f"Peak users: {self.config.peak_concurrent_users}")

        # Get initial state
        initial_pods = await self.get_pod_count(deployment_name)
        self.scaling_results['initial_pods'] = initial_pods
        print(f"Initial pod count: {initial_pods}")

        # Register and authenticate users
        print("Registering and authenticating test users...")
        auth_tokens = await self.register_and_authenticate_users(self.config.peak_concurrent_users)
        print(f"Successfully authenticated {len(auth_tokens)} users")

        # Start monitoring resource utilization
        monitor_task = asyncio.create_task(self.monitor_resources(deployment_name))

        # Start load test with gradual ramp-up
        print("Starting load test with gradual ramp-up...")
        start_time = time.time()
        end_time = start_time + (self.config.duration_minutes * 60)
        all_results = []

        # Ramp up users gradually
        current_users = self.config.initial_concurrent_users
        ramp_end_time = start_time + self.config.ramp_up_time

        while time.time() < end_time:
            # Calculate current number of users based on ramp-up schedule
            elapsed = time.time() - start_time
            if elapsed <= self.config.ramp_up_time:
                # Linear ramp-up
                progress = elapsed / self.config.ramp_up_time
                current_users = int(self.config.initial_concurrent_users +
                                  (self.config.peak_concurrent_users - self.config.initial_concurrent_users) * progress)
                current_users = max(self.config.initial_concurrent_users, min(current_users, self.config.peak_concurrent_users))

            # Select active tokens for current load
            active_tokens = auth_tokens[:min(len(auth_tokens), current_users)]

            # Create user simulation tasks
            user_tasks = []
            for token in active_tokens:
                task = asyncio.create_task(
                    self.simulate_user_activity(f"user_{uuid.uuid4().hex[:8]}", token, 30)  # 30 second bursts
                )
                user_tasks.append(task)

            # Wait for a short period before next iteration
            results_batch = await asyncio.gather(*user_tasks, return_exceptions=True)
            all_results.extend([r for r in results_batch if isinstance(r, list)])

            # Check current pod count
            current_pods = await self.get_pod_count(deployment_name)
            if current_pods > self.scaling_results['peak_pods']:
                self.scaling_results['peak_pods'] = current_pods

            # Small delay to prevent overwhelming the system
            await asyncio.sleep(2)

        # Stop monitoring
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass

        # Get final state
        final_pods = await self.get_pod_count(deployment_name)
        self.scaling_results['final_pods'] = final_pods

        # Calculate metrics
        all_responses = [resp for batch in all_results if isinstance(batch, list) for resp in batch]
        successful_responses = [r for r in all_responses if r['success']]
        failed_responses = [r for r in all_responses if not r['success']]

        if all_responses:
            response_times = [r['response_time'] for r in all_responses if r['response_time'] > 0]
            if response_times:
                self.scaling_results['avg_response_time'] = statistics.mean(response_times)
                self.scaling_results['p95_response_time'] = statistics.quantiles(response_times, n=20)[-1]  # 95th percentile
                self.scaling_results['requests_per_second'] = len(all_responses) / (self.config.duration_minutes * 60)

            self.scaling_results['error_rate'] = len(failed_responses) / len(all_responses)

        print(f"Final pod count: {final_pods}")
        print(f"Peak pod count: {self.scaling_results['peak_pods']}")
        print(f"Total requests: {len(all_responses)}")
        print(f"Successful requests: {len(successful_responses)}")
        print(f"Failed requests: {len(failed_responses)}")
        print(f"Error rate: {self.scaling_results['error_rate']:.2%}")
        print(f"Avg response time: {self.scaling_results['avg_response_time']:.3f}s")
        print(f"P95 response time: {self.scaling_results['p95_response_time']:.3f}s")

        return self.scaling_results

    async def monitor_resources(self, deployment_name: str, interval: int = 10):
        """Monitor resource utilization during the test"""
        while True:
            try:
                util = await self.get_resource_utilization()
                self.scaling_results['cpu_utilization'].append(util['cpu_avg'])
                self.scaling_results['memory_utilization'].append(util['memory_avg'])

                current_pods = await self.get_pod_count(deployment_name)
                print(f"[Monitor] Pods: {current_pods}, CPU Avg: {util['cpu_avg']:.2f}, Mem Avg: {util['memory_avg']:.2f}Mi")

                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error monitoring resources: {e}")
                await asyncio.sleep(interval)

    def evaluate_scaling_success(self) -> bool:
        """Evaluate if the scaling test was successful"""
        success_criteria = [
            self.scaling_results['peak_pods'] > self.scaling_results['initial_pods'],  # Did scale up
            self.scaling_results['error_rate'] <= self.config.max_error_rate,  # Low error rate
            self.scaling_results['avg_response_time'] <= self.config.target_response_time,  # Good response time
        ]

        return all(success_criteria)

    def print_scaling_report(self):
        """Print the scaling test report"""
        print(f"\n{'='*80}")
        print("HORIZONTAL SCALING TEST REPORT")
        print(f"{'='*80}")
        print(f"Test Duration: {self.config.duration_minutes} minutes")
        print(f"Initial Pods: {self.scaling_results['initial_pods']}")
        print(f"Peak Pods: {self.scaling_results['peak_pods']}")
        print(f"Final Pods: {self.scaling_results['final_pods']}")
        print(f"Target Response Time: {self.config.target_response_time}s")
        print(f"Actual Avg Response Time: {self.scaling_results['avg_response_time']:.3f}s")
        print(f"95th Percentile Response Time: {self.scaling_results['p95_response_time']:.3f}s")
        print(f"Target Error Rate: {self.config.max_error_rate:.1%}")
        print(f"Actual Error Rate: {self.scaling_results['error_rate']:.1%}")
        print(f"Requests Per Second: {self.scaling_results['requests_per_second']:.2f}")

        scaling_factor = self.scaling_results['peak_pods'] / max(1, self.scaling_results['initial_pods'])
        print(f"Scaling Factor: {scaling_factor:.2f}x")

        print(f"\nSCALING EVALUATION:")
        criteria_met = []

        if self.scaling_results['peak_pods'] > self.scaling_results['initial_pods']:
            criteria_met.append("✅ Auto-scaling triggered (scaled up from {} to {})".format(
                self.scaling_results['initial_pods'], self.scaling_results['peak_pods']))
        else:
            criteria_met.append("❌ No scaling occurred (stayed at {})".format(self.scaling_results['initial_pods']))

        if self.scaling_results['error_rate'] <= self.config.max_error_rate:
            criteria_met.append("✅ Error rate within acceptable bounds ({}% ≤ {}%)".format(
                self.scaling_results['error_rate'] * 100, self.config.max_error_rate * 100))
        else:
            criteria_met.append("❌ Error rate exceeded threshold ({}% > {}%)".format(
                self.scaling_results['error_rate'] * 100, self.config.max_error_rate * 100))

        if self.scaling_results['avg_response_time'] <= self.config.target_response_time:
            criteria_met.append("✅ Response time acceptable ({}s ≤ {}s)".format(
                round(self.scaling_results['avg_response_time'], 3), self.config.target_response_time))
        else:
            criteria_met.append("❌ Response time too high ({}s > {}s)".format(
                round(self.scaling_results['avg_response_time'], 3), self.config.target_response_time))

        for criterion in criteria_met:
            print(f"  {criterion}")

        success = self.evaluate_scaling_success()
        if success:
            print(f"\n🎉 HORIZONTAL SCALING TEST PASSED!")
            print("✅ System successfully scaled to handle increased load")
        else:
            print(f"\n⚠️  HORIZONTAL SCALING TEST PARTIALLY FAILED")
            print("🔍 Review the criteria above and adjust HPA configuration as needed")

        print(f"{'='*80}")


class MetricsCollector:
    """Collects and analyzes performance metrics during load testing"""

    def __init__(self):
        self.requests = []
        self.responses = []
        self.errors = []

    def record_request(self, method: str, endpoint: str, start_time: float):
        """Record a request start time"""
        self.requests.append({
            'method': method,
            'endpoint': endpoint,
            'start_time': start_time
        })

    def record_response(self, request_idx: int, status: int, response_time: float):
        """Record a response"""
        self.responses.append({
            'request_idx': request_idx,
            'status': status,
            'response_time': response_time
        })

    def record_error(self, error: str, endpoint: str = None):
        """Record an error"""
        self.errors.append({
            'error': error,
            'endpoint': endpoint,
            'timestamp': datetime.now()
        })

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of collected metrics"""
        if not self.responses:
            return {}

        response_times = [r['response_time'] for r in self.responses]
        statuses = [r['status'] for r in self.responses]

        return {
            'total_requests': len(self.requests),
            'successful_requests': len([s for s in statuses if 200 <= s < 300]),
            'failed_requests': len([s for s in statuses if s >= 400 or s == 0]),
            'avg_response_time': statistics.mean(response_times) if response_times else 0,
            'p95_response_time': statistics.quantiles(response_times, n=20)[-1] if len(response_times) >= 20 else 0,
            'p99_response_time': statistics.quantiles(response_times, n=100)[-1] if len(response_times) >= 100 else 0,
            'error_rate': len(self.errors) / len(self.requests) if self.requests else 0,
            'throughput_rps': len(self.responses) / (datetime.now().timestamp() - self.requests[0]['start_time']) if self.requests else 0
        }


import uuid


async def main():
    """Main function to run horizontal scaling tests"""
    parser = argparse.ArgumentParser(description='Test horizontal scaling under load')
    parser.add_argument('--url', default='http://localhost:8080',
                       help='Base URL of the Todo App')
    parser.add_argument('--duration', type=int, default=5,
                       help='Test duration in minutes')
    parser.add_argument('--initial-users', type=int, default=10,
                       help='Initial number of concurrent users')
    parser.add_argument('--peak-users', type=int, default=100,
                       help='Peak number of concurrent users')
    parser.add_argument('--deployment', default='todo-backend',
                       help='Deployment name to test scaling on')

    args = parser.parse_args()

    # Create load test configuration
    config = LoadTestConfig(
        duration_minutes=args.duration,
        initial_concurrent_users=args.initial_users,
        peak_concurrent_users=args.peak_users
    )

    async with HorizontalScalingTester(args.url, config) as tester:
        results = await tester.run_scaling_test(args.deployment)
        tester.print_scaling_report()

        # Determine exit code based on scaling success
        if tester.evaluate_scaling_success():
            print(f"\n✅ Horizontal scaling test successful! System can scale appropriately under load.")
            return 0
        else:
            print(f"\n🚨 Horizontal scaling test revealed issues that need to be addressed.")
            return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)