import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { env } from '../config/env';
import { authSessionStorage } from '../storage/authSession.storage';
import { authTokenStorage } from '../storage/authToken.storage';
import { ApiError } from './apiError';

type ErrorResponse = {
  message?: string;
  detail?: string | { msg?: string } | Array<{ msg?: string }>;
};

type RefreshResponse = {
  access_token: string;
  token_type: string;
};

type RetryableRequestConfig = InternalAxiosRequestConfig & {
  _retry?: boolean;
};

function getErrorMessage(error: AxiosError<ErrorResponse>) {
  const data = error.response?.data;

  if (data?.message) return data.message;
  if (typeof data?.detail === 'string') return data.detail;
  if (Array.isArray(data?.detail)) return data.detail[0]?.msg ?? error.message;
  if (data?.detail?.msg) return data.detail.msg;

  return error.message;
}

function shouldAttemptRefresh(error: AxiosError<ErrorResponse>) {
  const status = error.response?.status;
  const url = error.config?.url ?? '';

  return status === 401 && !url.includes('/auth/login') && !url.includes('/auth/refresh');
}

export const apiClient = axios.create({
  baseURL: env.apiBaseUrl,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const accessToken = authTokenStorage.getAccessToken();

  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }

  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ErrorResponse>) => {
    const originalRequest = error.config as RetryableRequestConfig | undefined;

    if (originalRequest && !originalRequest._retry && shouldAttemptRefresh(error)) {
      originalRequest._retry = true;

      try {
        const { data } = await axios.post<RefreshResponse>(
          `${env.apiBaseUrl}/auth/refresh`,
          undefined,
          { withCredentials: true },
        );

        authTokenStorage.setAccessToken(data.access_token);

        const session = authSessionStorage.getSession();
        if (session) {
          authSessionStorage.setSession({
            ...session,
            accessToken: data.access_token,
            tokenType: data.token_type,
          });
        }

        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return apiClient(originalRequest);
      } catch {
        authTokenStorage.clear();
        authSessionStorage.clear();
      }
    }

    const status = error.response?.status;
    const message = getErrorMessage(error);

    return Promise.reject(new ApiError(message, status));
  },
);
