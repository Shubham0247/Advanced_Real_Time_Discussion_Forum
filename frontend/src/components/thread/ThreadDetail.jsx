import PropTypes from "prop-types";
import {
  Heart,
  Edit3,
  Trash2,
  Lock,
  ChevronDown,
  MoreVertical,
  Flag,
  Share2,
} from "lucide-react";
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import toast from "react-hot-toast";
import Avatar from "../common/Avatar";
import { formatFullDate } from "../../utils/formatDate";
import { reportThread } from "../../api/moderationApi";
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
  likers = [],
  likersLoading = false,
}) {
  const [showLikers, setShowLikers] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  const reportMutation = useMutation({
    mutationFn: (reason) => reportThread(thread.id, reason),
    onSuccess: () => toast.success("Thread reported"),
    onError: (err) =>
      toast.error(err.response?.data?.detail || "Could not report thread"),
  });

  const handleShare = async () => {
    const url = `${window.location.origin}/threads/${thread.id}`;
    try {
      await navigator.clipboard.writeText(url);
      toast.success("Thread link copied");
    } catch {
      toast.error("Could not copy link");
    } finally {
      setMenuOpen(false);
    }
  };

  const handleReport = () => {
    const reason = window.prompt("Why are you reporting this thread? (optional)", "");
    if (reason === null) {
      setMenuOpen(false);
      return;
    }
    reportMutation.mutate(reason.trim());
    setMenuOpen(false);
  };

  return (
    <div className="relative bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
      <div className="absolute top-4 right-4 z-20">
        <button
          onClick={() => setMenuOpen((v) => !v)}
          className="p-1.5 rounded-md text-gray-400 hover:bg-gray-100 hover:text-gray-600"
          title="More options"
        >
          <MoreVertical size={16} />
        </button>
        {menuOpen && (
          <div className="absolute right-0 mt-1 w-36 bg-white border border-gray-200 rounded-lg shadow-lg py-1">
            <button
              onClick={handleReport}
              disabled={reportMutation.isPending}
              className="w-full px-3 py-2 text-sm text-left text-gray-700 hover:bg-gray-50 flex items-center gap-2"
            >
              <Flag size={14} /> Report
            </button>
            <button
              onClick={handleShare}
              className="w-full px-3 py-2 text-sm text-left text-gray-700 hover:bg-gray-50 flex items-center gap-2"
            >
              <Share2 size={14} /> Share
            </button>
          </div>
        )}
      </div>

      <div className="flex items-start gap-3.5">
        <Avatar
          name={thread.author_name || thread.author_username || "User"}
          avatarUrl={thread.author_avatar}
          size="md"
        />
        <div className="flex-1 min-w-0">
          <h1 className="text-[1.35rem] font-semibold tracking-tight text-gray-900">{thread.title}</h1>
          <p className="text-xs text-gray-500 mt-1">
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
          className="mt-4 text-sm text-gray-700 whitespace-pre-wrap leading-7 block"
        />
      )}
      {thread.image_url && (
        <img
          src={thread.image_url}
          alt={thread.title}
          className="mt-4 w-full max-h-[28rem] object-cover rounded-xl border border-gray-200"
        />
      )}

      {/* Actions */}
      <div className="flex items-center gap-3 mt-5 pt-4 border-t border-gray-200">
        <div className="relative">
          <div className="flex items-center">
            <button
              onClick={onLike}
              disabled={likeLoading}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-l-lg text-sm font-medium transition-colors
                ${
                  thread.is_liked_by_current_user
                    ? "bg-red-50 border border-red-100 text-red-600"
                    : "bg-gray-50 border border-gray-200 text-gray-600 hover:bg-gray-100"
                }`}
            >
              <Heart
                size={16}
                className={thread.is_liked_by_current_user ? "fill-red-500" : ""}
              />
              {thread.like_count ?? 0}
            </button>
            <button
              onClick={() => setShowLikers((v) => !v)}
              className="px-2 py-1.5 rounded-r-lg text-sm text-gray-600 bg-gray-50 border-y border-r border-gray-200 hover:bg-gray-100"
              title="View users who liked this thread"
            >
              <ChevronDown size={14} />
            </button>
          </div>

          {showLikers && (
            <div className="absolute z-30 mt-1 w-64 bg-white rounded-xl shadow-lg border border-gray-200 p-2">
              <p className="text-xs font-medium text-gray-500 px-2 py-1">
                Liked by
              </p>
              {likersLoading ? (
                <p className="text-sm text-gray-500 px-2 py-2">Loading...</p>
              ) : likers.length === 0 ? (
                <p className="text-sm text-gray-500 px-2 py-2">No likes yet</p>
              ) : (
                <div className="max-h-56 overflow-y-auto">
                  {likers.map((u) => (
                    <div key={u.id} className="flex items-center gap-2 px-2 py-1.5">
                      <Avatar
                        name={u.full_name || u.username}
                        avatarUrl={u.avatar_url}
                        size="sm"
                      />
                      <div className="min-w-0">
                        <p className="text-sm text-gray-800 truncate">{u.full_name || u.username}</p>
                        <p className="text-xs text-gray-500 truncate">@{u.username}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {canEdit && (
          <>
            <button
              onClick={onEdit}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm text-gray-600 border border-gray-200 hover:bg-gray-50 transition-colors"
            >
              <Edit3 size={15} /> Edit
            </button>
            <button
              onClick={onDelete}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm text-red-600 border border-red-200 hover:bg-red-50 transition-colors"
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
  likers: PropTypes.array,
  likersLoading: PropTypes.bool,
};
