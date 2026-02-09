import requests
import json

def test_auth_flow():
    base_url = "http://localhost:8000/api/auth"

    # Try to create a test user
    signup_payload = {
        "email": "test@example.com",
        "password": "testpassword123",
        "name": "Test User"
    }

    print("Attempting to signup test user...")
    signup_response = requests.post(f"{base_url}/signup", json=signup_payload)
    print(f"Signup Response: {signup_response.status_code}")

    if signup_response.status_code == 200:
        signup_data = signup_response.json()
        token = signup_data['token']
        user_id = signup_data['user']['id']

        print(f"Signup successful! User ID: {user_id}")
        print(f"Token: {token[:20]}...")  # Show first 20 chars

        # Now test the chat endpoint with the token
        # Remove conversation_id if it's None to avoid validation error
        chat_payload = {
            "message": "Add a task by meeting"
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        print(f"\nTesting chat endpoint with user_id: {user_id}")
        chat_response = requests.post(f"http://localhost:8000/api/{user_id}/chat",
                                     headers=headers, json=chat_payload)

        print(f"Chat Response Status: {chat_response.status_code}")
        print(f"Chat Response Body: {chat_response.text}")

        if chat_response.status_code == 200:
            print("\nSUCCESS: Chat API is working with authentication!")
        else:
            print(f"\nFAILED: Chat API still returning error {chat_response.status_code}")

    else:
        print(f"Signup failed: {signup_response.text}")

        # Maybe user already exists, try login instead
        login_payload = {
            "email": "test@example.com",
            "password": "testpassword123"
        }

        print("\nTrying to login test user...")
        login_response = requests.post(f"{base_url}/login", json=login_payload)
        print(f"Login Response: {login_response.status_code}")

        if login_response.status_code == 200:
            login_data = login_response.json()
            token = login_data['token']
            user_id = login_data['user']['id']

            print(f"Login successful! User ID: {user_id}")

            # Now test the chat endpoint with the token
            chat_payload = {
                "message": "Add a task by meeting"
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }

            print(f"\nTesting chat endpoint with user_id: {user_id}")
            chat_response = requests.post(f"http://localhost:8000/api/{user_id}/chat",
                                         headers=headers, json=chat_payload)

            print(f"Chat Response Status: {chat_response.status_code}")
            print(f"Chat Response Body: {chat_response.text}")

            if chat_response.status_code == 200:
                print("\nSUCCESS: Chat API is working with authentication!")
            else:
                print(f"\nFAILED: Chat API still returning error {chat_response.status_code}")
        else:
            print(f"Login failed: {login_response.text}")

if __name__ == "__main__":
    test_auth_flow()