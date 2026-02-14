import { discussionClient } from "./axiosClient";

/**
 * List / search threads (admin + moderator).
 */
export const moderationThreads = ({ q, page = 1, size = 20 } = {}) => {
  const params = { page, size };
  if (q) params.q = q;
  return discussionClient
    .get("/moderation/threads", { params })
    .then((r) => r.data);
};

/**
 * List / search comments (admin + moderator).
 */
export const moderationComments = ({ q, page = 1, size = 20 } = {}) => {
  const params = { page, size };
  if (q) params.q = q;
  return discussionClient
    .get("/moderation/comments", { params })
    .then((r) => r.data);
};
