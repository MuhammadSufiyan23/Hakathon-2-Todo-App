#!/usr/bin/env python3
"""Test script to check if imports work properly"""

print("Testing imports...")

try:
    from routes.tasks import router as tasks_router
    print("[OK] Routes import successful")
except Exception as e:
    print(f"[ERROR] Routes import failed: {e}")
    import traceback
    traceback.print_exc()

try:
    from models import Task
    print("[OK] Models import successful")
except Exception as e:
    print(f"[ERROR] Models import failed: {e}")
    import traceback
    traceback.print_exc()

try:
    from utils.auth import get_current_user
    print("[OK] Auth utility import successful")
except Exception as e:
    print(f"[ERROR] Auth utility import failed: {e}")
    import traceback
    traceback.print_exc()

try:
    from db import get_session
    print("[OK] DB utility import successful")
except Exception as e:
    print(f"[ERROR] DB utility import failed: {e}")
    import traceback
    traceback.print_exc()

print("Import test completed.")