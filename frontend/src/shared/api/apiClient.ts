import axios, { AxiosError } from 'axios';
import { env } from '../config/env';
import { authTokenStorage } from '../storage/authToken.storage';
import { ApiError } from './apiError';

type ErrorResponse = {
  message?: string;
  detail?: string | { msg?: string } | Array<{ msg?: string }>;
};

function getErrorMessage(error: AxiosError<ErrorResponse>) {
  const data = error.response?.data;

  if (data?.message) return data.message;
  if (typeof data?.detail === 'string') return data.detail;
  if (Array.isArray(data?.detail)) return data.detail[0]?.msg ?? error.message;
  if (data?.detail?.msg) return data.detail.msg;

  return error.message;
}

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
  (error: AxiosError<ErrorResponse>) => {
    const status = error.response?.status;
    const message = getErrorMessage(error);

    return Promise.reject(new ApiError(message, status));
  },
);
