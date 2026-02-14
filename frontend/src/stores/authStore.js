import { create } from "zustand";
import { tokenStorage } from "../utils/tokenStorage";
import { getMe } from "../api/authApi";

/**
 * Global auth state.
 *
 * Usage:
 *   const { user, isAuthenticated, login, logout } = useAuthStore();
 */
const useAuthStore = create((set, get) => ({
  user: null,
  isAuthenticated: !!tokenStorage.getAccessToken(),
  isLoading: true, // true until initial hydration completes

  /**
   * Store tokens and fetch user profile after login.
   */
  login: async (accessToken, refreshToken) => {
    tokenStorage.setTokens(accessToken, refreshToken);
    try {
      const user = await getMe();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch {
      tokenStorage.clearTokens();
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  /**
   * Clear everything and redirect to login.
   */
  logout: () => {
    tokenStorage.clearTokens();
    set({ user: null, isAuthenticated: false, isLoading: false });
  },

  /**
   * On app mount, try to hydrate user from stored token.
   */
  hydrate: async () => {
    const token = tokenStorage.getAccessToken();
    if (!token) {
      set({ isLoading: false });
      return;
    }
    try {
      const user = await getMe();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch {
      tokenStorage.clearTokens();
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  /**
   * Update user object in store (e.g. after profile edit).
   */
  setUser: (user) => set({ user }),

  /**
   * Check if current user has a specific role.
   */
  hasRole: (roleName) => {
    const { user } = get();
    if (!user?.roles) return false;
    return user.roles.some((r) => r.name === roleName);
  },
}));

export default useAuthStore;
