import PropTypes from "prop-types";
import Button from "../common/Button";
import MentionInput from "../mention/MentionInput";

/**
 * Form for posting or replying to a comment.
 */
export default function CommentForm({
  value,
  onChange,
  onSubmit,
  loading = false,
}) {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!value.trim()) return;
    onSubmit();
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="mt-6 bg-white rounded-xl border border-gray-100 p-4"
    >
      <MentionInput
        id="comment-input"
        placeholder="Write a comment... Use @username to mention someone"
        value={value}
        onChange={onChange}
        rows={3}
      />

      <div className="flex justify-end mt-3">
        <Button
          type="submit"
          size="sm"
          loading={loading}
          disabled={!value.trim()}
        >
          Post Comment
        </Button>
      </div>
    </form>
  );
}

CommentForm.propTypes = {
  value: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  loading: PropTypes.bool,
};
