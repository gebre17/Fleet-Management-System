/**
 * API client utility
 */
import axios, { AxiosInstance } from 'axios';
import { useAuthStore } from '@/store/authStore';

let apiClient: AxiosInstance;

export const initializeApiClient = () => {
  apiClient = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL,
    timeout: 30000,
  });

  // Request interceptor
  apiClient.interceptors.request.use((config) => {
    const { accessToken } = useAuthStore.getState();
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  });

  // Response interceptor
  apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
      const { refreshToken, setTokens, logout } = useAuthStore.getState();

      if (error.response?.status === 401 && refreshToken) {
        try {
          const response = await axios.post(
            `${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/refresh`,
            { refresh_token: refreshToken }
          );
          
          setTokens(response.data.access_token, response.data.refresh_token);
          
          // Retry original request
          error.config.headers.Authorization = `Bearer ${response.data.access_token}`;
          return apiClient(error.config);
        } catch (refreshError) {
          logout();
          window.location.href = '/login';
        }
      }

      return Promise.reject(error);
    }
  );

  return apiClient;
};

export const getApiClient = () => {
  if (!apiClient) {
    initializeApiClient();
  }
  return apiClient;
};

export default getApiClient;
