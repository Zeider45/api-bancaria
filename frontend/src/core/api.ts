import axios from 'axios';

const PUBLIC_API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const INTERNAL_API_BASE_URL = process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const API_BASE_URL = typeof window === 'undefined' ? INTERNAL_API_BASE_URL : PUBLIC_API_BASE_URL;

function normalizeApiErrorValue(value: unknown): string | null {
  if (!value) {
    return null;
  }

  if (typeof value === 'string') {
    return value;
  }

  if (Array.isArray(value)) {
    const messages = value
      .map((item) => {
        if (typeof item === 'string') {
          return item;
        }

        if (item && typeof item === 'object') {
          const record = item as Record<string, unknown>;
          const location = Array.isArray(record.loc)
            ? record.loc.map((part) => String(part)).join(' > ')
            : null;
          const message = typeof record.msg === 'string' ? record.msg : null;

          if (location && message) {
            return `${location}: ${message}`;
          }

          return message;
        }

        return null;
      })
      .filter((message): message is string => Boolean(message));

    return messages.length ? messages.join(' | ') : null;
  }

  if (typeof value === 'object') {
    const record = value as Record<string, unknown>;

    return (
      normalizeApiErrorValue(record.detail) ??
      normalizeApiErrorValue(record.error) ??
      normalizeApiErrorValue(record.message) ??
      (typeof record.msg === 'string' ? record.msg : null)
    );
  }

  return null;
}

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/internal/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiClient = api;

export function getApiErrorMessage(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error)) {
    const responseMessage = normalizeApiErrorValue(error.response?.data);
    return responseMessage || error.message || fallback;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return fallback;
}

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);