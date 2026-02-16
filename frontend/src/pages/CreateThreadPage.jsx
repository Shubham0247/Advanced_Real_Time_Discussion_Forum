import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { useThreadMutations } from "../hooks/useThreads";
import { uploadThreadImage } from "../api/threadApi";
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
        onSubmit={async (data) => {
          try {
            let image_url;
            if (data.imageFile) {
              const uploaded = await uploadThreadImage(data.imageFile);
              image_url = uploaded.image_url;
            }
            createMutation.mutate({
              title: data.title,
              description: data.description,
              image_url,
            });
          } catch (err) {
            toast.error(err.response?.data?.detail || "Failed to upload image");
          }
        }}
        loading={createMutation.isPending}
        onCancel={() => navigate("/")}
        submitLabel="Create Thread"
      />
    </PageWrapper>
  );
}
