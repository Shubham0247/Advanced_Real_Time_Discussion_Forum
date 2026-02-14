import { useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import useWebSocket from "./useWebSocket";
import { WS_URLS } from "../utils/constants";
import { tokenStorage } from "../utils/tokenStorage";

/**
 * Global feed WebSocket — listens to all thread_updates events
 * (likes, new comments, thread edits/deletes) and refreshes
 * the thread list + individual thread caches in real-time.
 *
 * Mount this on the HomePage or at App level.
 */
export default function useFeedWebSocket() {
  const queryClient = useQueryClient();
  const token = tokenStorage.getAccessToken();

  const url = token ? WS_URLS.FEED(token) : null;

  const handleMessage = useCallback(
    (data) => {
      const { event, thread_id } = data;

      switch (event) {
        case "thread.created":
        case "thread.like.updated":
        case "comment.like.updated":
        case "thread.updated":
        case "thread.deleted":
        case "comment.created":
        case "comment.updated":
        case "comment.deleted":
          // Refresh the thread list on the HomePage
          queryClient.invalidateQueries({ queryKey: ["threads"] });
          // Also refresh the individual thread if it's cached
          if (thread_id) {
            queryClient.invalidateQueries({ queryKey: ["thread", thread_id] });
            queryClient.invalidateQueries({ queryKey: ["comments", thread_id] });
          }
          break;
        default:
          break;
      }
    },
    [queryClient]
  );

  useWebSocket(url, handleMessage);
}
