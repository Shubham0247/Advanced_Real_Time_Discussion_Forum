import { useState, useCallback, useRef } from "react";
import { suggestMentionUsers } from "../api/authApi";

/**
 * Hook powering the @mention autocomplete.
 *
 * Tracks the textarea value, detects when the user types @,
 * fetches matching usernames, and exposes helpers to insert a mention.
 */
export default function useMentions() {
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [mentionQuery, setMentionQuery] = useState("");
  const debounceRef = useRef(null);

  /**
   * Call this from the textarea's onChange.
   * It detects the current @word and fetches matching users.
   */
  const handleInputChange = useCallback((text, cursorPos) => {
    // Find the @word at the cursor position
    const before = text.slice(0, cursorPos);
    const match = before.match(/@([A-Za-z0-9_]{1,50})$/);

    if (match) {
      const query = match[1];
      setMentionQuery(query);
      setShowSuggestions(true);

      // Debounce API call
      if (debounceRef.current) clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(async () => {
        try {
          const data = await suggestMentionUsers(query, 8);
          setSuggestions(
            (data.items || []).map((u) => ({
              id: u.id,
              username: u.username,
              full_name: u.full_name,
              avatar_url: u.avatar_url,
            }))
          );
        } catch {
          setSuggestions([]);
        }
      }, 250);
    } else {
      setShowSuggestions(false);
      setSuggestions([]);
    }
  }, []);

  /**
   * Insert a @username at the current cursor position.
   * Returns the new text with the mention inserted.
   */
  const insertMention = useCallback(
    (text, cursorPos, username) => {
      const before = text.slice(0, cursorPos);
      const after = text.slice(cursorPos);
      const replaced = before.replace(/@[A-Za-z0-9_]*$/, `@${username} `);
      setShowSuggestions(false);
      setSuggestions([]);
      return replaced + after;
    },
    []
  );

  const closeSuggestions = useCallback(() => {
    setShowSuggestions(false);
    setSuggestions([]);
  }, []);

  return {
    suggestions,
    showSuggestions,
    mentionQuery,
    handleInputChange,
    insertMention,
    closeSuggestions,
  };
}
