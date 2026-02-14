import { useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import useWebSocket from "./useWebSocket";
import { WS_URLS } from "../utils/constants";
import { tokenStorage } from "../utils/tokenStorage";

/**
 * Connects to the thread-specific WebSocket and updates React Query cache
 * in real-time as events arrive.
 *
 * @param {string} threadId
 */
export default function useThreadWebSocket(threadId) {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const token = tokenStorage.getAccessToken();

  const url = threadId && token ? WS_URLS.THREADS(threadId, token) : null;

  const handleMessage = useCallback(
    (data) => {
      const { event } = data;

      switch (event) {
        case "comment.created":
        case "comment.updated":
        case "comment.deleted":
          queryClient.invalidateQueries({ queryKey: ["comments", threadId] });
          queryClient.invalidateQueries({ queryKey: ["thread", threadId] });
          break;

        case "thread.updated":
          queryClient.invalidateQueries({ queryKey: ["thread", threadId] });
          break;

        case "thread.deleted":
          toast("This thread was deleted", { icon: "🗑️" });
          navigate("/");
          break;

        case "thread.like.updated":
        case "comment.like.updated":
          queryClient.invalidateQueries({ queryKey: ["thread", threadId] });
          queryClient.invalidateQueries({ queryKey: ["comments", threadId] });
          break;

        default:
          break;
      }
    },
    [threadId, queryClient, navigate]
  );

  useWebSocket(url, handleMessage);
}
