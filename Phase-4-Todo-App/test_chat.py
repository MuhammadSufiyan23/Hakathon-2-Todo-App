import requests
import json

# Test the backend chat endpoint directly
BASE_URL = "http://localhost:8000"

def test_chat_endpoint():
    """Test if the chat endpoint is accessible"""
    try:
        # First try to access the API docs to confirm the server is running
        response = requests.get(f"{BASE_URL}/docs")
        print(f"API Docs Status: {response.status_code}")

        # Check if the chat endpoint exists by looking at available endpoints
        openapi_response = requests.get(f"{BASE_URL}/openapi.json")
        if openapi_response.status_code == 200:
            api_spec = openapi_response.json()
            paths = list(api_spec.get('paths', {}).keys())
            print(f"Available endpoints: {len(paths)} found")

            # Look for chat-related endpoints
            chat_endpoints = [path for path in paths if 'chat' in path.lower()]
            print(f"Chat-related endpoints: {chat_endpoints}")

            if '/api/{user_id}/chat' in paths:
                print("[OK] Chat endpoint exists: /api/{user_id}/chat")

                # Test with a dummy user ID (this will likely fail due to auth, but should reach the endpoint)
                try:
                    test_response = requests.post(
                        f"{BASE_URL}/api/testuser/chat",
                        json={"message": "hello", "conversation_id": None},
                        headers={"Authorization": "Bearer invalid-token"}
                    )
                    print(f"[OK] Chat endpoint reachable, returns status: {test_response.status_code}")

                    # If it's a 401, that's expected (auth failure)
                    if test_response.status_code == 401:
                        print("[OK] Chat endpoint properly requires authentication")
                    elif test_response.status_code == 404:
                        print("[ERROR] Chat endpoint not found")
                    else:
                        print(f"[INFO] Chat endpoint returned: {test_response.status_code}")

                except Exception as e:
                    print(f"[ERROR] Error reaching chat endpoint: {e}")
            else:
                print("[ERROR] Chat endpoint not found in API spec")
        else:
            print("[ERROR] Could not retrieve API specification")

    except Exception as e:
        print(f"[ERROR] Error connecting to backend: {e}")

if __name__ == "__main__":
    print("Testing chat functionality...")
    test_chat_endpoint()