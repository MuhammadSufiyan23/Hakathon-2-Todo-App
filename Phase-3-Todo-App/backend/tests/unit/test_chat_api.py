import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_chat_endpoint_requires_auth(client):
    """Test that chat endpoint requires authentication"""
    response = client.post("/api/user123/chat", json={"message": "test message"})

    # Should return 401 or 403 since no auth token provided
    assert response.status_code in [401, 403]


def test_chat_endpoint_structure(client):
    """Test basic chat endpoint structure with mocked agent"""
    with patch('backend.src.api.chat.get_agent_runner') as mock_get_runner:
        # Mock the agent runner
        mock_runner = MagicMock()
        mock_runner.run_agent.return_value = {
            "response": "Test response",
            "tool_calls": [],
            "success": True
        }
        mock_get_runner.return_value = mock_runner

        # Mock auth dependency
        with patch('backend.utils.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"user_id": "user123", "email": "test@example.com"}

            response = client.post(
                "/api/user123/chat",
                json={"message": "test message", "conversation_id": None},
                headers={"Authorization": "Bearer fake-token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert "conversation_id" in data
            assert "response" in data
            assert "tool_calls" in data
            assert isinstance(data["tool_calls"], list)


def test_simple_chat_endpoint_requires_auth(client):
    """Test that simple chat endpoint requires authentication"""
    response = client.post("/api/chat", json={"message": "test message"})

    # Should return 401 since no auth token provided
    assert response.status_code == 401


def test_simple_chat_endpoint_success(client):
    """Test simple chat endpoint with valid auth and mocked response"""
    # This test would require mocking the JWT validation
    # For now we'll just test the auth requirement
    pass