import axios from "axios";
import { API_URLS } from "../utils/constants";
import { tokenStorage } from "../utils/tokenStorage";

/**
 * Create an Axios instance for a specific backend service.
 * Automatically attaches the access token and handles 401 refresh.
 */
function createClient(baseURL) {
  const client = axios.create({
    baseURL,
    headers: { "Content-Type": "application/json" },
  });

  // ---------- request: attach token ----------
  client.interceptors.request.use(
    (config) => {
      const token = tokenStorage.getAccessToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // ---------- response: auto-refresh on 401 ----------
  let isRefreshing = false;
  let failedQueue = [];

  const processQueue = (error, token = null) => {
    failedQueue.forEach((prom) => {
      if (error) prom.reject(error);
      else prom.resolve(token);
    });
    failedQueue = [];
  };

  client.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;

      // Only try refresh for 401, and not on the refresh endpoint itself
      if (
        error.response?.status !== 401 ||
        originalRequest._retry ||
        originalRequest.url?.includes("/auth/refresh") ||
        originalRequest.url?.includes("/auth/login")
      ) {
        return Promise.reject(error);
      }

      if (isRefreshing) {
        // Queue this request until refresh completes
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return client(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const refreshToken = tokenStorage.getRefreshToken();
        if (!refreshToken) throw new Error("No refresh token");

        const { data } = await axios.post(`${API_URLS.AUTH}/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const newAccess = data.access_token;
        const newRefresh = data.refresh_token || refreshToken;
        tokenStorage.setTokens(newAccess, newRefresh);

        processQueue(null, newAccess);

        originalRequest.headers.Authorization = `Bearer ${newAccess}`;
        return client(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        tokenStorage.clearTokens();

        // Redirect to login
        window.location.href = "/login";
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }
  );

  return client;
}

// One client per backend service
export const authClient = createClient(API_URLS.AUTH);
export const discussionClient = createClient(API_URLS.DISCUSSION);
export const notificationClient = createClient(API_URLS.NOTIFICATION);
