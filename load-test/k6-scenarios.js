import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');
const authFailures = new Rate('auth_failures');

export const options = {
  stages: [
    { duration: '2m', target: 50 },
    { duration: '5m', target: 100 },
    { duration: '5m', target: 500 },
    { duration: '2m', target: 1000 },
    { duration: '2m', target: 2000 },
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<200'],
    http_req_failed: ['rate<0.01'],
    errors: ['rate<0.05'],
    auth_failures: ['rate<0.01'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const PASSKEY = __ENV.PASSKEY || 'test-passkey-123';

let authToken = '';
let ingredientIds = [];

export function setup() {
  const unlockRes = http.post(`${BASE_URL}/api/v1/auth/unlock`, JSON.stringify({
    passkey: PASSKEY,
    is_developer: false,
  }), {
    headers: { 'Content-Type': 'application/json' },
  });

  if (unlockRes.status !== 200) {
    throw new Error('Failed to unlock database: ' + unlockRes.body);
  }

  authToken = unlockRes.json('token') || '';
  console.log('Database unlocked successfully');

  const headers = { 'X-Passkey': PASSKEY };

  const ingredientsRes = http.get(`${BASE_URL}/api/v1/inventory`, { headers });

  if (ingredientsRes.status === 200) {
    const items = ingredientsRes.json('items') || [];
    ingredientIds = items.map(i => i.id);
  }

  return { authToken, ingredientIds, passkey: PASSKEY };
}

export default function (data) {
  const headers = { 'X-Passkey': data.passkey };

  testInventoryList(headers);
  testValuationSummary(headers);
  testForecast(headers);
  testCreateIngredient(headers);

  sleep(1);
}

function testInventoryList(headers) {
  const res = http.get(`${BASE_URL}/api/v1/inventory`, { headers });

  const success = check(res, {
    'inventory status 200': (r) => r.status === 200,
    'has items array': (r) => Array.isArray(r.json('items')),
  });

  errorRate.add(!success);
}

function testValuationSummary(headers) {
  const res = http.get(`${BASE_URL}/api/v1/inventory/valuation/summary`, { headers });

  const success = check(res, {
    'valuation status 200': (r) => r.status === 200,
    'has total_valuation': (r) => r.json('total_valuation') !== undefined,
  });

  errorRate.add(!success);
}

function testForecast(headers) {
  const res = http.get(`${BASE_URL}/api/v1/forecast/weather`, { headers });

  const success = check(res, {
    'forecast status 200': (r) => r.status === 200,
    'has forecasts array': (r) => Array.isArray(r.json()),
  });

  errorRate.add(!success);
}

function testCreateIngredient(headers) {
  const payload = {
    name: `Test Ingredient ${Date.now()}`,
    unit: 'gram',
    cost_per_unit: 1000,
    shelf_life_days: 7,
    current_stock: 100,
    min_stock_threshold: 20,
    lead_time_days: 2,
  };

  const res = http.post(`${BASE_URL}/api/v1/inventory`, JSON.stringify(payload), {
    headers: {
      ...headers,
      'Content-Type': 'application/json',
    },
  });

  const success = check(res, {
    'create status 201': (r) => r.status === 201,
    'returns id': (r) => r.json('id') !== undefined,
  });

  errorRate.add(!success);
}