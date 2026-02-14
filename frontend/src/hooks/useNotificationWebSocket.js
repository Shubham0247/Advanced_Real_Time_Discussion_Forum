import { useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import useWebSocket from "./useWebSocket";
import useNotificationStore from "../stores/notificationStore";
import { WS_URLS } from "../utils/constants";
import { tokenStorage } from "../utils/tokenStorage";

/**
 * Global notification WebSocket.
 * Should be mounted once at App level for logged-in users.
 * Receives live events and updates the notification bell badge.
 */
export default function useNotificationWebSocket() {
  const queryClient = useQueryClient();
  const { increment } = useNotificationStore();
  const token = tokenStorage.getAccessToken();

  const url = token ? WS_URLS.NOTIFICATIONS(token) : null;

  const handleMessage = useCallback(
    (data) => {
      increment();
      queryClient.invalidateQueries({ queryKey: ["notifications"] });

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
    [increment, queryClient]
  );

  useWebSocket(url, handleMessage);
}
