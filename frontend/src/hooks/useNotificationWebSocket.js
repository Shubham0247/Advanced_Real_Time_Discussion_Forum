import { useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import useWebSocket from "./useWebSocket";
import useNotificationStore from "../stores/notificationStore";
import { WS_URLS } from "../utils/constants";
import { tokenStorage } from "../utils/tokenStorage";
import { getUnreadCount } from "../api/notificationApi";

/**
 * Global notification WebSocket.
 * Should be mounted once at App level for logged-in users.
 * Receives live events and updates the notification bell badge.
 */
export default function useNotificationWebSocket() {
  const queryClient = useQueryClient();
  const { setUnreadCount } = useNotificationStore();
  const token = tokenStorage.getAccessToken();

  const url = token ? WS_URLS.NOTIFICATIONS(token) : null;

  const handleMessage = useCallback(
    async (data) => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["unread-count"] });

      // Always sync unread badge from server to avoid count drift/races.
      try {
        const unreadData = await queryClient.fetchQuery({
          queryKey: ["unread-count"],
          queryFn: getUnreadCount,
          staleTime: 0,
        });
        setUnreadCount(unreadData?.unread_count ?? 0);
      } catch {
        // Ignore transient failures; polling fallback will recover.
      }

      // Show a toast for certain event types
      const msg = data.payload?.message || data.message;
      if (msg) {
        toast(msg, {
          icon: "🔔",
          duration: 4000,
          style: { fontSize: "14px" },
        });
      }
    },
    [queryClient, setUnreadCount]
  );

  useWebSocket(url, handleMessage);
}
