import requests
import os
from dotenv import load_dotenv

# Load environment from backend directory
backend_dir = os.path.join(os.getcwd(), 'backend')
os.chdir(backend_dir)
load_dotenv('.env')

# Get the API key
api_key = os.getenv("COHERE_API_KEY")
print(f"Using API key: {api_key}")

if not api_key or api_key == "dummy-key-for-import":
    print("ERROR: COHERE_API_KEY is not properly set!")
    exit(1)

# Test the API call directly
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": "command-r-08-2024",
    "message": "Hello, how are you?",
    "temperature": 0.1
}

print("Making test request to Cohere API...")
response = requests.post(
    "https://api.cohere.ai/v1/chat",
    headers=headers,
    json=data
)

print(f"Response Status Code: {response.status_code}")
print(f"Response Text: {response.text}")

if response.status_code == 200:
    print("SUCCESS: Cohere API is working!")
else:
    print("FAILED: Cohere API is not working properly.")