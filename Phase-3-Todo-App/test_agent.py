#!/usr/bin/env python3
"""
Script to test the AI agent functionality directly
"""

import sys
import os

# Add backend to path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

# Set up environment
os.environ.setdefault('BETTER_AUTH_SECRET', 'test-secret-key-for-development')
# Remove or set empty COHERE_API_KEY to trigger fallback mechanism
os.environ.pop('COHERE_API_KEY', None)  # Remove if exists
os.environ['COHERE_API_KEY'] = ''  # Set to empty string

def test_agent():
    print("Testing AI agent functionality...")

    try:
        # Import the agent runner
        from backend.src.agents.runner import get_agent_runner

        # Create a test runner
        agent_runner = get_agent_runner()

        # Test a simple task
        test_input = "Add a task to buy groceries"
        user_id = "test-user-123"
        conversation_history = []

        print(f"Running agent with input: {test_input}")
        result = agent_runner.run_agent(
            user_input=test_input,
            user_id=user_id,
            conversation_history=conversation_history
        )

        print("Agent response:", result)

    except Exception as e:
        print(f"Error testing agent: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agent()