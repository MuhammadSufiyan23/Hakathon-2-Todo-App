#!/usr/bin/env python3
"""
Minimal test to isolate the import issue
"""

import sys
import os

# Add backend to path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

print("Testing individual imports to isolate the issue...")

try:
    print("1. Importing models directly...")
    from models import Task, User
    print("   [OK] Models import successful")

    print("2. Importing schemas...")
    from schemas import TaskCreate, TaskUpdate, TaskOut
    print("   [OK] Schemas import successful")

    print("3. Importing db...")
    from db import engine
    print("   [OK] DB import successful")

    print("4. Importing routes.tasks (this is where the error occurs)...")
    from routes.tasks import router
    print("   [OK] Routes import successful")

    print("\nAll imports successful! The issue might be resolved.")

except Exception as e:
    print(f"   [ERROR] Error occurred: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()