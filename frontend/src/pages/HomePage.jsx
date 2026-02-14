import { useState } from "react";
import { Link } from "react-router-dom";
import { Plus, MessageSquareText } from "lucide-react";
import { useThreadList } from "../hooks/useThreads";
import { PAGE_SIZES } from "../utils/constants";
import PageWrapper from "../components/layout/PageWrapper";
import Spinner from "../components/common/Spinner";
import Pagination from "../components/common/Pagination";
import EmptyState from "../components/common/EmptyState";
import Button from "../components/common/Button";
import ThreadCard from "../components/thread/ThreadCard";

export default function HomePage() {
  const [page, setPage] = useState(1);
  const { data, isLoading, isError } = useThreadList(page);

  const threads = data?.items || [];
  const totalPages = data ? Math.ceil(data.total / PAGE_SIZES.THREADS) : 0;

  return (
    <PageWrapper>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Discussions</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Browse and join the conversation
          </p>
        </div>
        <Link to="/threads/new">
          <Button size="md">
            <Plus size={16} />
            New Thread
          </Button>
        </Link>
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="flex justify-center py-16">
          <Spinner size={32} />
        </div>
      ) : isError ? (
        <div className="text-center py-16 text-red-500">
          Failed to load threads. Please try again.
        </div>
      ) : threads.length === 0 ? (
        <EmptyState
          icon={MessageSquareText}
          title="No discussions yet"
          description="Be the first to start a conversation!"
          action={
            <Link to="/threads/new">
              <Button>Create Thread</Button>
            </Link>
          }
        />
      ) : (
        <>
          <div className="space-y-3">
            {threads.map((thread) => (
              <ThreadCard key={thread.id} thread={thread} />
            ))}
          </div>
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
