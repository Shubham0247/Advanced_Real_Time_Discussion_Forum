import { Link, useNavigate } from "react-router-dom";
import { Heart, MessageCircle, Clock } from "lucide-react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import PropTypes from "prop-types";
import Avatar from "../common/Avatar";
import { formatDate } from "../../utils/formatDate";
import { toggleThreadLike } from "../../api/likeApi";
import MentionText from "../mention/MentionText";

export default function ThreadCard({ thread }) {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const likeMutation = useMutation({
    mutationFn: () => toggleThreadLike(thread.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["threads"] });
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

  return (
    <Link
      to={`/threads/${thread.id}`}
      className="block bg-white rounded-xl border border-gray-100 p-5 hover:border-indigo-200 hover:shadow-sm transition-all duration-150"
    >
      <div className="flex items-start gap-3">
        <Avatar
          name={thread.author_name || thread.author_username || "User"}
          avatarUrl={thread.author_avatar}
          size="sm"
        />
        <div className="flex-1 min-w-0">
          <h3 className="text-base font-semibold text-gray-900 truncate">
            {thread.title}
          </h3>
          <p className="text-xs text-gray-500 mt-1">
            @{thread.author_username || "user"}
          </p>
          {thread.description && (
            <MentionText
              text={thread.description}
              className="text-sm text-gray-500 mt-1 line-clamp-2 block"
            />
          )}
          <div className="flex items-center gap-4 mt-3 text-xs text-gray-400">
            <span className="flex items-center gap-1">
              <Clock size={13} />
              {formatDate(thread.created_at)}
            </span>
            <button
              onClick={handleLike}
              disabled={likeMutation.isPending}
              className={`flex items-center gap-1 rounded-md px-1.5 py-0.5 transition-colors
                ${
                  thread.is_liked_by_current_user
                    ? "text-red-500 hover:bg-red-50"
                    : "text-gray-400 hover:text-red-500 hover:bg-red-50"
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
              className="flex items-center gap-1 rounded-md px-1.5 py-0.5 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
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
    created_at: PropTypes.string,
    like_count: PropTypes.number,
    comment_count: PropTypes.number,
    is_liked_by_current_user: PropTypes.bool,
  }).isRequired,
};
