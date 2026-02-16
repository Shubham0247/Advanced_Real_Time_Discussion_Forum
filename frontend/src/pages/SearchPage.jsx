import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { SearchX } from "lucide-react";
import { useThreadSearch } from "../hooks/useThreads";
import { searchUsers } from "../api/authApi";
import PageWrapper from "../components/layout/PageWrapper";
import SearchBar from "../components/common/SearchBar";
import Spinner from "../components/common/Spinner";
import Pagination from "../components/common/Pagination";
import EmptyState from "../components/common/EmptyState";
import ThreadCard from "../components/thread/ThreadCard";
import Avatar from "../components/common/Avatar";

const TABS = [
  { key: "threads", label: "Threads" },
  { key: "users", label: "Users" },
];

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [tab, setTab] = useState("threads");
  const [page, setPage] = useState(1);
  const size = 10;

  const threadQuery = useThreadSearch(tab === "threads" ? query : "", page, size);
  const userQuery = useQuery({
    queryKey: ["search-users", query, page],
    queryFn: () => searchUsers({ q: query, page, size }),
    enabled: tab === "users" && query.length > 0,
  });

  const handleSearch = (q) => {
    setQuery(q);
    setPage(1);
  };

  const activeQuery = tab === "threads" ? threadQuery : userQuery;
  const items = activeQuery.data?.items || [];
  const total = activeQuery.data?.total || 0;
  const totalPages = Math.ceil(total / size);

  return (
    <PageWrapper>
      <h1 className="text-2xl font-bold text-gray-900 mb-4">Search</h1>

      <SearchBar
        placeholder="Search threads and users..."
        onSearch={handleSearch}
        onChangeSearch={handleSearch}
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
          description="Type a keyword to see live suggestions"
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
              {items.map((u) => (
                <div
                  key={u.id}
                  className="flex items-center gap-3 bg-white rounded-xl border border-gray-100 p-4"
                >
                  <Avatar
                    name={u.full_name || u.username}
                    avatarUrl={u.avatar_url}
                    size="md"
                  />
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {u.full_name || u.username}
                    </p>
                    <p className="text-xs text-gray-500 truncate">@{u.username}</p>
                    {u.bio && (
                      <p className="text-xs text-gray-400 mt-1 line-clamp-2">{u.bio}</p>
                    )}
                  </div>
                </div>
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
