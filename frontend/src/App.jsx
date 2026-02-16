import { useEffect } from "react";
import { useLocation } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { useQuery } from "@tanstack/react-query";
import AppRoutes from "./routes/AppRoutes";
import Navbar from "./components/layout/Navbar";
import useAuthStore from "./stores/authStore";
import useNotificationStore from "./stores/notificationStore";
import useNotificationWebSocket from "./hooks/useNotificationWebSocket";
import useFeedWebSocket from "./hooks/useFeedWebSocket";
import { getUnreadCount } from "./api/notificationApi";
import { applyTheme, getStoredTheme } from "./utils/theme";

function AppContent() {
  const { isAuthenticated, isLoading, hydrate } = useAuthStore();
  const { setUnreadCount } = useNotificationStore();
  const location = useLocation();

  // Hydrate user on app mount
  useEffect(() => {
    hydrate();
  }, [hydrate]);

  // Apply persisted theme
  useEffect(() => {
    applyTheme(getStoredTheme());
  }, []);

  // Fetch initial unread count
  const { data: unreadData } = useQuery({
    queryKey: ["unread-count"],
    queryFn: getUnreadCount,
    enabled: isAuthenticated,
    refetchInterval: 30000,
  });

  useEffect(() => {
    if (unreadData?.unread_count !== undefined) {
      setUnreadCount(unreadData.unread_count);
    }
  }, [unreadData, setUnreadCount]);

  // Live notification WebSocket
  useNotificationWebSocket();

  // Global feed WebSocket — real-time likes, comments, etc. across all pages
  useFeedWebSocket();

  // Determine if we're on an auth page (no navbar)
  const authPages = ["/login", "/register", "/forgot-password", "/reset-password"];
  const isAuthPage = authPages.some((page) => location.pathname.startsWith(page));

  return (
    <div className="min-h-screen bg-gray-50">
      {isAuthenticated && !isAuthPage && <Navbar />}
      <AppRoutes />
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            borderRadius: "12px",
            padding: "12px 16px",
            fontSize: "14px",
          },
        }}
      />
    </div>
  );
}

export default function App() {
  return <AppContent />;
}
