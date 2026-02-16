import { useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import useAuthStore from "../stores/authStore";
import { changeMyPassword, deactivateMyAccount } from "../api/authApi";
import { getStoredTheme, setTheme } from "../utils/theme";
import PageWrapper from "../components/layout/PageWrapper";
import Input from "../components/common/Input";
import Button from "../components/common/Button";

export default function SettingsPage() {
  const navigate = useNavigate();
  const { logout } = useAuthStore();
  const [theme, setThemeState] = useState(getStoredTheme());
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [deactivateLoading, setDeactivateLoading] = useState(false);
  const [passwordForm, setPasswordForm] = useState({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });

  const handlePasswordChange = (field) => (e) => {
    setPasswordForm((prev) => ({ ...prev, [field]: e.target.value }));
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    const { current_password, new_password, confirm_password } = passwordForm;
    if (!current_password || !new_password || !confirm_password) {
      toast.error("Please fill all password fields");
      return;
    }
    if (new_password.length < 8) {
      toast.error("New password must be at least 8 characters");
      return;
    }
    if (new_password !== confirm_password) {
      toast.error("New password and confirm password do not match");
      return;
    }

    setPasswordLoading(true);
    try {
      await changeMyPassword({ current_password, new_password });
      setPasswordForm({
        current_password: "",
        new_password: "",
        confirm_password: "",
      });
      toast.success("Password changed successfully");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to change password");
    } finally {
      setPasswordLoading(false);
    }
  };

  const handleThemeChange = (e) => {
    const next = e.target.value;
    setThemeState(next);
    setTheme(next);
    toast.success("Theme updated");
  };

  const handleDeactivate = async () => {
    if (
      !confirm(
        "Are you sure you want to deactivate your account? You will be logged out immediately."
      )
    ) {
      return;
    }

    setDeactivateLoading(true);
    try {
      await deactivateMyAccount();
      logout();
      toast.success("Account deactivated");
      navigate("/login");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to deactivate account");
    } finally {
      setDeactivateLoading(false);
    }
  };

  return (
    <PageWrapper className="max-w-2xl">
      <h1 className="text-2xl font-semibold tracking-tight text-gray-900 mb-6">Settings</h1>

      <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Change Theme</h2>
        <label
          htmlFor="theme_select"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Theme
        </label>
        <select
          id="theme_select"
          value={theme}
          onChange={handleThemeChange}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm
            focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        >
          <option value="light">Light</option>
          <option value="dark">Dark</option>
          <option value="system">System</option>
        </select>
      </div>

      <div className="bg-white rounded-2xl border border-gray-200 p-6 mt-6 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Reset Password</h2>
        <form onSubmit={handlePasswordSubmit} className="space-y-4">
          <Input
            id="current_password"
            label="Current Password"
            type="password"
            value={passwordForm.current_password}
            onChange={handlePasswordChange("current_password")}
            placeholder="Enter current password"
          />
          <Input
            id="new_password"
            label="New Password"
            type="password"
            value={passwordForm.new_password}
            onChange={handlePasswordChange("new_password")}
            placeholder="Minimum 8 characters"
          />
          <Input
            id="confirm_password"
            label="Confirm New Password"
            type="password"
            value={passwordForm.confirm_password}
            onChange={handlePasswordChange("confirm_password")}
            placeholder="Re-enter new password"
          />
          <div className="flex justify-end pt-2">
            <Button type="submit" loading={passwordLoading}>
              Update Password
            </Button>
          </div>
        </form>
      </div>

      <div className="bg-white rounded-2xl border border-red-200 p-6 mt-6 shadow-sm">
        <h2 className="text-lg font-semibold text-red-600 mb-2">Deactivate Account</h2>
        <p className="text-sm text-gray-600 mb-4">
          This will deactivate your account and log you out.
        </p>
        <div className="flex justify-end">
          <Button
            type="button"
            variant="danger"
            loading={deactivateLoading}
            onClick={handleDeactivate}
          >
            Deactivate Account
          </Button>
        </div>
      </div>
    </PageWrapper>
  );
}
