import { discussionClient } from "./axiosClient";

/**
 * List / search threads (admin + moderator).
 */
export const moderationThreads = ({ q, status, page = 1, size = 20 } = {}) => {
  const params = { page, size };
  if (q) params.q = q;
  if (status) params.status = status;
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

/**
 * List thread reports by status for moderation.
 */
export const moderationReports = ({
  status = "reported",
  q,
  page = 1,
  size = 20,
} = {}) => {
  const params = { status, page, size };
  if (q) params.q = q;
  return discussionClient
    .get("/moderation/reports", { params })
    .then((r) => r.data);
};

/**
 * Update moderation status of a report.
 */
export const updateReportStatus = (reportId, status) =>
  discussionClient
    .patch(`/moderation/reports/${reportId}/status`, { status })
    .then((r) => r.data);

/**
 * Update moderation status of a thread.
 */
export const updateThreadModerationStatus = (threadId, status) =>
  discussionClient
    .patch(`/moderation/threads/${threadId}/status`, { status })
    .then((r) => r.data);

/**
 * Report a thread.
 */
export const reportThread = (threadId, reason) =>
  discussionClient
    .post(`/threads/${threadId}/report`, { reason })
    .then((r) => r.data);
