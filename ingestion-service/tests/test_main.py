import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the parent directory to the Python path so we can import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app  # noqa: E402


@pytest.fixture
def client():
    """Create test client fixture"""
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_ingestion_endpoint_exists(client):
    """Test that ingestion endpoint exists"""
    response = client.post(
        "/api/ingestion/upload",
        files={"file": ("test.txt", "test content", "text/plain")},
    )
    # The endpoint should exist even if it returns an error due to missing deps
    assert response.status_code in [200, 400, 422, 500]


class TestIngestionService:
    """Test suite for ingestion service functionality"""

    def test_file_upload_validation(self, client):
        """Test file upload validation"""
        # Test with invalid file type
        response = client.post(
            "/api/ingestion/upload",
            files={
                "file": ("test.exe", "malicious content", "application/exe")
            },
        )
        assert response.status_code in [400, 422]

    def test_empty_file_upload(self, client):
        """Test empty file upload"""
        response = client.post(
            "/api/ingestion/upload",
            files={"file": ("empty.txt", "", "text/plain")},
        )
        assert response.status_code in [400, 422]
