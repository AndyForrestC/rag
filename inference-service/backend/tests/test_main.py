import pytest
from fastapi.testclient import TestClient

def test_health_check():
    """Test health check endpoint"""
    from main import app
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


def test_chat_endpoint_exists():
    """Test that chat endpoint exists"""
    from main import app
    with TestClient(app) as client:
        response = client.post("/api/chat", json={"message": "Hello"})
        # The endpoint should exist even if it returns an error due to missing dependencies
        assert response.status_code in [200, 400, 422, 500]


class TestInferenceService:
    """Test suite for inference service functionality"""
    
    def test_chat_message_validation(self):
        """Test chat message validation"""
        # Test with empty message
        response = client.post("/api/chat", json={"message": ""})
        assert response.status_code in [400, 422]
    
    def test_chat_message_format(self):
        """Test chat message format"""
        response = client.post("/api/chat", json={"invalid": "format"})
        assert response.status_code in [400, 422]
