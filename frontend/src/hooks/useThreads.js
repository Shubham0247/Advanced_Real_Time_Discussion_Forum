import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import {
  getThreads,
  getThread,
  createThread,
  updateThread,
  deleteThread,
  searchThreads,
} from "../api/threadApi";
import { toggleThreadLike } from "../api/likeApi";
import { PAGE_SIZES } from "../utils/constants";

/**
 * Hook for paginated thread list.
 */
export function useThreadList(page) {
  return useQuery({
    queryKey: ["threads", page],
    queryFn: () => getThreads({ page, size: PAGE_SIZES.THREADS }),
    keepPreviousData: true,
  });
}

/**
 * Hook for a single thread by ID.
 */
export function useThread(threadId) {
  return useQuery({
    queryKey: ["thread", threadId],
    queryFn: () => getThread(threadId),
    enabled: !!threadId,
  });
}

/**
 * Hook for searching threads.
 */
export function useThreadSearch(query, page, size = 10) {
  return useQuery({
    queryKey: ["search-threads", query, page],
    queryFn: () => searchThreads({ q: query, page, size }),
    enabled: query.length > 0,
  });
}

/**
 * Hook for thread mutations (create, update, delete, like).
 */
export function useThreadMutations(threadId) {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const createMutation = useMutation({
    mutationFn: createThread,
    onSuccess: (data) => {
      toast.success("Thread created!");
      navigate(`/threads/${data.id}`);
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Failed to create thread");
    },
  });

  const updateMutation = useMutation({
    mutationFn: (payload) => updateThread(threadId, payload),
    onSuccess: () => {
      toast.success("Thread updated");
      queryClient.invalidateQueries({ queryKey: ["thread", threadId] });
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Failed to update thread");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteThread(threadId),
    onSuccess: () => {
      toast.success("Thread deleted");
      navigate("/");
    },
  });

  const likeMutation = useMutation({
    mutationFn: () => toggleThreadLike(threadId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["thread", threadId] });
      queryClient.invalidateQueries({ queryKey: ["threads"] });
    },
  });

  return { createMutation, updateMutation, deleteMutation, likeMutation };
}
