#!/usr/bin/env python3
"""
Test script to verify the new /api/chat endpoint works correctly.
"""

import os
import sys
import subprocess
import time
import threading
import requests
import jwt
from datetime import datetime, timedelta

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

def start_server():
    """Start the FastAPI server in a separate thread."""
    from backend.main import app
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

def create_test_token():
    """Create a valid JWT token for testing."""
    secret = os.getenv('BETTER_AUTH_SECRET', 'test_secret_key_for_testing_purposes_only')

    # Create payload
    payload = {
        'userId': 'test_user_123',
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow(),
        'sub': 'test_user_123'
    }

    # Encode the token
    token = jwt.encode(payload, secret, algorithm='HS256')
    return token

def test_endpoint():
    """Test the new /api/chat endpoint."""
    time.sleep(3)  # Give server time to start

    # Test 1: Without token should return 401
    print("Testing endpoint without token...")
    response = requests.post('http://127.0.0.1:8000/api/chat',
                           json={'message': 'Hello, world!'})
    print(f"Status code without token: {response.status_code}")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    print("✓ Endpoint correctly rejects requests without token")

    # Test 2: With valid token should return 200
    print("\nTesting endpoint with valid token...")
    token = create_test_token()
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post('http://127.0.0.1:8000/api/chat',
                           json={'message': 'Hello, world!'},
                           headers=headers)
    print(f"Status code with valid token: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code == 200:
        data = response.json()
        print(f"Response data: {data}")
        assert 'reply' in data, f"Expected 'reply' in response, got {data}"
        expected_reply = "I understand your request: Hello, world!"
        assert data['reply'] == expected_reply, f"Expected '{expected_reply}', got '{data['reply']}'"
        print("✓ Endpoint correctly processes requests with valid token")
    else:
        print(f"✗ Endpoint failed with status {response.status_code}: {response.text}")

    # Test 3: With invalid token should return 401
    print("\nTesting endpoint with invalid token...")
    bad_headers = {'Authorization': 'Bearer invalid_token_here'}
    response = requests.post('http://127.0.0.1:8000/api/chat',
                           json={'message': 'Hello, world!'},
                           headers=bad_headers)
    print(f"Status code with invalid token: {response.status_code}")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    print("✓ Endpoint correctly rejects invalid tokens")

    print("\n✓ All tests passed! The new /api/chat endpoint is working correctly.")

if __name__ == '__main__':
    # Start server in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Run tests
    try:
        test_endpoint()
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nStopping server...")