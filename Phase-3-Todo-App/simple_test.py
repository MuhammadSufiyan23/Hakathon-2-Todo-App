#!/usr/bin/env python3
"""
Simple test to verify the original errors are fixed
"""

import sys
import os

# Add backend to sys.path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

print("Testing imports that were causing the original error...")

try:
    # This mimics the original error sequence:
    # File "/routes/tasks.py", line 287, in <module> -> from schemas import TaskCreate, TaskUpdate, TaskOut

    # First, test if schemas can be imported without error
    print("1. Testing schemas import...")
    import sys
    original_path = sys.path[:]

    # Change to backend directory to mimic how routes/tasks.py would import
    os.chdir(backend_dir)
    sys.path.insert(0, backend_dir)  # Make sure backend is in path

    from schemas import TaskCreate, TaskUpdate, TaskOut
    print("   [OK] Schemas import successful - no IndentationError!")

    # Now test if models can be imported
    print("2. Testing models import...")
    from models import Task, User
    print("   [OK] Models import successful!")

    # Test if routes can import schemas (mimicking routes/tasks.py)
    print("3. Testing routes import chain...")
    from routes.tasks import router  # This internally does 'from schemas import ...'
    print("   [OK] Routes import successful!")

    print("\nAll original errors appear to be fixed!")
    print("- No ModuleNotFoundError for backend.db")
    print("- No relative import errors")
    print("- No IndentationError in schemas.py")

except SyntaxError as e:
    print(f"   [ERROR] SyntaxError (might be the indentation error): {e}")
except ImportError as e:
    print(f"   [ERROR] ImportError: {e}")
except Exception as e:
    print(f"   [INFO] Different error (may be new issue): {type(e).__name__}: {e}")
    print("   Note: This may be a different issue not related to the original errors.")

finally:
    # Restore original path and dir
    sys.path[:] = original_path
    os.chdir(os.path.dirname(__file__))