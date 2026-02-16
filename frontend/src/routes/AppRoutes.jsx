import { Routes, Route, Navigate } from "react-router-dom";
import ProtectedRoute from "./ProtectedRoute";
import AdminRoute from "./AdminRoute";

// Pages
import LoginPage from "../pages/LoginPage";
import RegisterPage from "../pages/RegisterPage";
import ForgotPasswordPage from "../pages/ForgotPasswordPage";
import ResetPasswordPage from "../pages/ResetPasswordPage";
import HomePage from "../pages/HomePage";
import CreateThreadPage from "../pages/CreateThreadPage";
import ThreadPage from "../pages/ThreadPage";
import SearchPage from "../pages/SearchPage";
import ProfilePage from "../pages/ProfilePage";
import SettingsPage from "../pages/SettingsPage";
import MyThreadsPage from "../pages/MyThreadsPage";
import MyActivityPage from "../pages/MyActivityPage";
import NotificationsPage from "../pages/NotificationsPage";
import AdminDashboard from "../pages/AdminDashboard";
import ModerationPage from "../pages/ModerationPage";

export default function AppRoutes() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />

      {/* Protected routes — require authentication */}
      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/threads/new" element={<CreateThreadPage />} />
        <Route path="/threads/:threadId" element={<ThreadPage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/my-threads" element={<MyThreadsPage />} />
        <Route path="/my-activity" element={<MyActivityPage />} />
        <Route path="/notifications" element={<NotificationsPage />} />

        {/* Moderator routes */}
        <Route element={<AdminRoute roles={["admin", "moderator"]} />}>
          <Route path="/moderation" element={<ModerationPage />} />
        </Route>

        {/* Admin routes */}
        <Route element={<AdminRoute roles={["admin"]} />}>
          <Route path="/admin" element={<AdminDashboard />} />
        </Route>
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
