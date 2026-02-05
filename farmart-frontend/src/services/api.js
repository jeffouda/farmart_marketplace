import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Enable credentials for cookies
});

// Request interceptor for handling FormData
api.interceptors.request.use(
  (config) => {
    // If data is FormData, let browser set Content-Type with boundary
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Helper methods
export const apiGet = (endpoint) => api.get(endpoint).then((r) => r.data);
export const apiPost = (endpoint, data) => api.post(endpoint, data);
export const apiPut = (endpoint, data) => api.put(endpoint, data);
export const apiPatch = (endpoint, data) => api.patch(endpoint, data);
export const apiDelete = (endpoint) => api.delete(endpoint);

export default api;
