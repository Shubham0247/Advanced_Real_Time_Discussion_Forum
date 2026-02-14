import { Navigate, Outlet } from "react-router-dom";
import useAuthStore from "../stores/authStore";
import Spinner from "../components/common/Spinner";

/**
 * Wraps routes that require authentication.
 * Redirects to /login if not authenticated.
 */
export default function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuthStore();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Spinner size={32} />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
