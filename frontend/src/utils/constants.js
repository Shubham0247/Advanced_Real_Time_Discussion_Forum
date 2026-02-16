const normalizeBaseUrl = (url) => String(url || "").replace(/\/+$/, "");

const authBaseUrl = normalizeBaseUrl(
  import.meta.env.VITE_AUTH_URL || "http://localhost:8000"
);
const discussionBaseUrl = normalizeBaseUrl(
  import.meta.env.VITE_DISCUSSION_URL || "http://localhost:8001"
);
const realtimeBaseUrl = normalizeBaseUrl(
  import.meta.env.VITE_REALTIME_URL || "http://localhost:8002"
);
const notificationBaseUrl = normalizeBaseUrl(
  import.meta.env.VITE_NOTIFICATION_URL || "http://localhost:8003"
);
const wsBaseUrl = normalizeBaseUrl(
  import.meta.env.VITE_WS_BASE || "ws://localhost:8002"
);

export const API_URLS = {
  AUTH: authBaseUrl,
  DISCUSSION: discussionBaseUrl,
  REALTIME: realtimeBaseUrl,
  NOTIFICATION: notificationBaseUrl,
};

export const WS_URLS = {
  THREADS: (threadId, token) =>
    `${wsBaseUrl}/ws/threads/${threadId}?token=${token}`,
  FEED: (token) =>
    `${wsBaseUrl}/ws/feed?token=${token}`,
  NOTIFICATIONS: (token) =>
    `${wsBaseUrl}/ws/notifications?token=${token}`,
};

export const ROLES = {
  ADMIN: "admin",
  MODERATOR: "moderator",
  MEMBER: "member",
};

export const PAGE_SIZES = {
  THREADS: 10,
  COMMENTS: 20,
  NOTIFICATIONS: 15,
  ACTIVITY: 15,
  ADMIN_USERS: 20,
};
