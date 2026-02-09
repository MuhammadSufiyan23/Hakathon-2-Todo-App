import requests
import json

# Test the chat functionality
def test_chat():
    # Replace with a valid user_id from your system
    user_id = "user_123"  # This should match the authenticated user

    # Headers for the request
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test-token"  # This might be required depending on your auth setup
    }

    # Test data for adding a task
    payload = {
        "message": "Add a task by meeting",
        "conversation_id": None
    }

    # Make the request to the chat endpoint
    url = f"http://localhost:8000/api/{user_id}/chat"

    try:
        print(f"Making request to: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")

        response = requests.post(url, headers=headers, json=payload)

        print(f"Response Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

        if response.status_code == 200:
            print("SUCCESS: Chat API is working!")
            return True
        else:
            print(f"ERROR: Chat API returned status code {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the server. Is the backend running?")
        return False
    except Exception as e:
        print(f"ERROR: An exception occurred: {str(e)}")
        return False

if __name__ == "__main__":
    test_chat()