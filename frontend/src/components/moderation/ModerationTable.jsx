import PropTypes from "prop-types";
import { Link } from "react-router-dom";
import { Trash2 } from "lucide-react";
import Button from "../common/Button";
import Pagination from "../common/Pagination";
import { formatDate } from "../../utils/formatDate";

/**
 * Shared table for moderation thread/comment lists.
 */
export default function ModerationTable({
  items,
  type,
  total,
  page,
  totalPages,
  onPageChange,
  onDelete,
}) {
  return (
    <>
      <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <th className="px-4 py-3">Content</th>
                <th className="px-4 py-3">Author</th>
                <th className="px-4 py-3">Date</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {items.map((item) => (
                <tr key={item.id} className="hover:bg-gray-50/50">
                  <td className="px-4 py-3 max-w-xs">
                    {type === "threads" ? (
                      <Link
                        to={`/threads/${item.id}`}
                        className="font-medium text-gray-900 hover:text-indigo-600 truncate block"
                      >
                        {item.title}
                      </Link>
                    ) : (
                      <Link
                        to={`/threads/${item.thread_id}`}
                        className="text-gray-700 hover:text-indigo-600 line-clamp-2 block"
                      >
                        {item.content}
                      </Link>
                    )}
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {item.author_username || "—"}
                  </td>
                  <td className="px-4 py-3 text-gray-400 text-xs">
                    {formatDate(item.created_at)}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Button
                      size="sm"
                      variant="danger"
                      onClick={() => {
                        if (!confirm("Delete this item?")) return;
                        onDelete(item.id);
                      }}
                    >
                      <Trash2 size={14} />
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <Pagination page={page} totalPages={totalPages} onPageChange={onPageChange} />

      <p className="text-xs text-gray-400 text-center mt-2">
        {total} {type} total
      </p>
    </>
  );
}

ModerationTable.propTypes = {
  items: PropTypes.array.isRequired,
  type: PropTypes.oneOf(["threads", "comments"]).isRequired,
  total: PropTypes.number.isRequired,
  page: PropTypes.number.isRequired,
  totalPages: PropTypes.number.isRequired,
  onPageChange: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
};
