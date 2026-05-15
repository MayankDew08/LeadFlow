import axios from 'axios'
import { getToken, clearToken } from './auth'

// ── Smart baseURL detection ──────────────────────────────────────────────────
// In production/Docker:  VITE_API_URL is empty → uses relative '/api'
// In standalone dev:     VITE_API_URL = 'http://localhost:8000' → uses absolute
const baseURL = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api`
  : '/api'

const api = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' }
})

// ── Request interceptor: attach JWT token ────────────────────────────────────
api.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ── Response interceptor: handle 401 ─────────────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearToken()
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api