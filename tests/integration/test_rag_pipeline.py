import pytest
import requests
import time
import os
from pathlib import Path

# Test configuration
INGESTION_BASE_URL = "http://localhost:8003"
INFERENCE_BASE_URL = "http://localhost:8004"
FRONTEND_BASE_URL = "http://localhost:3001"

class TestRAGIntegration:
    """Integration tests for the complete RAG pipeline"""
    
    @classmethod
    def setup_class(cls):
        """Wait for services to be ready"""
        cls.wait_for_services()
    
    @staticmethod
    def wait_for_services(timeout=120):
        """Wait for all services to be healthy"""
        services = [
            (INGESTION_BASE_URL, "Ingestion Service"),
            (INFERENCE_BASE_URL, "Inference Backend"),
            (FRONTEND_BASE_URL, "Frontend")
        ]
        
        start_time = time.time()
        
        for url, name in services:
            while time.time() - start_time < timeout:
                try:
                    response = requests.get(f"{url}/health", timeout=5)
                    if response.status_code == 200:
                        print(f"✅ {name} is ready")
                        break
                except requests.exceptions.RequestException:
                    pass
                
                print(f"⏳ Waiting for {name}...")
                time.sleep(5)
            else:
                pytest.fail(f"❌ {name} failed to start within {timeout} seconds")

    def test_ingestion_health(self):
        """Test ingestion service health endpoint"""
        response = requests.get(f"{INGESTION_BASE_URL}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_inference_health(self):
        """Test inference service health endpoint"""
        response = requests.get(f"{INFERENCE_BASE_URL}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_frontend_accessible(self):
        """Test frontend is accessible"""
        response = requests.get(FRONTEND_BASE_URL, timeout=10)
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    def test_document_ingestion(self):
        """Test document upload and processing"""
        # Create test document
        test_content = """
        Artificial Intelligence (AI) is a field of computer science that focuses on creating
        systems capable of performing tasks that typically require human intelligence.
        These tasks include learning, reasoning, problem-solving, and understanding language.
        """
        
        files = {
            'file': ('test_document.txt', test_content, 'text/plain')
        }
        
        response = requests.post(
            f"{INGESTION_BASE_URL}/api/ingestion/upload",
            files=files,
            timeout=30
        )
        
        # Should return success or accepted status
        assert response.status_code in [200, 202]
        
        # Wait a bit for processing
        time.sleep(5)

    def test_chat_query(self):
        """Test chat functionality"""
        payload = {
            "message": "What is artificial intelligence?",
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        response = requests.post(
            f"{INFERENCE_BASE_URL}/api/chat",
            json=payload,
            timeout=30
        )
        
        # Should return successful response
        assert response.status_code in [200, 202]
        
        # Response should contain some content
        if response.status_code == 200:
            response_data = response.json()
            assert "message" in response_data or "response" in response_data

    def test_end_to_end_rag_pipeline(self):
        """Test complete RAG pipeline: ingest -> query -> response"""
        
        # Step 1: Upload a document
        test_doc = """
        Machine Learning is a subset of artificial intelligence that enables computers
        to learn and make decisions from data without being explicitly programmed.
        It uses algorithms to identify patterns in data and make predictions.
        """
        
        files = {'file': ('ml_doc.txt', test_doc, 'text/plain')}
        
        ingestion_response = requests.post(
            f"{INGESTION_BASE_URL}/api/ingestion/upload",
            files=files,
            timeout=30
        )
        
        assert ingestion_response.status_code in [200, 202]
        
        # Step 2: Wait for document processing
        time.sleep(10)
        
        # Step 3: Query about the uploaded content
        query_payload = {
            "message": "What is machine learning?",
            "temperature": 0.5,
            "max_tokens": 200
        }
        
        chat_response = requests.post(
            f"{INFERENCE_BASE_URL}/api/chat",
            json=query_payload,
            timeout=45
        )
        
        assert chat_response.status_code in [200, 202]
        
        # Step 4: Verify response contains relevant information
        if chat_response.status_code == 200:
            response_text = str(chat_response.json()).lower()
            # Should mention machine learning concepts
            assert any(keyword in response_text for keyword in [
                "machine learning", "algorithm", "data", "pattern", "prediction"
            ])

    def test_concurrent_requests(self):
        """Test system under concurrent load"""
        import concurrent.futures
        import threading
        
        def make_chat_request(query_id):
            payload = {
                "message": f"Test query {query_id}: What is AI?",
                "temperature": 0.5,
                "max_tokens": 50
            }
            
            try:
                response = requests.post(
                    f"{INFERENCE_BASE_URL}/api/chat",
                    json=payload,
                    timeout=30
                )
                return response.status_code, query_id
            except Exception as e:
                return 500, query_id
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_chat_request, i) for i in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # At least 70% of requests should succeed
        successful_requests = sum(1 for status, _ in results if status in [200, 202])
        success_rate = successful_requests / len(results)
        
        assert success_rate >= 0.7, f"Success rate too low: {success_rate}"

    def test_error_handling(self):
        """Test error handling for invalid requests"""
        
        # Test invalid chat payload
        invalid_payload = {"invalid": "payload"}
        
        response = requests.post(
            f"{INFERENCE_BASE_URL}/api/chat",
            json=invalid_payload,
            timeout=10
        )
        
        assert response.status_code in [400, 422]
        
        # Test invalid file upload
        files = {'file': ('test.exe', b'malicious content', 'application/exe')}
        
        response = requests.post(
            f"{INGESTION_BASE_URL}/api/ingestion/upload",
            files=files,
            timeout=10
        )
        
        assert response.status_code in [400, 422]

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
