import PropTypes from "prop-types";
import { Bell, Check, AtSign, MessageCircle, Heart } from "lucide-react";
import { formatDate } from "../../utils/formatDate";

const TYPE_CONFIG = {
  mention: { icon: AtSign, color: "text-blue-600 bg-blue-50", label: "Mentioned you" },
  "mention.thread": { icon: AtSign, color: "text-blue-600 bg-blue-50", label: "Mentioned you in thread" },
  "mention.comment": { icon: AtSign, color: "text-blue-600 bg-blue-50", label: "Mentioned you in comment" },
  "comment.replied": { icon: MessageCircle, color: "text-green-600 bg-green-50", label: "Replied to you" },
  "thread.commented": { icon: MessageCircle, color: "text-indigo-600 bg-indigo-50", label: "Commented on your thread" },
  "comment.liked": { icon: Heart, color: "text-pink-500 bg-pink-50", label: "Liked your comment" },
  "thread.liked": { icon: Heart, color: "text-red-500 bg-red-50", label: "Liked your thread" },
  default: { icon: Bell, color: "text-gray-600 bg-gray-50", label: "Notification" },
};

export default function NotificationItem({ notification, onMarkRead, onOpen }) {
  const config = TYPE_CONFIG[notification.type] || TYPE_CONFIG.default;
  const Icon = config.icon;

  return (
    <div
      onClick={() => onOpen(notification)}
      className={`relative flex items-start gap-3 p-4 rounded-xl border transition-colors
        cursor-pointer
        ${
          notification.is_read
            ? "bg-white border-gray-200 hover:border-gray-300"
            : "bg-indigo-50/40 border-indigo-200"
        }`}
    >
      {!notification.is_read && (
        <div className="absolute left-0 top-3 bottom-3 w-1 rounded-r bg-indigo-500" />
      )}
      <div
        className={`flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center ${config.color}`}
      >
        <Icon size={16} />
      </div>

      <div className="flex-1 min-w-0">
        <p className="text-sm text-gray-800 leading-6">{notification.message}</p>
        <p className="text-xs text-gray-400 mt-1">
          {config.label} &middot; {formatDate(notification.created_at)}
        </p>
      </div>

      {!notification.is_read && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onMarkRead(notification.id);
          }}
          className="flex-shrink-0 p-1.5 rounded-lg text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
          title="Mark as read"
        >
          <Check size={16} />
        </button>
      )}
    </div>
  );
}

NotificationItem.propTypes = {
  notification: PropTypes.shape({
    id: PropTypes.string.isRequired,
    type: PropTypes.string,
    reference_id: PropTypes.string,
    message: PropTypes.string,
    is_read: PropTypes.bool,
    created_at: PropTypes.string,
  }).isRequired,
  onMarkRead: PropTypes.func.isRequired,
  onOpen: PropTypes.func.isRequired,
};
