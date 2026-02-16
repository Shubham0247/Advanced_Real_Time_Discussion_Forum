import { discussionClient } from "./axiosClient";

/**
 * Toggle like on a thread.
 * @param {string} threadId
 */
export const toggleThreadLike = (threadId) =>
  discussionClient.post(`/likes/thread/${threadId}`).then((r) => r.data);

/**
 * Toggle like on a comment.
 * @param {string} commentId
 */
export const toggleCommentLike = (commentId) =>
  discussionClient.post(`/likes/comment/${commentId}`).then((r) => r.data);

/**
 * Get users who liked a thread.
 * @param {string} threadId
 */
export const getThreadLikers = (threadId) =>
  discussionClient.get(`/likes/thread/${threadId}/users`).then((r) => r.data);
