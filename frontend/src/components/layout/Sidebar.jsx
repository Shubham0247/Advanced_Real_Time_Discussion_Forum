import { Link, useLocation } from "react-router-dom";
import {
  MessageSquare,
  Search,
  Bell,
  User,
  Shield,
  ShieldCheck,
} from "lucide-react";
import PropTypes from "prop-types";
import useAuthStore from "../../stores/authStore";
import useNotificationStore from "../../stores/notificationStore";

const NAV_ITEMS = [
  { to: "/", icon: MessageSquare, label: "Threads" },
  { to: "/search", icon: Search, label: "Search" },
  { to: "/notifications", icon: Bell, label: "Notifications", badge: true },
  { to: "/profile", icon: User, label: "Profile" },
];

export default function Sidebar({ className = "" }) {
  const location = useLocation();
  const { hasRole } = useAuthStore();
  const { unreadCount } = useNotificationStore();

  const isAdmin = hasRole("admin");
  const isModerator = hasRole("moderator") || isAdmin;

  const items = [
    ...NAV_ITEMS,
    ...(isModerator
      ? [{ to: "/moderation", icon: ShieldCheck, label: "Moderation" }]
      : []),
    ...(isAdmin
      ? [{ to: "/admin", icon: Shield, label: "Admin" }]
      : []),
  ];

  return (
    <aside className={`w-56 shrink-0 ${className}`}>
      <nav className="space-y-1">
        {items.map((item) => {
          const Icon = item.icon;
          const active = location.pathname === item.to;
          return (
            <Link
              key={item.to}
              to={item.to}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors
                ${
                  active
                    ? "bg-indigo-50 text-indigo-700"
                    : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                }`}
            >
              <Icon size={18} />
              <span className="flex-1">{item.label}</span>
              {item.badge && unreadCount > 0 && (
                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
                  {unreadCount > 99 ? "99+" : unreadCount}
                </span>
              )}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}

Sidebar.propTypes = {
  className: PropTypes.string,
};
