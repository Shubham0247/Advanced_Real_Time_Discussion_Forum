export const API_URLS = {
  AUTH: "http://localhost:8000",
  DISCUSSION: "http://localhost:8001",
  REALTIME: "http://localhost:8002",
  NOTIFICATION: "http://localhost:8003",
};

export const WS_URLS = {
  THREADS: (threadId, token) =>
    `ws://localhost:8002/ws/threads/${threadId}?token=${token}`,
  FEED: (token) =>
    `ws://localhost:8002/ws/feed?token=${token}`,
  NOTIFICATIONS: (token) =>
    `ws://localhost:8002/ws/notifications?token=${token}`,
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
  ADMIN_USERS: 20,
};
