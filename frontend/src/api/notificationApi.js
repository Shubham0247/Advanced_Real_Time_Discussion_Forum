import { notificationClient } from "./axiosClient";

/**
 * Get current user's notifications (paginated).
 */
export const getNotifications = ({ page = 1, size = 15 } = {}) =>
  notificationClient
    .get("/notifications/me", { params: { page, size } })
    .then((r) => r.data);

/**
 * Get unread notification count.
 */
export const getUnreadCount = () =>
  notificationClient
    .get("/notifications/unread-count")
    .then((r) => r.data);

/**
 * Mark a single notification as read.
 * @param {string} notificationId
 */
export const markOneRead = (notificationId) =>
  notificationClient
    .patch(`/notifications/${notificationId}/read`)
    .then((r) => r.data);

/**
 * Mark all notifications as read.
 */
export const markAllRead = () =>
  notificationClient.patch("/notifications/read-all").then((r) => r.data);
