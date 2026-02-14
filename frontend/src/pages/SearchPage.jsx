import { useState } from "react";
import { SearchX } from "lucide-react";
import { Link } from "react-router-dom";
import { useThreadSearch } from "../hooks/useThreads";
import { useCommentSearch } from "../hooks/useComments";
import PageWrapper from "../components/layout/PageWrapper";
import SearchBar from "../components/common/SearchBar";
import Spinner from "../components/common/Spinner";
import Pagination from "../components/common/Pagination";
import EmptyState from "../components/common/EmptyState";
import ThreadCard from "../components/thread/ThreadCard";
import { formatDate } from "../utils/formatDate";

const TABS = [
  { key: "threads", label: "Threads" },
  { key: "comments", label: "Comments" },
];

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [tab, setTab] = useState("threads");
  const [page, setPage] = useState(1);
  const size = 10;

  const threadQuery = useThreadSearch(tab === "threads" ? query : "", page, size);
  const commentQuery = useCommentSearch(tab === "comments" ? query : "", page, size);

  const handleSearch = (q) => {
    setQuery(q);
    setPage(1);
  };

  const activeQuery = tab === "threads" ? threadQuery : commentQuery;
  const items = activeQuery.data?.items || [];
  const total = activeQuery.data?.total || 0;
  const totalPages = Math.ceil(total / size);

  return (
    <PageWrapper>
      <h1 className="text-2xl font-bold text-gray-900 mb-4">Search</h1>

      <SearchBar
        placeholder="Search threads and comments..."
        onSearch={handleSearch}
        className="mb-4"
      />

      {/* Tabs */}
      <div className="flex gap-1 mb-6 border-b border-gray-200">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => {
              setTab(t.key);
              setPage(1);
            }}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors -mb-px
              ${
                tab === t.key
                  ? "border-indigo-600 text-indigo-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Results */}
      {!query ? (
        <EmptyState
          icon={SearchX}
          title="Start searching"
          description="Type a keyword and press Enter to search"
        />
      ) : activeQuery.isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner size={28} />
        </div>
      ) : items.length === 0 ? (
        <EmptyState
          icon={SearchX}
          title="No results found"
          description={`No ${tab} match "${query}"`}
        />
      ) : (
        <>
          <p className="text-sm text-gray-500 mb-4">
            {total} result{total !== 1 ? "s" : ""} for &ldquo;{query}&rdquo;
          </p>

          {tab === "threads" ? (
            <div className="space-y-3">
              {items.map((thread) => (
                <ThreadCard key={thread.id} thread={thread} />
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              {items.map((comment) => (
                <Link
                  key={comment.id}
                  to={`/threads/${comment.thread_id}`}
                  className="block bg-white rounded-xl border border-gray-100 p-4 hover:border-indigo-200 transition-all"
                >
                  <p className="text-sm text-gray-700 line-clamp-3">
                    {comment.content}
                  </p>
                  <p className="text-xs text-gray-400 mt-2">
                    {comment.author_username || "User"} &middot;{" "}
                    {formatDate(comment.created_at)}
                  </p>
                </Link>
              ))}
            </div>
          )}

          <Pagination
            page={page}
            totalPages={totalPages}
            onPageChange={setPage}
          />
        </>
      )}
    </PageWrapper>
  );
}
