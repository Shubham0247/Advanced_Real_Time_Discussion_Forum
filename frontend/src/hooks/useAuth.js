import { useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { login as loginApi, register as registerApi } from "../api/authApi";
import useAuthStore from "../stores/authStore";
import { getApiErrorMessage } from "../utils/getApiErrorMessage";

/**
 * Hook that wraps authentication actions with loading/error state.
 */
export default function useAuth() {
  const navigate = useNavigate();
  const authLogin = useAuthStore((s) => s.login);
  const { logout, user, isAuthenticated, hasRole } = useAuthStore();
  const [loading, setLoading] = useState(false);

  const handleLogin = async (form) => {
    setLoading(true);
    try {
      const data = await loginApi(form);
      await authLogin(data.access_token, data.refresh_token);
      toast.success("Welcome back!");
      navigate("/");
    } catch (err) {
      const msg = getApiErrorMessage(err, "Login failed. Check your credentials.");
      toast.error(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (form) => {
    setLoading(true);
    try {
      await registerApi(form);
      toast.success("Account created! Please sign in.");
      navigate("/login");
    } catch (err) {
      toast.error(getApiErrorMessage(err, "Registration failed. Please try again."));
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return {
    user,
    isAuthenticated,
    hasRole,
    loading,
    handleLogin,
    handleRegister,
    handleLogout,
  };
}
