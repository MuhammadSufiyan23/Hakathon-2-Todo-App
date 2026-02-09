import os
import sys
from dotenv import load_dotenv

# Change to the backend directory to load environment variables
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
os.chdir(backend_dir)

# Load environment variables from backend directory
load_dotenv('.env')

# Check if COHERE_API_KEY is properly loaded
cohere_key = os.getenv("COHERE_API_KEY")
print(f"COHERE_API_KEY from environment: {cohere_key}")

if cohere_key:
    print("✓ COHERE_API_KEY is loaded")

    # Test if it looks like a valid API key (not the dummy one)
    if cohere_key == "dummy-key-for-import":
        print("⚠ WARNING: Using dummy API key - this won't work with real API")
    elif len(cohere_key) >= 20:  # Basic check for reasonable length
        print("✓ API key has reasonable length")
    else:
        print("⚠ WARNING: API key might be too short to be valid")
else:
    print("✗ COHERE_API_KEY is NOT loaded")

# Test the other keys too
better_auth_secret = os.getenv("BETTER_AUTH_SECRET")
api_base_url = os.getenv("NEXT_PUBLIC_API_BASE_URL")

print(f"BETTER_AUTH_SECRET loaded: {'Yes' if better_auth_secret else 'No'}")
print(f"NEXT_PUBLIC_API_BASE_URL loaded: {api_base_url}")