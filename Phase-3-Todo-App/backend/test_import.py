import sys
import os

# Set up the path so that 'from models import ...' always refers to backend/models.py
backend_dir = os.path.dirname(os.path.abspath('main.py'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# This should trigger the import error if it exists
from main import app
print('App imported successfully!')