import { Link } from "react-router-dom";
import { Bell } from "lucide-react";
import useNotificationStore from "../../stores/notificationStore";

/**
 * Bell icon with unread badge. Used in the Navbar.
 */
export default function NotificationBell() {
  const { unreadCount } = useNotificationStore();

  return (
    <Link
      to="/notifications"
      className="relative p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors"
    >
      <Bell size={20} />
      {unreadCount > 0 && (
        <span className="absolute -top-0.5 -right-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white ring-2 ring-white">
          {unreadCount > 99 ? "99+" : unreadCount}
        </span>
      )}
    </Link>
  );
}
