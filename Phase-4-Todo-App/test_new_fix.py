import sys
import os

# Add backend to path to simulate the environment
backend_dir = os.path.join(os.getcwd(), 'backend')
sys.path.insert(0, backend_dir)

try:
    from src.tools.task_tools import add_task
    print("✅ task_tools.py imports successfully")
    print("✅ No ModuleNotFoundError for 'backend' module")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()