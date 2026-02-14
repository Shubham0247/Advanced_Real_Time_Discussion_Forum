import { Navigate, Outlet } from "react-router-dom";
import useAuthStore from "../stores/authStore";

/**
 * Wraps routes that require a specific role.
 * Falls through to ProtectedRoute for auth check first.
 */
export default function AdminRoute({ roles = ["admin"] }) {
  const { user } = useAuthStore();

  const hasAccess = user?.roles?.some((r) => roles.includes(r.name));

  if (!hasAccess) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}
