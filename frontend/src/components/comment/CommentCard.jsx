import { useEffect, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Heart, Reply, Edit3, Trash2 } from "lucide-react";
import PropTypes from "prop-types";
import toast from "react-hot-toast";
import { updateComment, deleteComment } from "../../api/commentApi";
import { toggleCommentLike } from "../../api/likeApi";
import useAuthStore from "../../stores/authStore";
import Avatar from "../common/Avatar";
import Button from "../common/Button";
import { formatDate } from "../../utils/formatDate";
import MentionText from "../mention/MentionText";
import MentionInput from "../mention/MentionInput";

const MAX_DEPTH = 4;

export default function CommentCard({
  comment,
  threadId,
  threadAuthorId,
  onReply,
  depth = 0,
}) {
  const { user, hasRole } = useAuthStore();
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [editText, setEditText] = useState(comment.content);
  const [replying, setReplying] = useState(false);
  const [replyText, setReplyText] = useState("");
  const [replySubmitting, setReplySubmitting] = useState(false);

  const isOwner = user && String(comment.author_id) === String(user.id);
  const isThreadOwner = user && String(threadAuthorId) === String(user.id);
  const canModerate = hasRole("admin") || hasRole("moderator");
  const canEdit = isOwner || canModerate; // thread owner can delete, not edit
  const canDelete = isOwner || canModerate || isThreadOwner;
  const isDeleted = !!comment.is_deleted;

  const likeMutation = useMutation({
    mutationFn: () => toggleCommentLike(comment.id),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["comments", threadId] }),
  });

  const editMutation = useMutation({
    mutationFn: () => updateComment(comment.id, { content: editText }),
    onSuccess: () => {
      setEditing(false);
      queryClient.invalidateQueries({ queryKey: ["comments", threadId] });
      toast.success("Comment updated");
    },
    onError: (err) =>
      toast.error(err.response?.data?.detail || "Failed to update"),
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteComment(comment.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["comments", threadId] });
      toast.success("Comment deleted");
    },
  });

  useEffect(() => {
    if (!replying) return;
    const replyInput = document.getElementById(`reply-input-${comment.id}`);
    if (replyInput) {
      replyInput.focus();
    }
  }, [replying, comment.id]);

  const handleReplySubmit = async () => {
    if (!replyText.trim() || replySubmitting) return;

    try {
      setReplySubmitting(true);
      await onReply(comment.id, replyText.trim());
      setReplyText("");
      setReplying(false);
    } catch {
      // Error toast is handled by the shared comment mutation hook.
    } finally {
      setReplySubmitting(false);
    }
  };

  return (
    <div
      className={`${
        depth > 0 ? "ml-6 pl-4 border-l-2 border-gray-200" : ""
      }`}
    >
      <div className="bg-white rounded-xl p-4 border border-gray-200 shadow-sm">
        {/* Header */}
        <div className="flex items-center gap-2 mb-2">
          <Avatar
            name={comment.author_name || comment.author_username || "User"}
            avatarUrl={comment.author_avatar}
            size="sm"
          />
          <div>
            <span className="text-sm font-semibold text-gray-900">
              {comment.author_username || "User"}
            </span>
            <span className="text-xs text-gray-400 ml-2">
              {formatDate(comment.created_at)}
            </span>
          </div>
        </div>

        {/* Content */}
        {editing && !isDeleted ? (
          <div className="mt-2">
            <textarea
              rows={3}
              value={editText}
              onChange={(e) => setEditText(e.target.value)}
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm
                focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 resize-y"
            />
            <div className="flex gap-2 mt-2">
              <Button
                size="sm"
                onClick={() => editMutation.mutate()}
                loading={editMutation.isPending}
              >
                Save
              </Button>
              <Button
                size="sm"
                variant="secondary"
                onClick={() => {
                  setEditing(false);
                  setEditText(comment.content);
                }}
              >
                Cancel
              </Button>
            </div>
          </div>
        ) : isDeleted ? (
          <p className="text-sm text-gray-400 italic whitespace-pre-wrap">
            {comment.content || "This message has been deleted"}
          </p>
        ) : (
          <MentionText text={comment.content} className="text-sm text-gray-700 whitespace-pre-wrap block leading-6" />
        )}

        {/* Actions */}
        {!editing && !isDeleted && (
          <div className="flex items-center gap-2 mt-3">
            <button
              onClick={() => likeMutation.mutate()}
              disabled={likeMutation.isPending}
              className={`flex items-center gap-1 px-2 py-1 rounded text-xs font-medium transition-colors
                ${
                  comment.is_liked_by_current_user
                    ? "text-red-600 bg-red-50 border border-red-100"
                    : "text-gray-600 border border-gray-200 hover:bg-gray-50"
                }`}
            >
              <Heart
                size={13}
                className={
                  comment.is_liked_by_current_user ? "fill-red-500" : ""
                }
              />
              {comment.like_count ?? 0}
            </button>

            {depth < MAX_DEPTH && (
              <button
                onClick={() => setReplying((prev) => !prev)}
                className="flex items-center gap-1 px-2 py-1 rounded text-xs text-gray-600 border border-gray-200 hover:bg-gray-50 transition-colors"
              >
                <Reply size={13} /> Reply
              </button>
            )}

            {canEdit && (
              <>
                <button
                  onClick={() => setEditing(true)}
                  className="flex items-center gap-1 px-2 py-1 rounded text-xs text-gray-600 border border-gray-200 hover:bg-gray-50"
                >
                  <Edit3 size={13} /> Edit
                </button>
              </>
            )}
            {canDelete && (
              <>
                <button
                  onClick={() => {
                    if (confirm("Delete this comment?"))
                      deleteMutation.mutate();
                  }}
                  className="flex items-center gap-1 px-2 py-1 rounded text-xs text-red-600 border border-red-200 hover:bg-red-50"
                >
                  <Trash2 size={13} /> Delete
                </button>
              </>
            )}
          </div>
        )}

        {replying && depth < MAX_DEPTH && (
          <div className="mt-3 border-t border-gray-100 pt-3">
            <MentionInput
              id={`reply-input-${comment.id}`}
              placeholder="Write a reply... Use @username to mention someone"
              value={replyText}
              onChange={setReplyText}
              rows={2}
            />
            <div className="flex justify-end gap-2 mt-2">
              <Button
                type="button"
                size="sm"
                variant="secondary"
                onClick={() => {
                  setReplying(false);
                  setReplyText("");
                }}
              >
                Cancel
              </Button>
              <Button
                type="button"
                size="sm"
                onClick={handleReplySubmit}
                loading={replySubmitting}
                disabled={!replyText.trim()}
              >
                Post Reply
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Nested replies */}
      {comment.replies && comment.replies.length > 0 && (
        <div className="mt-2 space-y-2">
          {comment.replies.map((reply) => (
            <CommentCard
              key={reply.id}
              comment={reply}
              threadId={threadId}
              onReply={onReply}
              threadAuthorId={threadAuthorId}
              depth={depth + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}

CommentCard.propTypes = {
  comment: PropTypes.object.isRequired,
  threadId: PropTypes.string.isRequired,
  threadAuthorId: PropTypes.string,
  onReply: PropTypes.func.isRequired,
  depth: PropTypes.number,
};
