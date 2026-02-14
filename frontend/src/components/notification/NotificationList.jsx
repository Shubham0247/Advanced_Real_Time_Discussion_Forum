import PropTypes from "prop-types";
import { BellOff } from "lucide-react";
import NotificationItem from "./NotificationItem";
import EmptyState from "../common/EmptyState";
import Pagination from "../common/Pagination";

/**
 * Renders a paginated list of NotificationItems.
 */
export default function NotificationList({
  items,
  page,
  totalPages,
  onPageChange,
  onMarkRead,
  onOpen,
}) {
  if (items.length === 0) {
    return (
      <EmptyState
        icon={BellOff}
        title="No notifications"
        description="You're all caught up!"
      />
    );
  }

  return (
    <>
      <div className="space-y-2">
        {items.map((n) => (
          <NotificationItem
            key={n.id}
            notification={n}
            onMarkRead={onMarkRead}
            onOpen={onOpen}
          />
        ))}
      </div>
      <Pagination page={page} totalPages={totalPages} onPageChange={onPageChange} />
    </>
  );
}

NotificationList.propTypes = {
  items: PropTypes.array.isRequired,
  page: PropTypes.number.isRequired,
  totalPages: PropTypes.number.isRequired,
  onPageChange: PropTypes.func.isRequired,
  onMarkRead: PropTypes.func.isRequired,
  onOpen: PropTypes.func.isRequired,
};
