import { discussionClient } from "./axiosClient";

/**
 * Create a new thread.
 * @param {{ title: string, description: string }} payload
 */
export const createThread = (payload) =>
  discussionClient.post("/threads/", payload).then((r) => r.data);

/**
 * List threads (paginated).
 */
export const getThreads = ({ page = 1, size = 10 } = {}) =>
  discussionClient
    .get("/threads/", { params: { page, size } })
    .then((r) => r.data);

/**
 * Search threads by keyword.
 */
export const searchThreads = ({ q, page = 1, size = 10 }) =>
  discussionClient
    .get("/threads/search", { params: { q, page, size } })
    .then((r) => r.data);

/**
 * Get a single thread by ID.
 * @param {string} threadId
 */
export const getThread = (threadId) =>
  discussionClient.get(`/threads/${threadId}`).then((r) => r.data);

/**
 * Update a thread.
 * @param {string} threadId
 * @param {{ title?: string, description?: string }} payload
 */
export const updateThread = (threadId, payload) =>
  discussionClient.patch(`/threads/${threadId}`, payload).then((r) => r.data);

/**
 * Delete a thread.
 * @param {string} threadId
 */
export const deleteThread = (threadId) =>
  discussionClient.delete(`/threads/${threadId}`).then((r) => r.data);
