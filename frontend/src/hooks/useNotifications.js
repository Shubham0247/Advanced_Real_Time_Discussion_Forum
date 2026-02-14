import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import {
  getNotifications,
  getUnreadCount,
  markOneRead,
  markAllRead,
} from "../api/notificationApi";
import useNotificationStore from "../stores/notificationStore";

/**
 * Hook for paginated notification list.
 */
export function useNotificationList(page, size = 15) {
  return useQuery({
    queryKey: ["notifications", page],
    queryFn: () => getNotifications({ page, size }),
  });
}

/**
 * Hook for unread count (used by the bell).
 */
export function useUnreadCount(enabled = true) {
  return useQuery({
    queryKey: ["unread-count"],
    queryFn: getUnreadCount,
    enabled,
    refetchInterval: 30000,
  });
}

/**
 * Hook for notification mutations (mark one, mark all).
 */
export function useNotificationMutations() {
  const queryClient = useQueryClient();
  const { setUnreadCount } = useNotificationStore();

  const markOneMutation = useMutation({
    mutationFn: markOneRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      setUnreadCount((c) => Math.max(0, c - 1));
    },
  });

  const markAllMutation = useMutation({
    mutationFn: markAllRead,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      setUnreadCount(0);
      toast.success(`${data.updated_count} notifications marked as read`);
    },
  });

  return { markOneMutation, markAllMutation };
}
