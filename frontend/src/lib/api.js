import axios from 'axios';
import { clearToken, getToken } from './auth';

const api = axios.create({
  baseURL: `${import.meta.env.VITE_API_URL}/api`,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
    const requestUrl = error?.config?.url || '';
    const onAuthPage = window.location.pathname === '/login' || window.location.pathname === '/signup';
    const isLoginCall = requestUrl.includes('/auth/login');
    if (status === 401 && !onAuthPage && !isLoginCall) {
      clearToken();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  },
);

export default api;
