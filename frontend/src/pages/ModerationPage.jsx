import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { ShieldCheck } from "lucide-react";
import toast from "react-hot-toast";
import {
  moderationReports,
  moderationThreads,
  updateReportStatus,
  updateThreadModerationStatus,
} from "../api/moderationApi";
import { deleteThread } from "../api/threadApi";
import PageWrapper from "../components/layout/PageWrapper";
import SearchBar from "../components/common/SearchBar";
import Spinner from "../components/common/Spinner";
import Button from "../components/common/Button";
import Pagination from "../components/common/Pagination";
import { formatDate } from "../utils/formatDate";

const TABS = [
  { key: "reported", label: "Reported" },
  { key: "pending", label: "Pending" },
  { key: "approved", label: "Approved" },
];

export default function ModerationPage() {
  const [tab, setTab] = useState("reported");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const size = 20;
  const queryClient = useQueryClient();

  const reportsQuery = useQuery({
    queryKey: ["mod-reports", tab, search, page],
    queryFn: () =>
      moderationReports({ status: tab, q: search || undefined, page, size }),
    enabled: tab === "reported",
  });

  const threadsQuery = useQuery({
    queryKey: ["mod-threads", tab, search, page],
    queryFn: () =>
      moderationThreads({
        status: tab,
        q: search || undefined,
        page,
        size,
      }),
    enabled: tab === "pending" || tab === "approved",
  });

  const statusMutation = useMutation({
    mutationFn: ({ reportId, status }) => updateReportStatus(reportId, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["mod-reports"] });
      queryClient.invalidateQueries({ queryKey: ["mod-threads"] });
      toast.success("Report status updated");
    },
  });

  const threadStatusMutation = useMutation({
    mutationFn: ({ threadId, status }) =>
      updateThreadModerationStatus(threadId, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["mod-reports"] });
      queryClient.invalidateQueries({ queryKey: ["mod-threads"] });
      toast.success("Thread moderation status updated");
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Could not update thread status");
    },
  });

  const deleteThreadMutation = useMutation({
    mutationFn: deleteThread,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["mod-reports"] });
      queryClient.invalidateQueries({ queryKey: ["mod-threads"] });
      queryClient.invalidateQueries({ queryKey: ["threads"] });
      toast.success("Thread deleted");
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || "Could not delete thread");
    },
  });

  const activeQuery = tab === "reported" ? reportsQuery : threadsQuery;
  const items = activeQuery.data?.items || [];
  const total = activeQuery.data?.total || 0;
  const totalPages = Math.ceil(total / size);

  const handleSearch = (q) => {
    setSearch(q);
    setPage(1);
  };

  return (
    <PageWrapper className="max-w-5xl">
      <div className="flex items-center gap-3 mb-6">
        <ShieldCheck size={28} className="text-indigo-600" />
        <h1 className="text-2xl font-bold text-gray-900">Moderation</h1>
      </div>

      <SearchBar
        placeholder={
          tab === "reported"
            ? "Search reported threads..."
            : tab === "pending"
              ? "Search pending threads..."
              : "Search approved threads..."
        }
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
        <>
          <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <th className="px-4 py-3">Thread</th>
                    <th className="px-4 py-3">
                      {tab === "reported" ? "Reported By" : "Author"}
                    </th>
                    <th className="px-4 py-3">
                      {tab === "reported" ? "Reason" : "Status"}
                    </th>
                    <th className="px-4 py-3">Date</th>
                    {tab !== "approved" && (
                      <th className="px-4 py-3 text-right">Actions</th>
                    )}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {items.map((item) => (
                    <tr key={`${tab}-${item.id}`} className="hover:bg-gray-50/50">
                      <td className="px-4 py-3 max-w-xs">
                        <Link
                          to={`/threads/${tab === "reported" ? item.thread_id : item.id}`}
                          className="font-medium text-gray-900 hover:text-indigo-600 truncate block"
                        >
                          {tab === "reported" ? item.thread_title : item.title}
                        </Link>
                      </td>
                      <td className="px-4 py-3 text-gray-500">
                        {tab === "reported"
                          ? `@${item.reporter_username}`
                          : `@${item.author_username || "user"}`}
                      </td>
                      <td className="px-4 py-3 text-gray-600 max-w-sm truncate">
                        {tab === "reported"
                          ? item.reason || "No reason provided"
                          : (item.moderation_status || "pending")}
                      </td>
                      <td className="px-4 py-3 text-gray-400 text-xs">
                        {formatDate(item.created_at)}
                      </td>
                      {tab !== "approved" && (
                        <td className="px-4 py-3">
                          <div className="flex justify-end gap-2">
                            <Button
                              size="sm"
                              variant="danger"
                              onClick={() => {
                                if (!confirm("Delete this thread?")) return;
                                deleteThreadMutation.mutate(
                                  tab === "reported" ? item.thread_id : item.id
                                );
                              }}
                              disabled={deleteThreadMutation.isPending}
                            >
                              Delete
                            </Button>
                            <Button
                              size="sm"
                              variant="primary"
                              onClick={async () => {
                                try {
                                  if (tab === "reported") {
                                    await statusMutation.mutateAsync({
                                      reportId: item.id,
                                      status: "approved",
                                    });
                                    await threadStatusMutation.mutateAsync({
                                      threadId: item.thread_id,
                                      status: "approved",
                                    });
                                  } else {
                                    await threadStatusMutation.mutateAsync({
                                      threadId: item.id,
                                      status: "approved",
                                    });
                                  }
                                } catch {
                                  // Error toasts are handled in mutation callbacks.
                                }
                              }}
                              disabled={statusMutation.isPending || threadStatusMutation.isPending}
                            >
                              Approve
                            </Button>
                          </div>
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />

          <p className="text-xs text-gray-400 text-center mt-2">
            {total} {tab === "reported" ? "reports" : "threads"} in {tab}
          </p>
        </>
      )}
    </PageWrapper>
  );
}
