import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import { Heart, MessageCircle, Clock, MoreVertical, Flag, Share2 } from "lucide-react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import PropTypes from "prop-types";
import toast from "react-hot-toast";
import Avatar from "../common/Avatar";
import { formatDate } from "../../utils/formatDate";
import { toggleThreadLike } from "../../api/likeApi";
import { reportThread } from "../../api/moderationApi";
import MentionText from "../mention/MentionText";

export default function ThreadCard({ thread }) {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const likeMutation = useMutation({
    mutationFn: () => toggleThreadLike(thread.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["threads"] });
    },
  });

  const reportMutation = useMutation({
    mutationFn: (reason) => reportThread(thread.id, reason),
    onSuccess: () => {
      toast.success("Thread reported");
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Could not report thread");
    },
  });

  const handleLike = (e) => {
    e.preventDefault();
    e.stopPropagation();
    likeMutation.mutate();
  };

  const handleCommentClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    navigate(`/threads/${thread.id}#comments`);
  };

  const handleShare = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    const url = `${window.location.origin}/threads/${thread.id}`;
    try {
      await navigator.clipboard.writeText(url);
      toast.success("Thread link copied");
    } catch {
      const textArea = document.createElement("textarea");
      textArea.value = url;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand("copy");
      document.body.removeChild(textArea);
      toast.success("Thread link copied");
    } finally {
      setMenuOpen(false);
    }
  };

  const handleReport = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const reason = window.prompt("Why are you reporting this thread? (optional)", "");
    if (reason === null) {
      setMenuOpen(false);
      return;
    }
    reportMutation.mutate(reason.trim());
    setMenuOpen(false);
  };

  return (
    <Link
      to={`/threads/${thread.id}`}
      className="relative block rounded-2xl border border-gray-200 bg-white p-5 shadow-sm hover:border-indigo-200 hover:shadow-md transition-all duration-150"
    >
      <div className="absolute top-3 right-3 z-20">
        <button
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setMenuOpen((v) => !v);
          }}
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
          size="sm"
        />
        <div className="flex-1 min-w-0">
          <h3 className="text-[1.02rem] font-semibold leading-6 text-gray-900 truncate">
            {thread.title}
          </h3>
          <p className="text-xs text-gray-500 mt-1 font-medium">
            @{thread.author_username || "user"}
          </p>
          {thread.description && (
            <MentionText
              text={thread.description}
              className="text-sm text-gray-600 mt-1.5 line-clamp-2 block leading-6"
            />
          )}
          {thread.image_url && (
            <img
              src={thread.image_url}
              alt={thread.title}
              className="mt-3 w-full max-h-56 object-cover rounded-xl border border-gray-200"
            />
          )}
          <div className="flex items-center gap-2 sm:gap-3 mt-4 text-xs">
            <span className="flex items-center gap-1 rounded-md bg-gray-50 border border-gray-200 px-2 py-1 text-gray-500">
              <Clock size={13} />
              {formatDate(thread.created_at)}
            </span>
            <button
              onClick={handleLike}
              disabled={likeMutation.isPending}
              className={`flex items-center gap-1 rounded-md border px-2 py-1 transition-colors
                ${
                  thread.is_liked_by_current_user
                    ? "text-red-500 bg-red-50 border-red-100"
                    : "text-gray-500 border-gray-200 hover:text-red-500 hover:bg-red-50 hover:border-red-100"
                }`}
            >
              <Heart
                size={13}
                className={thread.is_liked_by_current_user ? "fill-red-500" : ""}
              />
              {thread.like_count ?? 0}
            </button>
            <button
              onClick={handleCommentClick}
              className="flex items-center gap-1 rounded-md border border-gray-200 px-2 py-1 text-gray-500 hover:text-indigo-600 hover:bg-indigo-50 hover:border-indigo-100 transition-colors"
            >
              <MessageCircle size={13} />
              {thread.comment_count ?? 0}
            </button>
          </div>
        </div>
      </div>
    </Link>
  );
}

ThreadCard.propTypes = {
  thread: PropTypes.shape({
    id: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    description: PropTypes.string,
    author_name: PropTypes.string,
    author_username: PropTypes.string,
    author_avatar: PropTypes.string,
    image_url: PropTypes.string,
    created_at: PropTypes.string,
    like_count: PropTypes.number,
    comment_count: PropTypes.number,
    is_liked_by_current_user: PropTypes.bool,
  }).isRequired,
};
