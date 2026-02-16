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
  initialImageUrl = "",
  onSubmit,
  loading = false,
  onCancel,
  submitLabel = "Create Thread",
}) {
  const [title, setTitle] = useState(initialTitle);
  const [description, setDescription] = useState(initialDescription);
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(initialImageUrl);
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
    onSubmit({ title, description, imageFile });
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

      <div>
        <label
          htmlFor="thread_image"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Image (optional)
        </label>
        <input
          id="thread_image"
          type="file"
          accept="image/png,image/jpeg,image/jpg,image/webp,image/gif"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (!file) return;
            setImageFile(file);
            setImagePreview(URL.createObjectURL(file));
          }}
          className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm
            file:mr-4 file:rounded-md file:border-0 file:bg-indigo-50 file:px-3 file:py-1.5
            file:text-xs file:font-medium file:text-indigo-600 hover:file:bg-indigo-100
            focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
        {imagePreview && (
          <img
            src={imagePreview}
            alt="Thread preview"
            className="mt-2 max-h-64 w-full object-cover rounded-lg border border-gray-100"
          />
        )}
      </div>

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
  initialImageUrl: PropTypes.string,
  onSubmit: PropTypes.func.isRequired,
  loading: PropTypes.bool,
  onCancel: PropTypes.func,
  submitLabel: PropTypes.string,
};
