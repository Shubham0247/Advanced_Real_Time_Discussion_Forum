import { discussionClient } from "./axiosClient";

/**
 * Create a comment on a thread.
 * @param {string} threadId
 * @param {{ content: string, parent_id?: string }} payload
 */
export const createComment = (threadId, payload) =>
  discussionClient
    .post(`/comments/thread/${threadId}`, payload)
    .then((r) => r.data);

/**
 * Get all comments for a thread.
 * @param {string} threadId
 */
export const getComments = (threadId) =>
  discussionClient.get(`/comments/thread/${threadId}`).then((r) => r.data);

/**
 * Search comments by keyword.
 */
export const searchComments = ({ q, page = 1, size = 10 }) =>
  discussionClient
    .get("/comments/search", { params: { q, page, size } })
    .then((r) => r.data);

/**
 * Update a comment.
 * @param {string} commentId
 * @param {{ content: string }} payload
 */
export const updateComment = (commentId, payload) =>
  discussionClient
    .patch(`/comments/${commentId}`, payload)
    .then((r) => r.data);

/**
 * Delete a comment.
 * @param {string} commentId
 */
export const deleteComment = (commentId) =>
  discussionClient.delete(`/comments/${commentId}`).then((r) => r.data);
