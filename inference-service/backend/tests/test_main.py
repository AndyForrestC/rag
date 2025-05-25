import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the parent directory to the Python path so we can import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


@pytest.fixture
def client():
    """Create test client fixture"""
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_chat_endpoint_exists(client):
    """Test that chat endpoint exists"""
    response = client.post("/api/chat", json={"message": "Hello"})
    # The endpoint should exist even if it returns an error due to missing dependencies
    assert response.status_code in [200, 400, 422, 500]


class TestInferenceService:
    """Test suite for inference service functionality"""
    
    def test_chat_message_validation(self, client):
        """Test chat message validation"""
        # Test with empty message
        response = client.post("/api/chat", json={"message": ""})
        assert response.status_code in [400, 422]
    
    def test_chat_message_format(self, client):
        """Test chat message format validation"""
        # Test with invalid JSON format
        response = client.post("/api/chat", json={"invalid_field": "test"})
        assert response.status_code in [400, 422]
