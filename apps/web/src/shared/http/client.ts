import axios, { type AxiosInstance } from 'axios';

const api: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptor for request ID and idempotent key
api.interceptors.request.use((config) => {
  if (!config.headers['X-Request-Id']) {
    config.headers['X-Request-Id'] = `req_${Math.random().toString(36).substring(2, 10)}`;
  }
  return config;
});

// Interceptor for standard error translation
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.data?.error) {
      const err = error.response.data.error;
      const customError = new Error(err.message || '请求处理失败');
      (customError as any).code = err.code;
      (customError as any).details = err.details;
      (customError as any).retryable = err.retryable;
      return Promise.reject(customError);
    }
    const message = error.response?.data?.detail || error.message || '网络连接或服务异常';
    return Promise.reject(new Error(typeof message === 'string' ? message : JSON.stringify(message)));
  }
);

export default api;
