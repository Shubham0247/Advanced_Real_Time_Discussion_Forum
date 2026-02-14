import PropTypes from "prop-types";
import { MessageCircle } from "lucide-react";
import CommentCard from "./CommentCard";
import Spinner from "../common/Spinner";
import EmptyState from "../common/EmptyState";

/**
 * Renders the full comment section: heading + tree of nested CommentCards.
 */
export default function CommentTree({
  comments,
  threadId,
  loading,
  onReply,
}) {
  return (
    <div id="comments" className="mt-6 scroll-mt-24">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Comments {comments.length > 0 && `(${comments.length})`}
      </h2>

      {loading ? (
        <div className="flex justify-center py-8">
          <Spinner size={24} />
        </div>
      ) : comments.length === 0 ? (
        <EmptyState
          icon={MessageCircle}
          title="No comments yet"
          description="Be the first to share your thoughts"
        />
      ) : (
        <div className="space-y-3">
          {comments.map((comment) => (
            <CommentCard
              key={comment.id}
              comment={comment}
              threadId={threadId}
              onReply={onReply}
              depth={0}
            />
          ))}
        </div>
      )}
    </div>
  );
}

CommentTree.propTypes = {
  comments: PropTypes.array.isRequired,
  threadId: PropTypes.string.isRequired,
  loading: PropTypes.bool,
  onReply: PropTypes.func.isRequired,
};
