import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import {
  getComments,
  createComment,
  updateComment,
  deleteComment,
  searchComments,
} from "../api/commentApi";
import { toggleCommentLike } from "../api/likeApi";

/**
 * Hook for fetching comments for a thread.
 */
export function useCommentList(threadId) {
  const query = useQuery({
    queryKey: ["comments", threadId],
    queryFn: () => getComments(threadId),
    enabled: !!threadId,
  });

  const raw = query.data;
  const comments = Array.isArray(raw) ? raw : raw?.items || raw || [];

  return { ...query, comments };
}

/**
 * Hook for searching comments.
 */
export function useCommentSearch(queryStr, page, size = 10) {
  return useQuery({
    queryKey: ["search-comments", queryStr, page],
    queryFn: () => searchComments({ q: queryStr, page, size }),
    enabled: queryStr.length > 0,
  });
}

/**
 * Build a nested comment tree from flat array.
 */
export function buildCommentTree(flatComments) {
  if (!Array.isArray(flatComments) || flatComments.length === 0) {
    return [];
  }

  // Backend currently returns a nested tree for thread comments.
  // If replies are already present, keep that structure as-is.
  const alreadyNested = flatComments.some(
    (comment) => Array.isArray(comment.replies) && comment.replies.length > 0
  );
  if (alreadyNested) {
    return flatComments;
  }

  const map = {};
  const roots = [];
  flatComments.forEach((comment) => {
    map[comment.id] = { ...comment, replies: [] };
  });
  flatComments.forEach((comment) => {
    if (comment.parent_id && map[comment.parent_id]) {
      map[comment.parent_id].replies.push(map[comment.id]);
    } else {
      roots.push(map[comment.id]);
    }
  });
  return roots;
}

/**
 * Hook for comment mutations (create, update, delete, like).
 */
export function useCommentMutations(threadId) {
  const queryClient = useQueryClient();

  const invalidateComments = () => {
    queryClient.invalidateQueries({ queryKey: ["comments", threadId] });
    queryClient.invalidateQueries({ queryKey: ["thread", threadId] });
  };

  const createMutation = useMutation({
    mutationFn: (payload) => createComment(threadId, payload),
    onSuccess: invalidateComments,
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Failed to post comment");
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ commentId, content }) =>
      updateComment(commentId, { content }),
    onSuccess: () => {
      invalidateComments();
      toast.success("Comment updated");
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Failed to update");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (commentId) => deleteComment(commentId),
    onSuccess: () => {
      invalidateComments();
      toast.success("Comment deleted");
    },
  });

  const likeMutation = useMutation({
    mutationFn: (commentId) => toggleCommentLike(commentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["comments", threadId] });
    },
  });

  return { createMutation, updateMutation, deleteMutation, likeMutation };
}
