import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Activity, MessageCircle, Heart, FileText } from "lucide-react";
import { useMyActivityList } from "../hooks/useActivity";
import { PAGE_SIZES } from "../utils/constants";
import { formatDate } from "../utils/formatDate";
import PageWrapper from "../components/layout/PageWrapper";
import Spinner from "../components/common/Spinner";
import EmptyState from "../components/common/EmptyState";
import Pagination from "../components/common/Pagination";

const RANGE_OPTIONS = [
  { key: "24h", label: "Recent 24 hours" },
  { key: "7d", label: "Last 7 days" },
  { key: "1m", label: "Last 1 month" },
  { key: "all", label: "All time" },
];

const TYPE_OPTIONS = [
  { key: "all", label: "All activity" },
  { key: "like", label: "Likes" },
  { key: "comment", label: "Comments" },
];

function getActivityLabel(type) {
  switch (type) {
    case "thread.created":
      return "Created a thread";
    case "comment.created":
      return "Posted a comment";
    case "reply.created":
      return "Posted a reply";
    case "thread.liked":
      return "Liked a thread";
    case "comment.liked":
      return "Liked a comment";
    default:
      return "Activity";
  }
}

function getActivityIcon(type) {
  if (type.includes("liked")) return Heart;
  if (type.includes("comment") || type.includes("reply")) return MessageCircle;
  return FileText;
}

function getActivityRoute(item) {
  if (!item.thread_id) return null;
  if (item.comment_id) return `/threads/${item.thread_id}#comments`;
  return `/threads/${item.thread_id}`;
}

export default function MyActivityPage() {
  const [range, setRange] = useState("all");
  const [type, setType] = useState("all");
  const [page, setPage] = useState(1);

  const { data, isLoading, isError } = useMyActivityList(range, type, page);
  const items = data?.items || [];
  const total = data?.total || 0;
  const totalPages = useMemo(
    () => Math.ceil(total / PAGE_SIZES.ACTIVITY),
    [total]
  );

  return (
    <PageWrapper>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">My Activity</h1>
        <p className="text-sm text-gray-500 mt-0.5">
          Your comments, replies, likes, and threads
        </p>
      </div>

      <div className="mb-5 flex flex-col sm:flex-row sm:items-end gap-3 sm:gap-4">
        <div className="sm:w-64">
          <label
            htmlFor="activity-time-range"
            className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2"
          >
            Time Range
          </label>
          <select
            id="activity-time-range"
            value={range}
            onChange={(e) => {
              setRange(e.target.value);
              setPage(1);
            }}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-700 bg-white focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            {RANGE_OPTIONS.map((option) => (
              <option key={option.key} value={option.key}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <div className="sm:w-64">
          <label
            htmlFor="activity-type-filter"
            className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2"
          >
            Activity Type
          </label>
          <select
            id="activity-type-filter"
            value={type}
            onChange={(e) => {
              setType(e.target.value);
              setPage(1);
            }}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-700 bg-white focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            {TYPE_OPTIONS.map((option) => (
              <option key={option.key} value={option.key}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-16">
          <Spinner size={30} />
        </div>
      ) : isError ? (
        <div className="text-center py-16 text-red-500">
          Failed to load your activity. Please try again.
        </div>
      ) : items.length === 0 ? (
        <EmptyState
          icon={Activity}
          title="No activity found"
          description="Try changing the filter or start interacting with threads."
        />
      ) : (
        <>
          <div className="space-y-3">
            {items.map((item, idx) => {
              const Icon = getActivityIcon(item.activity_type);
              const route = getActivityRoute(item);
              const Wrapper = route ? Link : "div";
              const wrapperProps = route ? { to: route } : {};
              return (
                <Wrapper
                  key={`${item.activity_type}-${item.created_at}-${idx}`}
                  {...wrapperProps}
                  className="block bg-white rounded-xl border border-gray-100 p-4 hover:border-indigo-200 hover:shadow-sm transition-all"
                >
                  <div className="flex items-start gap-3">
                    <div className="p-2 rounded-lg bg-indigo-50 text-indigo-600">
                      <Icon size={16} />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-gray-800">
                        {getActivityLabel(item.activity_type)}
                      </p>
                      {item.title && (
                        <p className="text-sm text-gray-600 mt-0.5 truncate">
                          Thread: {item.title}
                        </p>
                      )}
                      {item.preview && (
                        <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">
                          {item.preview}
                        </p>
                      )}
                      <p className="text-xs text-gray-400 mt-1">
                        {formatDate(item.created_at)}
                      </p>
                    </div>
                  </div>
                </Wrapper>
              );
            })}
          </div>

          <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
        </>
      )}
    </PageWrapper>
  );
}
