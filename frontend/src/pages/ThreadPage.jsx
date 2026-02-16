import { useState, useEffect } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import toast from "react-hot-toast";
import useAuthStore from "../stores/authStore";
import { useThread, useThreadMutations } from "../hooks/useThreads";
import { useCommentList, useCommentMutations, buildCommentTree } from "../hooks/useComments";
import { getThreadLikers } from "../api/likeApi";
import { uploadThreadImage } from "../api/threadApi";
import useThreadWebSocket from "../hooks/useThreadWebSocket";
import PageWrapper from "../components/layout/PageWrapper";
import Spinner from "../components/common/Spinner";
import Button from "../components/common/Button";
import Input from "../components/common/Input";
import Modal from "../components/common/Modal";
import SearchBar from "../components/common/SearchBar";
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
  const [editImageFile, setEditImageFile] = useState(null);
  const [editImagePreview, setEditImagePreview] = useState("");
  const [commentText, setCommentText] = useState("");
  const [commentSearch, setCommentSearch] = useState("");

  // ---- Fetch data ----
  const {
    data: thread,
    isLoading: threadLoading,
    isError: threadError,
  } = useThread(threadId);

  const { comments, isLoading: commentsLoading } = useCommentList(threadId);
  const { data: likersData, isLoading: likersLoading } = useQuery({
    queryKey: ["thread-likers", threadId, thread?.like_count],
    queryFn: () => getThreadLikers(threadId),
    enabled: !!threadId,
  });

  // ---- Mutations ----
  const { updateMutation, deleteMutation, likeMutation } =
    useThreadMutations(threadId);

  const { createMutation: commentMutation } = useCommentMutations(threadId);

  // Scroll to and focus comment input if URL hash is present
  useEffect(() => {
    if (location.hash === "#comments" && !commentsLoading) {
      setTimeout(() => {
        const commentInput = document.getElementById("comment-input");
        if (commentInput) {
          commentInput.scrollIntoView({ behavior: "smooth", block: "center" });
          commentInput.focus();
          const len = commentInput.value?.length ?? 0;
          commentInput.setSelectionRange?.(len, len);
          return;
        }

        const commentsEl = document.getElementById("comments");
        if (commentsEl) {
          commentsEl.scrollIntoView({ behavior: "smooth" });
        }
      }, 100);
    }
  }, [location.hash, commentsLoading]);

  // ---- Handlers ----
  const handleEditOpen = () => {
    setEditForm({ title: thread.title, description: thread.description || "" });
    setEditImageFile(null);
    setEditImagePreview(thread.image_url || "");
    setEditOpen(true);
  };

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    try {
      let image_url = thread.image_url;
      if (editImageFile) {
        const uploaded = await uploadThreadImage(editImageFile);
        image_url = uploaded.image_url;
      }
      updateMutation.mutate(
        { ...editForm, image_url },
        { onSuccess: () => setEditOpen(false) }
      );
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to upload image");
    }
  };

  const handleCommentSubmit = () => {
    commentMutation.mutate({ content: commentText }, {
      onSuccess: () => {
        setCommentText("");
      },
    });
  };

  const handleReplySubmit = async (parentId, content) => {
    await commentMutation.mutateAsync({
      content,
      parent_id: parentId,
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

  const filterCommentTree = (nodes, q) => {
    if (!q) return nodes;
    const needle = q.toLowerCase();

    return nodes
      .map((node) => {
        const filteredReplies = filterCommentTree(node.replies || [], q);
        const selfMatches =
          (node.content || "").toLowerCase().includes(needle) ||
          (node.author_username || "").toLowerCase().includes(needle);

        if (selfMatches || filteredReplies.length > 0) {
          return { ...node, replies: filteredReplies };
        }
        return null;
      })
      .filter(Boolean);
  };

  const visibleCommentTree = filterCommentTree(commentTree, commentSearch);

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
        likers={likersData?.items || []}
        likersLoading={likersLoading}
      />

      {/* Comment form */}
      {!thread.is_locked && (
        <CommentForm
          value={commentText}
          onChange={setCommentText}
          onSubmit={handleCommentSubmit}
          loading={commentMutation.isPending}
        />
      )}

      {/* Comments */}
      <CommentTree
        comments={visibleCommentTree}
        threadId={threadId}
        threadAuthorId={thread?.author_id}
        loading={commentsLoading}
        searchBar={
          <SearchBar
            placeholder="Search comments in this thread..."
            onSearch={setCommentSearch}
            onChangeSearch={setCommentSearch}
            className="mb-3"
          />
        }
        onReply={handleReplySubmit}
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
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Image (optional)
            </label>
            <input
              type="file"
              accept="image/png,image/jpeg,image/jpg,image/webp,image/gif"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (!file) return;
                setEditImageFile(file);
                setEditImagePreview(URL.createObjectURL(file));
              }}
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm
                file:mr-4 file:rounded-md file:border-0 file:bg-indigo-50 file:px-3 file:py-1.5
                file:text-xs file:font-medium file:text-indigo-600 hover:file:bg-indigo-100
                focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
            {editImagePreview && (
              <img
                src={editImagePreview}
                alt="Thread edit preview"
                className="mt-2 max-h-48 w-full object-cover rounded-lg border border-gray-100"
              />
            )}
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
