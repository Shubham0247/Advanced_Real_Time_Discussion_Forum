import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { CheckCheck } from "lucide-react";
import { useNotificationList, useNotificationMutations } from "../hooks/useNotifications";
import PageWrapper from "../components/layout/PageWrapper";
import Spinner from "../components/common/Spinner";
import Button from "../components/common/Button";
import NotificationList from "../components/notification/NotificationList";

export default function NotificationsPage() {
  const [page, setPage] = useState(1);
  const size = 15;
  const navigate = useNavigate();

  const { data, isLoading } = useNotificationList(page, size);
  const { markOneMutation, markAllMutation } = useNotificationMutations();

  const items = data?.items || [];
  const total = data?.total || 0;
  const totalPages = Math.ceil(total / size);

  const getNotificationRoute = (notification) => {
    const ref = notification.reference_id;
    if (!ref) return null;

    switch (notification.type) {
      case "thread.liked":
      case "mention.thread":
        return `/threads/${ref}`;
      case "comment.replied":
      case "comment.liked":
      case "thread.commented":
      case "mention.comment":
        return `/threads/${ref}#comments`;
      default:
        return null;
    }
  };

  const handleOpenNotification = async (notification) => {
    if (!notification.is_read) {
      try {
        await markOneMutation.mutateAsync(notification.id);
      } catch {
        // If mark-read fails, still allow opening the notification target.
      }
    }
    const route = getNotificationRoute(notification);
    if (route) {
      navigate(route);
    }
  };

  return (
    <PageWrapper>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Notifications</h1>
        {items.length > 0 && (
          <Button
            variant="secondary"
            size="sm"
            onClick={() => markAllMutation.mutate()}
            loading={markAllMutation.isPending}
          >
            <CheckCheck size={16} />
            Mark all read
          </Button>
        )}
      </div>

      {isLoading ? (
        <div className="flex justify-center py-16">
          <Spinner size={28} />
        </div>
      ) : (
        <NotificationList
          items={items}
          page={page}
          totalPages={totalPages}
          onPageChange={setPage}
          onMarkRead={(id) => markOneMutation.mutate(id)}
          onOpen={handleOpenNotification}
        />
      )}
    </PageWrapper>
  );
}
