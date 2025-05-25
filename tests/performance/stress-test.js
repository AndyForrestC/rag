import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

export const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '5m', target: 50 },   // Ramp up to 50 users
    { duration: '10m', target: 100 }, // Ramp up to 100 users
    { duration: '5m', target: 200 },  // Ramp up to 200 users (stress)
    { duration: '10m', target: 200 }, // Stay at 200 users
    { duration: '5m', target: 100 },  // Scale down to 100 users
    { duration: '5m', target: 0 },    // Scale down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(90)<3000'], // 90% of requests must complete below 3s
    http_req_failed: ['rate<0.2'],     // Error rate must be below 20% (higher for stress test)
    errors: ['rate<0.2'],
  },
};

const BASE_URL = 'http://localhost:8002';
const INGESTION_URL = 'http://localhost:8001';

export default function () {
  // Randomly choose between different endpoints
  const randomChoice = Math.random();
  
  if (randomChoice < 0.6) {
    // 60% - Chat requests
    const chatPayload = JSON.stringify({
      message: `Test query ${__VU}-${__ITER}: What is artificial intelligence and how does it work?`,
      temperature: 0.5,
      max_tokens: 300
    });

    const chatParams = {
      headers: {
        'Content-Type': 'application/json',
      },
    };

    const chatResponse = http.post(`${BASE_URL}/api/chat`, chatPayload, chatParams);
    
    const chatSuccess = check(chatResponse, {
      'chat status is 200': (r) => r.status === 200,
      'chat response time acceptable': (r) => r.timings.duration < 10000,
    });

    errorRate.add(!chatSuccess);
    
  } else if (randomChoice < 0.8) {
    // 20% - Health checks
    const healthResponse = http.get(`${BASE_URL}/health`);
    
    const healthSuccess = check(healthResponse, {
      'health status is 200': (r) => r.status === 200,
      'health response time < 500ms': (r) => r.timings.duration < 500,
    });

    errorRate.add(!healthSuccess);
    
  } else {
    // 20% - Document ingestion
    const fileContent = `Stress test document ${__VU}-${__ITER}. This document contains test content for stress testing the RAG ingestion pipeline.`;
    
    const formData = {
      file: http.file(fileContent, `stress-test-${__VU}-${__ITER}.txt`, 'text/plain'),
    };

    const uploadResponse = http.post(`${INGESTION_URL}/api/ingestion/upload`, formData);
    
    const uploadSuccess = check(uploadResponse, {
      'upload status acceptable': (r) => r.status === 200 || r.status === 202 || r.status === 429,
      'upload response time acceptable': (r) => r.timings.duration < 15000,
    });

    errorRate.add(!uploadSuccess);
  }

  sleep(Math.random() * 2 + 0.5); // Random sleep between 0.5-2.5 seconds
}
