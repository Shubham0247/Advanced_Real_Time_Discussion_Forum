import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import PropTypes from "prop-types";
import { resolveMentions } from "../../api/authApi";

const MENTION_TOKEN_RE = /(@[A-Za-z0-9_]{1,50})/g;
const USERNAME_ONLY_RE = /^@([A-Za-z0-9_]{1,50})$/;

export default function MentionText({ text, className = "" }) {
  const usernames = useMemo(() => {
    if (!text) return [];
    const matches = text.match(MENTION_TOKEN_RE) || [];
    return Array.from(
      new Set(matches.map((m) => m.slice(1).toLowerCase()).filter(Boolean))
    );
  }, [text]);

  const { data } = useQuery({
    queryKey: ["mention-resolve", usernames],
    queryFn: () => resolveMentions(usernames),
    enabled: usernames.length > 0,
    staleTime: 5 * 60 * 1000,
  });

  const existing = useMemo(() => {
    const list = data?.existing_usernames || [];
    return new Set(list.map((u) => u.toLowerCase()));
  }, [data]);

  const segments = useMemo(() => {
    if (!text) return [""];
    return text.split(MENTION_TOKEN_RE);
  }, [text]);

  return (
    <span className={className}>
      {segments.map((segment, index) => {
        const match = segment.match(USERNAME_ONLY_RE);
        if (!match) return <span key={index}>{segment}</span>;

        const username = match[1].toLowerCase();
        const isExisting = existing.has(username);
        if (!isExisting) return <span key={index}>{segment}</span>;

        return (
          <span key={index} className="font-semibold text-gray-900">
            {segment}
          </span>
        );
      })}
    </span>
  );
}

MentionText.propTypes = {
  text: PropTypes.string,
  className: PropTypes.string,
};
