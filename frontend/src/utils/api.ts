/**
 * Centralized API client with error handling, retries, and auth
 */
import React from 'react';

export interface ApiError {
  code: string;
  message: string;
  details?: any;
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  headers?: HeadersInit;
  body?: any;
  timeout?: number;
  retries?: number;
}

const DEFAULT_TIMEOUT = 10000;
const DEFAULT_RETRIES = 2;

class ApiClient {
  private baseUrl: string = '';
  private token: string | null = null;

  constructor() {
    // Use relative URLs for proxy
    this.baseUrl = '';
    this.loadToken();
  }

  private loadToken() {
    try {
      this.token = localStorage.getItem('auth_token');
    } catch (e) {
      // localStorage not available
    }
  }

  setToken(token: string) {
    this.token = token;
    try {
      localStorage.setItem('auth_token', token);
    } catch (e) {
      // localStorage not available
    }
  }

  clearToken() {
    this.token = null;
    try {
      localStorage.removeItem('auth_token');
    } catch (e) {
      // localStorage not available
    }
  }

  private getHeaders(options?: RequestOptions): HeadersInit {
    const headers: any = {
      'Content-Type': 'application/json',
    };

    if (options?.headers) {
      Object.assign(headers, options.headers);
    }

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  private async withRetry<T>(
    fn: () => Promise<T>,
    retries: number = DEFAULT_RETRIES
  ): Promise<T> {
    try {
      return await fn();
    } catch (error) {
      if (retries > 0 && this.isRetryableError(error)) {
        await new Promise((resolve) => setTimeout(resolve, 1000));
        return this.withRetry(fn, retries - 1);
      }
      throw error;
    }
  }

  private isRetryableError(error: any): boolean {
    // Retry on network errors or 5xx status codes
    if (error instanceof TypeError) return true;
    if (error.status && error.status >= 500) return true;
    return false;
  }

  private async fetchWithTimeout(
    url: string,
    options: RequestInit,
    timeout: number
  ): Promise<Response> {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);

    try {
      return await fetch(url, {
        ...options,
        signal: controller.signal,
      });
    } finally {
      clearTimeout(id);
    }
  }

  async request<T>(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const timeout = options.timeout || DEFAULT_TIMEOUT;
    const retries = options.retries !== undefined ? options.retries : DEFAULT_RETRIES;

    const fetchRequest = async () => {
      const response = await this.fetchWithTimeout(
        url,
        {
          method: options.method || 'GET',
          headers: this.getHeaders(options),
          body: options.body ? JSON.stringify(options.body) : undefined,
        },
        timeout
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const error = new Error(errorData.message || `API Error: ${response.status}`) as any;
        error.status = response.status;
        error.code = errorData.error_code || `HTTP_${response.status}`;
        error.details = errorData.details;
        throw error;
      }

      if (response.status === 204) {
        return {} as T;
      }

      return response.json() as Promise<T>;
    };

    return this.withRetry(fetchRequest, retries);
  }

  // Convenience methods
  async get<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'GET' });
  }

  async post<T>(
    endpoint: string,
    body: any,
    options?: RequestOptions
  ): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'POST', body });
  }

  async put<T>(
    endpoint: string,
    body: any,
    options?: RequestOptions
  ): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'PUT', body });
  }

  async delete<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' });
  }
}

export const apiClient = new ApiClient();

// Hooks for use in components
export const useApi = <T,>(
  endpoint: string | null,
  options?: RequestOptions
) => {
  const [data, setData] = React.useState<T | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<ApiError | null>(null);

  React.useEffect(() => {
    if (!endpoint) {
      setLoading(false);
      return;
    }

    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await apiClient.get<T>(endpoint, options);
        setData(result);
      } catch (err: any) {
        setError({
          code: err.code || 'UNKNOWN_ERROR',
          message: err.message || 'Failed to fetch data',
          details: err.details,
        });
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [endpoint, options]);

  const refetch = async () => {
    if (!endpoint) return;
    try {
      setLoading(true);
      setError(null);
      const result = await apiClient.get<T>(endpoint, options);
      setData(result);
    } catch (err: any) {
      setError({
        code: err.code || 'UNKNOWN_ERROR',
        message: err.message || 'Failed to fetch data',
        details: err.details,
      });
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, error, refetch };
};
