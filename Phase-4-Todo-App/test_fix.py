#!/usr/bin/env python3
"""
Test script to verify that the import issues are fixed
"""

import sys
import os

# Add backend to path like the main.py does
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

try:
    print("Testing main.py imports...")
    from backend.main import app
    print("✓ Main import successful")

    print("Testing schemas import...")
    from backend.schemas import TaskCreate, TaskUpdate, TaskOut
    print("✓ Schemas import successful")

    print("Testing routes import...")
    from backend.routes.tasks import router
    print("✓ Routes import successful")

    print("\nAll imports successful! The runtime error should be fixed.")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()