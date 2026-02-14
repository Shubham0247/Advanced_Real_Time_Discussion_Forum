import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { Shield } from "lucide-react";
import {
  adminListUsers,
  adminUpdateUserStatus,
  adminPromoteUser,
  adminDemoteUser,
} from "../api/authApi";
import PageWrapper from "../components/layout/PageWrapper";
import SearchBar from "../components/common/SearchBar";
import Spinner from "../components/common/Spinner";
import Pagination from "../components/common/Pagination";
import UserRow from "../components/moderation/UserRow";

export default function AdminDashboard() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const size = 20;
  const queryClient = useQueryClient();

  const invalidateUsers = () =>
    queryClient.invalidateQueries({ queryKey: ["admin-users"] });

  const { data, isLoading } = useQuery({
    queryKey: ["admin-users", page, search, roleFilter],
    queryFn: () =>
      adminListUsers({
        page,
        size,
        q: search || undefined,
        role: roleFilter || undefined,
      }),
  });

  const statusMutation = useMutation({
    mutationFn: ({ userId, isActive }) =>
      adminUpdateUserStatus(userId, isActive),
    onSuccess: () => { invalidateUsers(); toast.success("User status updated"); },
    onError: (err) => toast.error(err.response?.data?.detail || "Failed"),
  });

  const promoteMutation = useMutation({
    mutationFn: ({ userId, roleName }) => adminPromoteUser(userId, roleName),
    onSuccess: () => { invalidateUsers(); toast.success("User promoted"); },
    onError: (err) => toast.error(err.response?.data?.detail || "Failed"),
  });

  const demoteMutation = useMutation({
    mutationFn: ({ userId, roleName }) => adminDemoteUser(userId, roleName),
    onSuccess: () => { invalidateUsers(); toast.success("Role removed"); },
    onError: (err) => toast.error(err.response?.data?.detail || "Failed"),
  });

  const users = data?.items || [];
  const total = data?.total || 0;
  const totalPages = Math.ceil(total / size);

  const handleSearch = (q) => {
    setSearch(q);
    setPage(1);
  };

  return (
    <PageWrapper className="max-w-5xl">
      <div className="flex items-center gap-3 mb-6">
        <Shield size={28} className="text-indigo-600" />
        <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <SearchBar
          placeholder="Search users..."
          onSearch={handleSearch}
          className="flex-1"
        />
        <select
          value={roleFilter}
          onChange={(e) => {
            setRoleFilter(e.target.value);
            setPage(1);
          }}
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm bg-white
            focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        >
          <option value="">All roles</option>
          <option value="admin">Admin</option>
          <option value="moderator">Moderator</option>
          <option value="member">Member</option>
        </select>
      </div>

      {/* Table */}
      {isLoading ? (
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
                    <th className="px-4 py-3">User</th>
                    <th className="px-4 py-3">Roles</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {users.map((u) => (
                    <UserRow
                      key={u.id}
                      user={u}
                      onToggleStatus={(userId, isActive) =>
                        statusMutation.mutate({ userId, isActive })
                      }
                      onPromote={(userId, roleName) =>
                        promoteMutation.mutate({ userId, roleName })
                      }
                      onDemote={(userId, roleName) =>
                        demoteMutation.mutate({ userId, roleName })
                      }
                    />
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <Pagination
            page={page}
            totalPages={totalPages}
            onPageChange={setPage}
          />

          <p className="text-xs text-gray-400 text-center mt-2">
            {total} user{total !== 1 ? "s" : ""} total
          </p>
        </>
      )}
    </PageWrapper>
  );
}
