import { discussionClient } from "./axiosClient";

/**
 * Create a new thread.
 * @param {{ title: string, description: string, image_url?: string }} payload
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
 * List current user's threads (paginated).
 */
export const getMyThreads = ({ page = 1, size = 10 } = {}) =>
  discussionClient
    .get("/threads/me", { params: { page, size } })
    .then((r) => r.data);

/**
 * List current user's activity timeline.
 */
export const getMyActivity = ({ range = "all", page = 1, size = 15 } = {}) =>
  discussionClient
    .get("/threads/me/activity", { params: { range, page, size } })
    .then((r) => r.data);

/**
 * List current user's activity timeline with time + type filters.
 */
export const getMyActivityFiltered = ({
  range = "all",
  type = "all",
  page = 1,
  size = 15,
} = {}) =>
  discussionClient
    .get("/threads/me/activity", { params: { range, type, page, size } })
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
 * @param {{ title?: string, description?: string, image_url?: string }} payload
 */
export const updateThread = (threadId, payload) =>
  discussionClient.patch(`/threads/${threadId}`, payload).then((r) => r.data);

/**
 * Delete a thread.
 * @param {string} threadId
 */
export const deleteThread = (threadId) =>
  discussionClient.delete(`/threads/${threadId}`).then((r) => r.data);

/**
 * Upload thread image and return hosted URL.
 * @param {File} file
 */
export const uploadThreadImage = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return discussionClient
    .post("/threads/upload-image", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    })
    .then((r) => r.data);
};
