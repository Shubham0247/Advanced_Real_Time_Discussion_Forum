import { authClient } from "./axiosClient";

/**
 * Register a new user.
 * @param {{ username: string, email: string, full_name: string, password: string, avatar_url?: string, bio?: string }} payload
 */
export const register = (payload) =>
  authClient.post("/auth/register", payload).then((r) => r.data);

/**
 * Log in with email + password.
 * @param {{ email: string, password: string }} payload
 */
export const login = (payload) =>
  authClient.post("/auth/login", payload).then((r) => r.data);

/**
 * Refresh access token.
 * @param {string} refreshToken
 */
export const refreshToken = (refreshToken) =>
  authClient
    .post("/auth/refresh", { refresh_token: refreshToken })
    .then((r) => r.data);

/**
 * Request a password reset OTP.
 * @param {string} email
 */
export const forgotPassword = (email) =>
  authClient.post("/auth/forgot-password", { email }).then((r) => r.data);

/**
 * Reset password using email + OTP.
 * @param {{ email: string, otp: string, new_password: string }} payload
 */
export const resetPassword = (payload) =>
  authClient.post("/auth/reset-password", payload).then((r) => r.data);

/**
 * Get current authenticated user profile.
 */
export const getMe = () => authClient.get("/users/me").then((r) => r.data);

/**
 * Update current user profile.
 * @param {{ full_name?: string, avatar_url?: string, bio?: string }} payload
 */
export const updateProfile = (payload) =>
  authClient.patch("/users/me", payload).then((r) => r.data);

/**
 * Change current user's password.
 * @param {{ current_password: string, new_password: string }} payload
 */
export const changeMyPassword = (payload) =>
  authClient.post("/users/me/change-password", payload).then((r) => r.data);

/**
 * Deactivate current user's account.
 */
export const deactivateMyAccount = () =>
  authClient.post("/users/me/deactivate").then((r) => r.data);

/**
 * Upload avatar image from local device.
 * @param {File} file
 */
export const uploadAvatar = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return authClient
    .post("/users/me/avatar", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    })
    .then((r) => r.data);
};

/**
 * Mention autocomplete suggestions.
 * @param {string} q
 * @param {number} limit
 */
export const suggestMentionUsers = (q, limit = 8) =>
  authClient
    .get("/users/mentions/suggest", { params: { q, limit } })
    .then((r) => r.data);

/**
 * Resolve which @usernames actually exist.
 * @param {string[]} usernames
 */
export const resolveMentions = (usernames) =>
  authClient.post("/users/mentions/resolve", { usernames }).then((r) => r.data);

/**
 * Search users (public searchable fields).
 */
export const searchUsers = ({ q, page = 1, size = 10 }) =>
  authClient.get("/users/search", { params: { q, page, size } }).then((r) => r.data);

// ---- Admin endpoints ----

/**
 * List all users (admin only).
 */
export const adminListUsers = ({ page = 1, size = 20, q, role } = {}) => {
  const params = { page, size };
  if (q) params.q = q;
  if (role) params.role = role;
  return authClient.get("/users/admin/list", { params }).then((r) => r.data);
};

/**
 * Activate or deactivate a user (admin only).
 */
export const adminUpdateUserStatus = (userId, isActive) =>
  authClient
    .patch(`/users/${userId}/status`, { is_active: isActive })
    .then((r) => r.data);

/**
 * Promote a user to a role (admin only).
 */
export const adminPromoteUser = (userId, roleName) =>
  authClient
    .post(`/users/${userId}/promote`, null, { params: { role_name: roleName } })
    .then((r) => r.data);

/**
 * Demote a user from a role (admin only).
 */
export const adminDemoteUser = (userId, roleName) =>
  authClient
    .post(`/users/${userId}/demote`, null, { params: { role_name: roleName } })
    .then((r) => r.data);
