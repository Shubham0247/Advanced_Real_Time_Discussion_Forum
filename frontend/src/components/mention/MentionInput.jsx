import { useRef } from "react";
import PropTypes from "prop-types";
import useMentions from "../../hooks/useMentions";
import Avatar from "../common/Avatar";

/**
 * Textarea with @mention autocomplete.
 * Drop-in replacement for a plain <textarea>.
 */
export default function MentionInput({
  id,
  label,
  value,
  onChange,
  placeholder = "",
  rows = 3,
}) {
  const textareaRef = useRef(null);
  const {
    suggestions,
    showSuggestions,
    handleInputChange,
    insertMention,
    closeSuggestions,
  } = useMentions();

  const handleChange = (e) => {
    const text = e.target.value;
    onChange(text);
    handleInputChange(text, e.target.selectionStart);
  };

  const handleSelect = (username) => {
    const el = textareaRef.current;
    const newText = insertMention(value, el.selectionStart, username);
    onChange(newText);
    // Refocus the textarea
    setTimeout(() => el?.focus(), 0);
  };

  return (
    <div className="relative">
      {label && (
        <label
          htmlFor={id}
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          {label}
        </label>
      )}
      <textarea
        ref={textareaRef}
        id={id}
        rows={rows}
        placeholder={placeholder}
        value={value}
        onChange={handleChange}
        onBlur={() => setTimeout(closeSuggestions, 150)}
        className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm
          placeholder-gray-400 shadow-sm transition-colors resize-y
          focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
      />
      <p className="mt-1 text-xs text-gray-400">
        Tip: Use @username to mention other users
      </p>

      {/* Suggestion dropdown */}
      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute z-30 left-0 right-0 mt-1 bg-white rounded-lg shadow-lg border border-gray-200 max-h-48 overflow-y-auto">
          {suggestions.map((user) => (
            <button
              key={user.id}
              type="button"
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => handleSelect(user.username)}
              className="flex items-center gap-2 w-full px-3 py-2 text-sm text-left hover:bg-indigo-50 transition-colors"
            >
              <Avatar
                name={user.full_name}
                avatarUrl={user.avatar_url}
                size="sm"
              />
              <div>
                <p className="font-medium text-gray-900">{user.full_name}</p>
                <p className="text-xs text-gray-500">@{user.username}</p>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

MentionInput.propTypes = {
  id: PropTypes.string,
  label: PropTypes.string,
  value: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  placeholder: PropTypes.string,
  rows: PropTypes.number,
};
