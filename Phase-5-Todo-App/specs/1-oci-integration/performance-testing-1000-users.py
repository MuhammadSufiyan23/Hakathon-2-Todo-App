"""
Performance testing with 1000+ concurrent users
This script tests the system's performance under high load conditions
"""

import asyncio
import aiohttp
import json
import time
import statistics
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import argparse
import sys
import random
import uuid
from dataclasses import dataclass
import heapq


@dataclass
class PerformanceTestConfig:
    """Configuration for performance testing"""
    concurrent_users: int = 1000
    test_duration_minutes: int = 10
    think_time_min: float = 0.5  # Min time between requests (seconds)
    think_time_max: float = 2.0  # Max time between requests (seconds)
    target_response_time: float = 1.0  # Target response time (seconds)
    max_acceptable_error_rate: float = 0.05  # 5% max errors
    ramp_up_time: int = 120  # seconds to reach full load
    reporting_interval: int = 30  # seconds between reports


class PerformanceTester:
    """
    Performance tester for high-concurrency scenarios
    """

    def __init__(self, base_url: str = "http://localhost:8080", config: PerformanceTestConfig = None):
        self.base_url = base_url.rstrip('/')
        self.config = config or PerformanceTestConfig()
        self.session = None
        self.results = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'response_times': [],
            'error_rate': 0,
            'avg_response_time': 0,
            'p95_response_time': 0,
            'p99_response_time': 0,
            'throughput_rps': 0,
            'start_time': datetime.now(),
            'end_time': None,
            'metrics_history': [],
            'concurrent_users_history': []
        }
        self.active_users = 0
        self.stop_event = asyncio.Event()

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=1000, limit_per_host=100)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def authenticate_user(self) -> Optional[str]:
        """Authenticate a user and return the token"""
        user_data = {
            "username": f"perf_test_user_{uuid.uuid4().hex[:8]}",
            "email": f"perf{uuid.uuid4().hex[:8]}@example.com",
            "password": "SecurePassword123!"
        }

        # Try to register the user first
        try:
            async with self.session.post(f"{self.base_url}/api/users/register", json=user_data) as reg_response:
                if reg_response.status not in [200, 201, 409]:  # 409 = already exists
                    print(f"Registration failed: {reg_response.status}")
                    return None

            # Login to get token
            login_data = {
                "username": user_data["username"],
                "password": user_data["password"]
            }

            async with self.session.post(f"{self.base_url}/api/users/login", json=login_data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return response_data.get('access_token') or response_data.get('token')
                else:
                    print(f"Login failed: {response.status}")
                    return None
        except Exception as e:
            print(f"Authentication error: {e}")
            return None

    async def make_request_with_timing(self, endpoint: str, method: str = 'GET',
                                     data: Dict = None, token: str = None) -> Dict[str, Any]:
        """Make a request and record timing information"""
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'

        url = f"{self.base_url}{endpoint}"
        start_time = time.time()

        try:
            async with self.session.request(method, url, json=data, headers=headers) as response:
                response_time = time.time() - start_time
                response_text = await response.text()

                # Record metrics
                self.results['response_times'].append(response_time)
                self.results['total_requests'] += 1

                if 200 <= response.status < 300:
                    self.results['successful_requests'] += 1
                    success = True
                else:
                    self.results['failed_requests'] += 1
                    success = False

                return {
                    'status': response.status,
                    'response_time': response_time,
                    'success': success,
                    'response_text': response_text[:100]  # Limit response size
                }
        except asyncio.TimeoutError:
            response_time = time.time() - start_time
            self.results['failed_requests'] += 1
            self.results['total_requests'] += 1
            self.results['response_times'].append(response_time)

            return {
                'status': 408,  # Request Timeout
                'response_time': response_time,
                'success': False,
                'error': 'Request timed out'
            }
        except Exception as e:
            response_time = time.time() - start_time
            self.results['failed_requests'] += 1
            self.results['total_requests'] += 1
            self.results['response_times'].append(response_time)

            return {
                'status': 0,
                'response_time': response_time,
                'success': False,
                'error': str(e)
            }

    async def user_behavior_simulation(self, user_id: str, token: str):
        """Simulate realistic user behavior with the given token"""
        self.active_users += 1

        try:
            while not self.stop_event.is_set():
                # Randomly choose an action
                action = random.choice([
                    ('GET', '/api/tasks'),
                    ('POST', '/api/tasks', {
                        "title": f"Performance test task {uuid.uuid4().hex[:8]}",
                        "description": "Task created during performance testing",
                        "status": "pending",
                        "priority": random.choice(["low", "medium", "high"])
                    }),
                    ('GET', '/api/users/profile'),
                    ('GET', '/api/tasks/stats')
                ])

                method = action[0]
                endpoint = action[1]
                data = action[2] if len(action) > 2 else None

                await self.make_request_with_timing(endpoint, method, data, token)

                # Simulate think time between requests
                think_time = random.uniform(self.config.think_time_min, self.config.think_time_max)
                await asyncio.sleep(think_time)

        except Exception as e:
            print(f"Error in user simulation {user_id}: {e}")
        finally:
            self.active_users -= 1

    async def spawn_users_gradually(self) -> List[asyncio.Task]:
        """Spawn users gradually over the ramp-up period"""
        tasks = []
        start_time = time.time()
        end_ramp_time = start_time + self.config.ramp_up_time

        # Calculate how many users to spawn per second
        users_per_second = self.config.concurrent_users / self.config.ramp_up_time

        print(f"Spawning {self.config.concurrent_users} users over {self.config.ramp_up_time} seconds "
              f"({users_per_second:.2f} users/sec)")

        spawned_users = 0
        while spawned_users < self.config.concurrent_users and time.time() < end_ramp_time:
            # Calculate how many users should be spawned by now
            elapsed = time.time() - start_time
            target_spawned = int(elapsed * users_per_second)

            # Spawn any additional users needed
            while spawned_users < target_spawned and spawned_users < self.config.concurrent_users:
                token = await self.authenticate_user()
                if token:
                    user_task = asyncio.create_task(
                        self.user_behavior_simulation(f"user_{spawned_users}", token)
                    )
                    tasks.append(user_task)
                    spawned_users += 1

                    if spawned_users % 100 == 0:
                        print(f"Spawned {spawned_users}/{self.config.concurrent_users} users")
                else:
                    print(f"Failed to authenticate user {spawned_users}, skipping...")

                # Small delay to avoid overwhelming the system during startup
                await asyncio.sleep(0.01)

            # Wait a bit before checking again
            await asyncio.sleep(0.1)

        print(f"Completed spawning {spawned_users} users")
        return tasks

    async def report_metrics_periodically(self):
        """Report metrics periodically during the test"""
        start_time = time.time()

        while not self.stop_event.is_set():
            await asyncio.sleep(self.config.reporting_interval)

            if self.results['total_requests'] > 0:
                current_time = time.time()
                elapsed = current_time - start_time
                current_rps = self.results['total_requests'] / elapsed if elapsed > 0 else 0

                # Calculate current metrics
                if self.results['response_times']:
                    current_avg = statistics.mean(self.results['response_times'])
                    current_p95 = self._calculate_percentile(95)
                    current_p99 = self._calculate_percentile(99)
                else:
                    current_avg = current_p95 = current_p99 = 0

                current_error_rate = self.results['failed_requests'] / self.results['total_requests']

                print(f"[{elapsed:.0f}s] Users: {self.active_users}, "
                      f"Requests: {self.results['total_requests']}, "
                      f"RPS: {current_rps:.2f}, "
                      f"Resp Time (avg/p95/p99): {current_avg:.3f}s/{current_p95:.3f}s/{current_p99:.3f}s, "
                      f"Error Rate: {current_error_rate:.2%}")

                # Store metrics history
                self.results['metrics_history'].append({
                    'timestamp': time.time(),
                    'active_users': self.active_users,
                    'total_requests': self.results['total_requests'],
                    'rps': current_rps,
                    'avg_response_time': current_avg,
                    'p95_response_time': current_p95,
                    'p99_response_time': current_p99,
                    'error_rate': current_error_rate
                })

    def _calculate_percentile(self, percentile: int) -> float:
        """Calculate the specified percentile of response times"""
        if not self.results['response_times']:
            return 0
        sorted_times = sorted(self.results['response_times'])
        index = int((percentile / 100) * len(sorted_times))
        index = min(index, len(sorted_times) - 1)
        return sorted_times[index]

    async def run_performance_test(self) -> Dict[str, Any]:
        """Run the full performance test"""
        print(f"Starting performance test with {self.config.concurrent_users} concurrent users")
        print(f"Test duration: {self.config.test_duration_minutes} minutes")
        print(f"Ramp-up time: {self.config.ramp_up_time} seconds")

        # Spawn users gradually
        user_tasks = await self.spawn_users_gradually()

        # Start metrics reporting
        metrics_task = asyncio.create_task(self.report_metrics_periodically())

        # Run the test for the specified duration
        print(f"Running performance test for {self.config.test_duration_minutes} minutes...")
        await asyncio.sleep(self.config.test_duration_minutes * 60)

        # Signal stop and wait for tasks to complete
        print("Stopping performance test...")
        self.stop_event.set()

        # Wait a bit for tasks to stop gracefully
        await asyncio.sleep(5)

        # Cancel all tasks
        for task in user_tasks:
            if not task.done():
                task.cancel()

        metrics_task.cancel()

        try:
            await asyncio.gather(*user_tasks, metrics_task, return_exceptions=True)
        except asyncio.CancelledError:
            pass

        # Calculate final metrics
        self.calculate_final_metrics()

        return self.results

    def calculate_final_metrics(self):
        """Calculate final performance metrics"""
        if self.results['total_requests'] > 0:
            self.results['error_rate'] = self.results['failed_requests'] / self.results['total_requests']
            self.results['throughput_rps'] = self.results['total_requests'] / (self.config.test_duration_minutes * 60)

            if self.results['response_times']:
                self.results['avg_response_time'] = statistics.mean(self.results['response_times'])
                self.results['p95_response_time'] = self._calculate_percentile(95)
                self.results['p99_response_time'] = self._calculate_percentile(99)

        self.results['end_time'] = datetime.now()

    def evaluate_performance_success(self) -> bool:
        """Evaluate if performance test was successful"""
        success_criteria = [
            self.results['error_rate'] <= self.config.max_acceptable_error_rate,
            self.results['avg_response_time'] <= self.config.target_response_time,
            self.results['p95_response_time'] <= self.config.target_response_time * 2  # Allow higher for p95
        ]

        return all(success_criteria)

    def print_performance_report(self):
        """Print the performance test report"""
        print(f"\n{'='*100}")
        print("PERFORMANCE TEST REPORT (1000+ CONCURRENT USERS)")
        print(f"{'='*100}")
        print(f"Test Configuration:")
        print(f"  - Concurrent Users: {self.config.concurrent_users:,}")
        print(f"  - Test Duration: {self.config.test_duration_minutes} minutes")
        print(f"  - Ramp-up Time: {self.config.ramp_up_time} seconds")
        print(f"  - Target Response Time: {self.config.target_response_time}s")
        print(f"  - Max Acceptable Error Rate: {self.config.max_acceptable_error_rate:.1%}")
        print(f"")
        print(f"Test Results:")
        print(f"  - Total Requests: {self.results['total_requests']:,}")
        print(f"  - Successful Requests: {self.results['successful_requests']:,}")
        print(f"  - Failed Requests: {self.results['failed_requests']:,}")
        print(f"  - Error Rate: {self.results['error_rate']:.2%}")
        print(f"  - Average Response Time: {self.results['avg_response_time']:.3f}s")
        print(f"  - P95 Response Time: {self.results['p95_response_time']:.3f}s")
        print(f"  - P99 Response Time: {self.results['p99_response_time']:.3f}s")
        print(f"  - Peak Throughput: {self.results['throughput_rps']:.2f} RPS")
        print(f"  - Test Duration: {self.results['end_time'] - self.results['start_time']}")
        print(f"")

        print(f"PERFORMANCE EVALUATION:")
        criteria_met = []

        if self.results['error_rate'] <= self.config.max_acceptable_error_rate:
            criteria_met.append(f"✅ Error rate acceptable ({self.results['error_rate']:.2%} ≤ {self.config.max_acceptable_error_rate:.1%})")
        else:
            criteria_met.append(f"❌ Error rate too high ({self.results['error_rate']:.2%} > {self.config.max_acceptable_error_rate:.1%})")

        if self.results['avg_response_time'] <= self.config.target_response_time:
            criteria_met.append(f"✅ Avg response time acceptable ({self.results['avg_response_time']:.3f}s ≤ {self.config.target_response_time}s)")
        else:
            criteria_met.append(f"❌ Avg response time too high ({self.results['avg_response_time']:.3f}s > {self.config.target_response_time}s)")

        if self.results['p95_response_time'] <= self.config.target_response_time * 2:
            criteria_met.append(f"✅ P95 response time acceptable ({self.results['p95_response_time']:.3f}s ≤ {self.config.target_response_time * 2}s)")
        else:
            criteria_met.append(f"❌ P95 response time too high ({self.results['p95_response_time']:.3f}s > {self.config.target_response_time * 2}s)")

        for criterion in criteria_met:
            print(f"  {criterion}")

        success = self.evaluate_performance_success()
        print(f"")
        if success:
            print(f"🎉 PERFORMANCE TEST PASSED!")
            print(f"✅ System performs well under high concurrency load")
        else:
            print(f"⚠️  PERFORMANCE TEST PARTIALLY FAILED")
            print(f"🔍 Review the performance bottlenecks and optimize as needed")

        print(f"{'='*100}")

    def generate_detailed_metrics_report(self) -> Dict[str, Any]:
        """Generate a detailed metrics report"""
        report = {
            'summary': {
                'test_duration': str(self.results['end_time'] - self.results['start_time']),
                'concurrent_users': self.config.concurrent_users,
                'total_requests': self.results['total_requests'],
                'successful_requests': self.results['successful_requests'],
                'failed_requests': self.results['failed_requests'],
                'error_rate': self.results['error_rate'],
                'throughput_rps': self.results['throughput_rps']
            },
            'response_time_metrics': {
                'average': self.results['avg_response_time'],
                'p50': self._calculate_percentile(50),
                'p90': self._calculate_percentile(90),
                'p95': self.results['p95_response_time'],
                'p99': self.results['p99_response_time'],
                'min': min(self.results['response_times']) if self.results['response_times'] else 0,
                'max': max(self.results['response_times']) if self.results['response_times'] else 0
            },
            'time_series': self.results['metrics_history'],
            'recommendations': self._generate_recommendations()
        }

        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []

        if self.results['error_rate'] > self.config.max_acceptable_error_rate:
            recommendations.append("Reduce error rate by optimizing error handling and improving system stability")

        if self.results['avg_response_time'] > self.config.target_response_time:
            recommendations.append("Improve response time through database optimization, caching, or code optimization")

        if self.results['p99_response_time'] > self.config.target_response_time * 3:
            recommendations.append("Address outliers causing high p99 response times")

        if self.results['throughput_rps'] is not None and self.results['throughput_rps'] < 100:  # arbitrary threshold
            recommendations.append("Consider infrastructure scaling to handle higher throughput")

        if not recommendations:
            recommendations.append("Performance is satisfactory under high load conditions")

        return recommendations


async def main():
    """Main function to run performance testing"""
    parser = argparse.ArgumentParser(description='Run performance test with 1000+ concurrent users')
    parser.add_argument('--url', default='http://localhost:8080',
                       help='Base URL of the Todo App')
    parser.add_argument('--users', type=int, default=1000,
                       help='Number of concurrent users (default: 1000)')
    parser.add_argument('--duration', type=int, default=10,
                       help='Test duration in minutes (default: 10)')
    parser.add_argument('--target-response-time', type=float, default=1.0,
                       help='Target response time in seconds (default: 1.0)')
    parser.add_argument('--output-report',
                       help='Output detailed metrics report to JSON file')

    args = parser.parse_args()

    # Create performance test configuration
    config = PerformanceTestConfig(
        concurrent_users=args.users,
        test_duration_minutes=args.duration,
        target_response_time=args.target_response_time
    )

    print(f"Preparing performance test with {args.users:,} concurrent users...")
    print(f"This may take a while to ramp up to full load...")

    async with PerformanceTester(args.url, config) as tester:
        results = await tester.run_performance_test()
        tester.print_performance_report()

        # Generate and optionally save detailed report
        detailed_report = tester.generate_detailed_metrics_report()

        if args.output_report:
            with open(args.output_report, 'w') as f:
                json.dump(detailed_report, f, indent=2, default=str)
            print(f"\nDetailed metrics report saved to {args.output_report}")

        # Determine exit code based on performance success
        if tester.evaluate_performance_success():
            print(f"\n✅ Performance test successful! System can handle high concurrency.")
            return 0
        else:
            print(f"\n⚠️  Performance test revealed issues that need optimization.")
            return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)