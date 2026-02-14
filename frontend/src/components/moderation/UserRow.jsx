import PropTypes from "prop-types";
import { UserCheck, UserX, ChevronUp, ChevronDown } from "lucide-react";
import Avatar from "../common/Avatar";
import Button from "../common/Button";

const ROLES_AVAILABLE = ["moderator", "admin"];

/**
 * A single user row inside the admin user table.
 */
export default function UserRow({
  user,
  onToggleStatus,
  onPromote,
  onDemote,
}) {
  const userRoles = user.roles?.map((r) => r.name) || [];

  return (
    <tr className="hover:bg-gray-50/50">
      <td className="px-4 py-3">
        <div className="flex items-center gap-3">
          <Avatar name={user.full_name} avatarUrl={user.avatar_url} size="sm" />
          <div>
            <p className="font-medium text-gray-900">{user.full_name}</p>
            <p className="text-xs text-gray-500">
              @{user.username} &middot; {user.email}
            </p>
          </div>
        </div>
      </td>
      <td className="px-4 py-3">
        <div className="flex gap-1 flex-wrap">
          {userRoles.map((role) => (
            <span
              key={role}
              className={`px-2 py-0.5 rounded-full text-[10px] font-medium
                ${
                  role === "admin"
                    ? "bg-red-50 text-red-600"
                    : role === "moderator"
                    ? "bg-amber-50 text-amber-700"
                    : "bg-gray-100 text-gray-600"
                }`}
            >
              {role}
            </span>
          ))}
        </div>
      </td>
      <td className="px-4 py-3">
        <span
          className={`inline-flex items-center gap-1 text-xs font-medium
            ${user.is_active ? "text-green-600" : "text-gray-400"}`}
        >
          {user.is_active ? (
            <>
              <UserCheck size={14} /> Active
            </>
          ) : (
            <>
              <UserX size={14} /> Inactive
            </>
          )}
        </span>
      </td>
      <td className="px-4 py-3">
        <div className="flex items-center justify-end gap-1.5">
          <Button
            size="sm"
            variant={user.is_active ? "danger" : "primary"}
            onClick={() => onToggleStatus(user.id, !user.is_active)}
          >
            {user.is_active ? "Deactivate" : "Activate"}
          </Button>

          {ROLES_AVAILABLE.map((role) =>
            userRoles.includes(role) ? (
              <Button
                key={role}
                size="sm"
                variant="secondary"
                onClick={() => onDemote(user.id, role)}
                title={`Remove ${role}`}
              >
                <ChevronDown size={14} />
                {role}
              </Button>
            ) : (
              <Button
                key={role}
                size="sm"
                variant="ghost"
                onClick={() => onPromote(user.id, role)}
                title={`Promote to ${role}`}
              >
                <ChevronUp size={14} />
                {role}
              </Button>
            )
          )}
        </div>
      </td>
    </tr>
  );
}

UserRow.propTypes = {
  user: PropTypes.object.isRequired,
  onToggleStatus: PropTypes.func.isRequired,
  onPromote: PropTypes.func.isRequired,
  onDemote: PropTypes.func.isRequired,
};
