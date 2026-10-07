import axios from 'axios';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('prepai_token') || sessionStorage.getItem('prepai_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('prepai_token');
      sessionStorage.removeItem('prepai_token');
    }
    return Promise.reject(error);
  },
);
