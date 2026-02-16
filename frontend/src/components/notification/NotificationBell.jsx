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
      className="relative rounded-xl border border-transparent p-2 text-gray-900 transition-colors hover:border-gray-200 hover:bg-gray-100 dark:text-slate-100 dark:hover:border-slate-700 dark:hover:bg-slate-800"
    >
      <Bell size={20} />
      {unreadCount > 0 && (
        <span className="absolute -top-0.5 -right-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white ring-2 ring-white dark:ring-slate-900">
          {unreadCount > 99 ? "99+" : unreadCount}
        </span>
      )}
    </Link>
  );
}
