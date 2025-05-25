import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
export const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '2m', target: 10 },  // Ramp up to 10 users
    { duration: '5m', target: 10 },  // Stay at 10 users
    { duration: '2m', target: 20 },  // Ramp up to 20 users
    { duration: '5m', target: 20 },  // Stay at 20 users
    { duration: '2m', target: 0 },   // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% of requests must complete below 2s
    http_req_failed: ['rate<0.1'],     // Error rate must be below 10%
    errors: ['rate<0.1'],
  },
};

const BASE_URL = 'http://localhost:8002';

export default function () {
  // Test chat endpoint
  const chatPayload = JSON.stringify({
    message: 'What is RAG?',
    temperature: 0.7,
    max_tokens: 500
  });

  const chatParams = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const chatResponse = http.post(`${BASE_URL}/api/chat`, chatPayload, chatParams);
  
  const chatSuccess = check(chatResponse, {
    'chat status is 200': (r) => r.status === 200,
    'chat response time < 5s': (r) => r.timings.duration < 5000,
    'chat response has content': (r) => r.body && r.body.length > 0,
  });

  errorRate.add(!chatSuccess);

  // Test health endpoint
  const healthResponse = http.get(`${BASE_URL}/health`);
  
  const healthSuccess = check(healthResponse, {
    'health status is 200': (r) => r.status === 200,
    'health response time < 100ms': (r) => r.timings.duration < 100,
  });

  errorRate.add(!healthSuccess);

  sleep(1);
}
