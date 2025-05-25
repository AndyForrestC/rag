import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

export const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '1m', target: 5 },   // Ramp up to 5 users
    { duration: '3m', target: 5 },   // Stay at 5 users
    { duration: '1m', target: 10 },  // Ramp up to 10 users
    { duration: '3m', target: 10 },  // Stay at 10 users
    { duration: '1m', target: 0 },   // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<10000'], // 95% of requests must complete below 10s
    http_req_failed: ['rate<0.1'],      // Error rate must be below 10%
    errors: ['rate<0.1'],
  },
};

const BASE_URL = 'http://localhost:8001';

export default function () {
  // Create a simple text file for upload
  const fileContent = 'This is a test document for RAG ingestion. It contains sample text that will be processed and vectorized.';
  
  const formData = {
    file: http.file(fileContent, 'test-document.txt', 'text/plain'),
    collection_name: 'test_collection',
  };

  const uploadResponse = http.post(`${BASE_URL}/api/ingestion/upload`, formData);
  
  const uploadSuccess = check(uploadResponse, {
    'upload status is 200 or 202': (r) => r.status === 200 || r.status === 202,
    'upload response time < 30s': (r) => r.timings.duration < 30000,
    'upload response has job_id or success': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.job_id || body.status === 'success';
      } catch (e) {
        return false;
      }
    },
  });

  errorRate.add(!uploadSuccess);

  // Test health endpoint
  const healthResponse = http.get(`${BASE_URL}/health`);
  
  const healthSuccess = check(healthResponse, {
    'health status is 200': (r) => r.status === 200,
    'health response time < 100ms': (r) => r.timings.duration < 100,
  });

  errorRate.add(!healthSuccess);

  sleep(2);
}
