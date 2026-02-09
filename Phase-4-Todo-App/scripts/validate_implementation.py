#!/usr/bin/env python3
"""
Validation script to check the AI Todo Chatbot implementation
"""
import os
import sys
from pathlib import Path

def validate_directory_structure():
    """Validate that all required directories exist"""
    required_dirs = [
        "backend/src/models",
        "backend/src/services",
        "backend/src/tools",
        "backend/src/agents",
        "backend/src/api",
        "frontend/src/components",
        "frontend/src/pages",
        "frontend/src/services"
    ]

    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)

    if missing_dirs:
        print(f"[ERROR] Missing directories: {missing_dirs}")
        return False
    else:
        print("[SUCCESS] All required directories exist")
        return True


def validate_required_files():
    """Validate that all required files exist"""
    required_files = [
        "backend/src/models/conversation.py",
        "backend/src/models/message.py",
        "backend/src/tools/task_tools.py",
        "backend/src/tools/server.py",
        "backend/src/agents/todo_agent.py",
        "backend/src/agents/runner.py",
        "backend/src/api/chat.py",
        "frontend/src/components/ChatBot.tsx",
        "frontend/src/components/ChatIcon.tsx",
        "frontend/src/pages/dashboard.tsx",
        "docs/ai-todo-chatbot.md"
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print(f"[ERROR] Missing files: {missing_files}")
        return False
    else:
        print("[SUCCESS] All required files exist")
        return True


def validate_dependencies():
    """Validate that required dependencies are in requirements.txt"""
    requirements_path = "backend/requirements.txt"
    if not Path(requirements_path).exists():
        print("[ERROR] requirements.txt not found")
        return False

    with open(requirements_path, 'r') as f:
        content = f.read()

    required_deps = ["openai", "cohere", "mcp"]
    missing_deps = []

    for dep in required_deps:
        if dep not in content.lower():
            missing_deps.append(dep)

    if missing_deps:
        print(f"[ERROR] Missing dependencies in requirements.txt: {missing_deps}")
        return False
    else:
        print("[SUCCESS] All required dependencies are present")
        return True


def validate_environment():
    """Validate environment configuration"""
    env_file = "backend/.env"
    if not Path(env_file).exists():
        print("[ERROR] backend/.env file not found")
        return False

    with open(env_file, 'r') as f:
        content = f.read()

    required_vars = ["COHERE_API_KEY", "OPENAI_API_KEY"]
    missing_vars = []

    for var in required_vars:
        if var not in content:
            missing_vars.append(var)

    if missing_vars:
        print(f"[ERROR] Missing environment variables in backend/.env: {missing_vars}")
        return False
    else:
        print("[SUCCESS] Environment variables are configured")
        return True


def main():
    print("Validating AI Todo Chatbot Implementation...")
    print()

    checks = [
        validate_directory_structure(),
        validate_required_files(),
        validate_dependencies(),
        validate_environment()
    ]

    if all(checks):
        print()
        print("All validations passed! AI Todo Chatbot implementation is complete.")
        return 0
    else:
        print()
        print("Some validations failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())