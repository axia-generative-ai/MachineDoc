import axios, { AxiosError } from 'axios';
import { env } from '../config/env';
import { authTokenStorage } from '../storage/authToken.storage';
import { ApiError } from './apiError';

export const apiClient = axios.create({
  baseURL: env.apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const accessToken = authTokenStorage.getAccessToken();

  // 로그인 이후 요청은 공통으로 Authorization 헤더를 붙인다.
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }

  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ message?: string }>) => {
    const status = error.response?.status;
    const message = error.response?.data?.message ?? error.message;

    return Promise.reject(new ApiError(message, status));
  },
);
