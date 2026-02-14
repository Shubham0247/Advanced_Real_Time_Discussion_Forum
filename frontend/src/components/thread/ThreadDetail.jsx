import PropTypes from "prop-types";
import { Heart, Edit3, Trash2, Lock } from "lucide-react";
import Avatar from "../common/Avatar";
import { formatFullDate } from "../../utils/formatDate";
import MentionText from "../mention/MentionText";

/**
 * Displays the thread header: author, title, description, and action buttons.
 */
export default function ThreadDetail({
  thread,
  canEdit,
  onLike,
  likeLoading,
  onEdit,
  onDelete,
}) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 p-6">
      <div className="flex items-start gap-3">
        <Avatar
          name={thread.author_name || thread.author_username || "User"}
          avatarUrl={thread.author_avatar}
          size="md"
        />
        <div className="flex-1 min-w-0">
          <h1 className="text-xl font-bold text-gray-900">{thread.title}</h1>
          <p className="text-xs text-gray-400 mt-1">
            {thread.author_username || "User"} &middot;{" "}
            {formatFullDate(thread.created_at)}
            {thread.is_locked && (
              <span className="inline-flex items-center gap-1 ml-2 text-amber-600">
                <Lock size={12} /> Locked
              </span>
            )}
          </p>
        </div>
      </div>

      {thread.description && (
        <MentionText
          text={thread.description}
          className="mt-4 text-sm text-gray-700 whitespace-pre-wrap leading-relaxed block"
        />
      )}

      {/* Actions */}
      <div className="flex items-center gap-3 mt-5 pt-4 border-t border-gray-100">
        <button
          onClick={onLike}
          disabled={likeLoading}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors
            ${
              thread.is_liked_by_current_user
                ? "bg-red-50 text-red-600"
                : "bg-gray-50 text-gray-600 hover:bg-gray-100"
            }`}
        >
          <Heart
            size={16}
            className={thread.is_liked_by_current_user ? "fill-red-500" : ""}
          />
          {thread.like_count ?? 0}
        </button>

        {canEdit && (
          <>
            <button
              onClick={onEdit}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm text-gray-500 hover:bg-gray-100 transition-colors"
            >
              <Edit3 size={15} /> Edit
            </button>
            <button
              onClick={onDelete}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm text-red-500 hover:bg-red-50 transition-colors"
            >
              <Trash2 size={15} /> Delete
            </button>
          </>
        )}
      </div>
    </div>
  );
}

ThreadDetail.propTypes = {
  thread: PropTypes.object.isRequired,
  canEdit: PropTypes.bool,
  onLike: PropTypes.func.isRequired,
  likeLoading: PropTypes.bool,
  onEdit: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
};
