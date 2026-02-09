import requests
import json

def test_chat_functionality():
    """
    Test the chat functionality to see if the fixes work
    """
    # Use a mock user ID for testing
    user_id = "user_test123"
    
    # Headers for the request
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer dummy_token_for_testing"  # This might be required depending on your auth setup
    }

    # Test different chat commands
    test_messages = [
        {"message": "Add a task to buy groceries"},
        {"message": "Show my tasks"},
        {"message": "Add another task to call mom"},
        {"message": "List my tasks"}
    ]
    
    for i, payload in enumerate(test_messages):
        print(f"\n--- Test {i+1}: {payload['message']} ---")
        
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
            else:
                print(f"ERROR: Chat API returned status code {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("ERROR: Could not connect to the server. Is the backend running?")
            return False
        except Exception as e:
            print(f"ERROR: An exception occurred: {str(e)}")
            return False
    
    return True

if __name__ == "__main__":
    print("Testing chat functionality after fixes...")
    test_chat_functionality()