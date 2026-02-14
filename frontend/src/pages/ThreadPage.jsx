import { useState, useEffect } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import useAuthStore from "../stores/authStore";
import { useThread, useThreadMutations } from "../hooks/useThreads";
import { useCommentList, useCommentMutations, buildCommentTree } from "../hooks/useComments";
import useThreadWebSocket from "../hooks/useThreadWebSocket";
import PageWrapper from "../components/layout/PageWrapper";
import Spinner from "../components/common/Spinner";
import Button from "../components/common/Button";
import Input from "../components/common/Input";
import Modal from "../components/common/Modal";
import ThreadDetail from "../components/thread/ThreadDetail";
import CommentForm from "../components/comment/CommentForm";
import CommentTree from "../components/comment/CommentTree";

export default function ThreadPage() {
  const { threadId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { user, hasRole } = useAuthStore();

  // Realtime updates via WebSocket
  useThreadWebSocket(threadId);

  const [editOpen, setEditOpen] = useState(false);
  const [editForm, setEditForm] = useState({ title: "", description: "" });
  const [commentText, setCommentText] = useState("");
  const [replyTo, setReplyTo] = useState(null);

  // ---- Fetch data ----
  const {
    data: thread,
    isLoading: threadLoading,
    isError: threadError,
  } = useThread(threadId);

  const { comments, isLoading: commentsLoading } = useCommentList(threadId);

  // ---- Mutations ----
  const { updateMutation, deleteMutation, likeMutation } =
    useThreadMutations(threadId);

  const { createMutation: commentMutation } = useCommentMutations(threadId);

  // Scroll to #comments section if URL hash is present
  useEffect(() => {
    if (location.hash === "#comments" && !commentsLoading) {
      const el = document.getElementById("comments");
      if (el) {
        setTimeout(() => el.scrollIntoView({ behavior: "smooth" }), 100);
      }
    }
  }, [location.hash, commentsLoading]);

  // ---- Handlers ----
  const handleEditOpen = () => {
    setEditForm({ title: thread.title, description: thread.description || "" });
    setEditOpen(true);
  };

  const handleEditSubmit = (e) => {
    e.preventDefault();
    updateMutation.mutate(editForm, { onSuccess: () => setEditOpen(false) });
  };

  const handleCommentSubmit = () => {
    const payload = { content: commentText };
    if (replyTo) payload.parent_id = replyTo;
    commentMutation.mutate(payload, {
      onSuccess: () => {
        setCommentText("");
        setReplyTo(null);
      },
    });
  };

  const isOwner = thread && user && String(thread.author_id) === String(user.id);
  const canModerate = hasRole("admin") || hasRole("moderator");
  const canEdit = isOwner || canModerate;

  // ---- Loading / Error states ----
  if (threadLoading) {
    return (
      <PageWrapper>
        <div className="flex justify-center py-16">
          <Spinner size={32} />
        </div>
      </PageWrapper>
    );
  }

  if (threadError || !thread) {
    return (
      <PageWrapper>
        <div className="text-center py-16">
          <p className="text-gray-500">Thread not found or failed to load.</p>
          <Button variant="secondary" className="mt-4" onClick={() => navigate("/")}>
            Go back
          </Button>
        </div>
      </PageWrapper>
    );
  }

  const commentTree = buildCommentTree(comments);

  return (
    <PageWrapper>
      {/* Back button */}
      <button
        onClick={() => navigate("/")}
        className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-4 transition-colors"
      >
        <ArrowLeft size={16} /> Back to discussions
      </button>

      {/* Thread header */}
      <ThreadDetail
        thread={thread}
        canEdit={canEdit}
        onLike={() => likeMutation.mutate()}
        likeLoading={likeMutation.isPending}
        onEdit={handleEditOpen}
        onDelete={() => {
          if (confirm("Delete this thread?")) deleteMutation.mutate();
        }}
      />

      {/* Comment form */}
      {!thread.is_locked && (
        <CommentForm
          value={commentText}
          onChange={setCommentText}
          onSubmit={handleCommentSubmit}
          loading={commentMutation.isPending}
          replyTo={replyTo}
          onCancelReply={() => setReplyTo(null)}
        />
      )}

      {/* Comments */}
      <CommentTree
        comments={commentTree}
        threadId={threadId}
        loading={commentsLoading}
        onReply={(commentId) => {
          setReplyTo(commentId);
          window.scrollTo({ top: 0, behavior: "smooth" });
        }}
      />

      {/* Edit modal */}
      <Modal
        isOpen={editOpen}
        onClose={() => setEditOpen(false)}
        title="Edit Thread"
      >
        <form onSubmit={handleEditSubmit} className="space-y-4">
          <Input
            id="edit-title"
            label="Title"
            value={editForm.title}
            onChange={(e) =>
              setEditForm((prev) => ({ ...prev, title: e.target.value }))
            }
          />
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              rows={4}
              value={editForm.description}
              onChange={(e) =>
                setEditForm((prev) => ({
                  ...prev,
                  description: e.target.value,
                }))
              }
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm
                placeholder-gray-400 resize-y
                focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button
              variant="secondary"
              type="button"
              onClick={() => setEditOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" loading={updateMutation.isPending}>
              Save
            </Button>
          </div>
        </form>
      </Modal>
    </PageWrapper>
  );
}
