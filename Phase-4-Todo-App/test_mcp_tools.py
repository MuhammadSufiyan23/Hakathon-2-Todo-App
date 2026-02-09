#!/usr/bin/env python3
"""
Test script for MCP tools implementation
"""

import uuid
from todo_mcp_tools import list_tasks, add_task, update_task, delete_task, complete_task


def test_mcp_tools():
    # Generate a test user ID
    test_user_id = f"test_user_{uuid.uuid4()}"

    print(f"Testing MCP tools with user ID: {test_user_id}")

    # Test adding a task
    print("\n1. Testing add_task...")
    task = add_task(
        user_id=test_user_id,
        title="Test Task",
        description="This is a test task",
        priority="high"
    )
    print(f"Added task: {task}")
    task_id = task['id']

    # Test listing tasks
    print("\n2. Testing list_tasks...")
    tasks = list_tasks(user_id=test_user_id)
    print(f"Tasks for user: {tasks}")

    # Test updating a task
    print("\n3. Testing update_task...")
    updated_task = update_task(
        task_id=task_id,
        user_id=test_user_id,
        title="Updated Test Task",
        description="This is an updated test task",
        priority="medium"
    )
    print(f"Updated task: {updated_task}")

    # Test completing a task
    print("\n4. Testing complete_task...")
    completed_task = complete_task(
        task_id=task_id,
        user_id=test_user_id,
        completed=True
    )
    print(f"Completed task: {completed_task}")

    # Test uncompleting a task
    print("\n5. Testing complete_task (set to incomplete)...")
    incomplete_task = complete_task(
        task_id=task_id,
        user_id=test_user_id,
        completed=False
    )
    print(f"Incomplete task: {incomplete_task}")

    # Final list to verify all operations worked
    print("\n6. Final list_tasks...")
    final_tasks = list_tasks(user_id=test_user_id)
    print(f"Final tasks for user: {final_tasks}")

    # Test deleting the task
    print("\n7. Testing delete_task...")
    delete_result = delete_task(
        task_id=task_id,
        user_id=test_user_id
    )
    print(f"Delete result: {delete_result}")

    # Final verification that task was deleted
    print("\n8. Final verification (should be empty)...")
    final_verification = list_tasks(user_id=test_user_id)
    print(f"Tasks after deletion: {final_verification}")

    print("\nAll tests completed successfully!")


if __name__ == "__main__":
    test_mcp_tools()