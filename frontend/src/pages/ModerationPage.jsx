import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ShieldCheck } from "lucide-react";
import toast from "react-hot-toast";
import { moderationThreads, moderationComments } from "../api/moderationApi";
import { deleteThread } from "../api/threadApi";
import { deleteComment } from "../api/commentApi";
import PageWrapper from "../components/layout/PageWrapper";
import SearchBar from "../components/common/SearchBar";
import Spinner from "../components/common/Spinner";
import ModerationTable from "../components/moderation/ModerationTable";

const TABS = [
  { key: "threads", label: "Threads" },
  { key: "comments", label: "Comments" },
];

export default function ModerationPage() {
  const [tab, setTab] = useState("threads");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const size = 20;
  const queryClient = useQueryClient();

  const threadQuery = useQuery({
    queryKey: ["mod-threads", search, page],
    queryFn: () => moderationThreads({ q: search || undefined, page, size }),
    enabled: tab === "threads",
  });

  const commentQuery = useQuery({
    queryKey: ["mod-comments", search, page],
    queryFn: () => moderationComments({ q: search || undefined, page, size }),
    enabled: tab === "comments",
  });

  const deleteThreadMutation = useMutation({
    mutationFn: deleteThread,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["mod-threads"] });
      toast.success("Thread deleted");
    },
  });

  const deleteCommentMutation = useMutation({
    mutationFn: deleteComment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["mod-comments"] });
      toast.success("Comment deleted");
    },
  });

  const activeQuery = tab === "threads" ? threadQuery : commentQuery;
  const items = activeQuery.data?.items || [];
  const total = activeQuery.data?.total || 0;
  const totalPages = Math.ceil(total / size);

  const handleSearch = (q) => {
    setSearch(q);
    setPage(1);
  };

  const handleDelete = (id) => {
    if (tab === "threads") {
      deleteThreadMutation.mutate(id);
    } else {
      deleteCommentMutation.mutate(id);
    }
  };

  return (
    <PageWrapper className="max-w-5xl">
      <div className="flex items-center gap-3 mb-6">
        <ShieldCheck size={28} className="text-indigo-600" />
        <h1 className="text-2xl font-bold text-gray-900">Moderation</h1>
      </div>

      <SearchBar
        placeholder={`Search ${tab}...`}
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
              setSearch("");
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

      {activeQuery.isLoading ? (
        <div className="flex justify-center py-16">
          <Spinner size={28} />
        </div>
      ) : (
        <ModerationTable
          items={items}
          type={tab}
          total={total}
          page={page}
          totalPages={totalPages}
          onPageChange={setPage}
          onDelete={handleDelete}
        />
      )}
    </PageWrapper>
  );
}
