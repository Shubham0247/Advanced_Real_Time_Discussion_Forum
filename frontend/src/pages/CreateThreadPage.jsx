import { useNavigate } from "react-router-dom";
import { useThreadMutations } from "../hooks/useThreads";
import PageWrapper from "../components/layout/PageWrapper";
import ThreadForm from "../components/thread/ThreadForm";

export default function CreateThreadPage() {
  const navigate = useNavigate();
  const { createMutation } = useThreadMutations();

  return (
    <PageWrapper className="max-w-2xl">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">
        Start a New Discussion
      </h1>

      <ThreadForm
        onSubmit={(data) => createMutation.mutate(data)}
        loading={createMutation.isPending}
        onCancel={() => navigate("/")}
        submitLabel="Create Thread"
      />
    </PageWrapper>
  );
}
