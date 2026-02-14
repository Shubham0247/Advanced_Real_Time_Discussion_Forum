import { useState } from "react";
import PropTypes from "prop-types";
import Input from "../common/Input";
import Button from "../common/Button";
import MentionInput from "../mention/MentionInput";

/**
 * Reusable form for creating or editing a thread.
 */
export default function ThreadForm({
  initialTitle = "",
  initialDescription = "",
  onSubmit,
  loading = false,
  onCancel,
  submitLabel = "Create Thread",
}) {
  const [title, setTitle] = useState(initialTitle);
  const [description, setDescription] = useState(initialDescription);
  const [errors, setErrors] = useState({});

  const validate = () => {
    const e = {};
    if (!title.trim()) e.title = "Title is required";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validate()) return;
    onSubmit({ title, description });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <Input
        id="title"
        label="Title"
        placeholder="What's on your mind?"
        value={title}
        onChange={(e) => {
          setTitle(e.target.value);
          if (errors.title) setErrors((prev) => ({ ...prev, title: "" }));
        }}
        error={errors.title}
        autoFocus
      />

      <MentionInput
        id="description"
        label="Description"
        placeholder="Add details, context, or use @username to mention someone..."
        value={description}
        onChange={setDescription}
        rows={6}
      />

      <div className="flex items-center gap-3 pt-2">
        <Button type="submit" loading={loading}>
          {submitLabel}
        </Button>
        {onCancel && (
          <Button type="button" variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
}

ThreadForm.propTypes = {
  initialTitle: PropTypes.string,
  initialDescription: PropTypes.string,
  onSubmit: PropTypes.func.isRequired,
  loading: PropTypes.bool,
  onCancel: PropTypes.func,
  submitLabel: PropTypes.string,
};
