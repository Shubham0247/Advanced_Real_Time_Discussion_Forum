import { useState } from "react";
import { Link } from "react-router-dom";
import { MessageSquareText } from "lucide-react";
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
    <PageWrapper className="max-w-6xl">
      {/* Header */}
      <div className="mx-auto mb-7 w-full max-w-4xl">
        <h1 className="text-3xl font-semibold tracking-tight text-gray-900">Discussions</h1>
        <p className="mt-2 text-sm text-gray-600">
          Browse and join the conversation in real-time.
        </p>
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
          <div className="mx-auto w-full max-w-3xl space-y-3">
            {threads.map((thread) => (
              <ThreadCard key={thread.id} thread={thread} />
            ))}
          </div>
          <div className="mx-auto w-full max-w-3xl">
            <Pagination
              page={page}
              totalPages={totalPages}
              onPageChange={setPage}
            />
          </div>
        </>
      )}
    </PageWrapper>
  );
}
