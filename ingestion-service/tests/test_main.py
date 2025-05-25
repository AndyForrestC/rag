import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_ingestion_endpoint_exists():
    """Test that ingestion endpoint exists"""
    response = client.post("/api/ingestion/upload", files={"file": ("test.txt", "test content", "text/plain")})
    # The endpoint should exist even if it returns an error due to missing dependencies
    assert response.status_code in [200, 400, 422, 500]


class TestIngestionService:
    """Test suite for ingestion service functionality"""
    
    def test_file_upload_validation(self):
        """Test file upload validation"""
        # Test with invalid file type
        response = client.post("/api/ingestion/upload", files={"file": ("test.exe", "malicious content", "application/exe")})
        assert response.status_code in [400, 422]
    
    def test_empty_file_upload(self):
        """Test empty file upload"""
        response = client.post("/api/ingestion/upload", files={"file": ("empty.txt", "", "text/plain")})
        assert response.status_code in [400, 422]
