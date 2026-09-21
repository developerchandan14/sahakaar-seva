// Sahakaar Seva API Client
const API_BASE = window.API_BASE || 'https://sahakaar-seva-0409.onrender.com';

class ApiClient {
  constructor() {
    this.base = API_BASE;
    this.token = localStorage.getItem('sahakaar_token');
  }

  setToken(token) {
    this.token = token;
    localStorage.setItem('sahakaar_token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('sahakaar_token');
  }

  async request(path, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    };
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const res = await fetch(`${this.base}${path}`, {
      ...options,
      headers
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({detail: res.statusText}));
      throw new Error(err.detail || `API Error ${res.status}`);
    }
    return res.json();
  }

  // Auth
  async register(data) {
    return this.request('/auth/register', {method: 'POST', body: JSON.stringify(data)});
  }

  async login(phone, password) {
    const form = new URLSearchParams();
    form.append('username', phone);
    form.append('password', password);
    const res = await fetch(`${this.base}/auth/login`, {
      method: 'POST',
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: form
    });
    if (!res.ok) throw new Error('Login failed');
    const data = await res.json();
    this.setToken(data.access_token);
    return data;
  }

  async me() {
    return this.request('/auth/me');
  }

  // Workers
  async listWorkers(params = {}) {
    const q = new URLSearchParams(params).toString();
    return this.request(`/workers?${q}`);
  }

  // Jobs
  async createJob(data) {
    return this.request('/jobs', {method: 'POST', body: JSON.stringify(data)});
  }

  async listJobs(params = {}) {
    const q = new URLSearchParams(params).toString();
    return this.request(`/jobs?${q}`);
  }

  async aiMatch(jobId, top_k=5) {
    return this.request('/jobs/ai/match', {method: 'POST', body: JSON.stringify({job_id: jobId, top_k})});
  }

  async acceptJob(jobId, workerId) {
    return this.request(`/jobs/${jobId}/accept`, {method: 'POST', body: JSON.stringify({worker_id: workerId})});
  }

  async completeJob(jobId) {
    return this.request(`/jobs/${jobId}/complete`, {method: 'POST'});
  }

  // Payments
  async getPaymentByJob(jobId) {
    return this.request(`/payments/job/${jobId}`);
  }

  async getTransparency(jobId) {
    return this.request(`/payments/job/${jobId}/transparency`);
  }

  async getPolicy(coopId) {
    return this.request(`/payments/cooperative/${coopId}/policy`);
  }

  async updatePolicy(coopId, data) {
    return this.request(`/payments/cooperative/${coopId}/policy`, {method: 'PUT', body: JSON.stringify(data)});
  }

  // Cooperative
  async getCooperative(coopId) {
    return this.request(`/cooperative/${coopId}`);
  }

  async getDashboard(coopId) {
    return this.request(`/cooperative/${coopId}/dashboard`);
  }

  async getCoopWorkers(coopId) {
    return this.request(`/cooperative/${coopId}/workers`);
  }

  async getCoopJobs(coopId) {
    return this.request(`/cooperative/${coopId}/jobs`);
  }

  // AI
  async demandForecast() {
    return this.request('/ai/demand-forecast');
  }

  async workforceInsights() {
    return this.request('/ai/workforce-insights');
  }

  async trainingRecommendations() {
    return this.request('/ai/training-recommendations');
  }

  async anomalies() {
    return this.request('/ai/anomalies');
  }

  async nlQuery(query) {
    return this.request(`/ai/natural-language?query=${encodeURIComponent(query)}&cooperative_id=1`, {method: 'POST'});
  }
}

window.api = new ApiClient();
