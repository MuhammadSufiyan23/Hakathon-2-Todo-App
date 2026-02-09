#!/usr/bin/env python3
"""
Script to run the backend server with proper Python path setup.
This addresses the import issues when running the server in deployment environments.
"""
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set the working directory to backend
os.chdir(backend_dir)

# Now import and run the main app
from main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))