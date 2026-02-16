import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  MessageSquare,
  Search,
  User,
  List,
  Activity,
  Settings,
  LogOut,
  Shield,
  Menu,
  X,
  Plus,
} from "lucide-react";
import useAuthStore from "../../stores/authStore";
import Avatar from "../common/Avatar";
import NotificationBell from "../notification/NotificationBell";

export default function Navbar() {
  const { user, logout, hasRole } = useAuthStore();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const isAdmin = hasRole("admin");
  const isModerator = hasRole("moderator") || isAdmin;

  return (
    <nav className="sticky top-0 z-40 border-b border-gray-200 bg-white text-gray-900 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 shrink-0">
            <MessageSquare size={26} className="text-indigo-600" />
            <span className="text-lg font-bold text-gray-900 hidden sm:block">
              Forum
            </span>
          </Link>

          {/* Right side actions */}
          <div className="flex items-center gap-2">
            {isAdmin && (
              <Link
                to="/admin"
                className="hidden md:inline-flex px-3 py-2 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-100 hover:text-gray-900 transition-colors dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-slate-100"
              >
                <Shield size={18} />
              </Link>
            )}
            {isModerator && (
              <Link
                to="/moderation"
                className="hidden md:inline-flex px-3 py-2 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-100 hover:text-gray-900 transition-colors dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-slate-100"
              >
                Moderation
              </Link>
            )}
            <Link
              to="/search"
              className="hidden sm:inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl border border-gray-200 bg-white text-sm font-medium text-gray-900 hover:bg-gray-50 transition-colors dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:hover:bg-slate-800"
              title="Search"
            >
              <Search size={16} />
              Search
            </Link>
            <Link
              to="/threads/new"
              className="hidden sm:inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700 transition-colors shadow-sm"
            >
              <Plus size={16} />
              New Thread
            </Link>

            {/* Notification bell */}
            <NotificationBell />

            {/* Profile dropdown */}
            <div className="relative">
              <button
                onClick={() => setProfileOpen(!profileOpen)}
                className="flex items-center gap-2 rounded-xl border border-transparent p-1 transition-colors hover:border-gray-200 hover:bg-gray-100 dark:hover:border-slate-700 dark:hover:bg-slate-800"
              >
                <Avatar
                  name={user?.full_name}
                  avatarUrl={user?.avatar_url}
                  size="sm"
                />
              </button>

              {profileOpen && (
                <>
                  <div
                    className="fixed inset-0 z-10"
                    onClick={() => setProfileOpen(false)}
                  />
                  <div className="absolute right-0 z-20 mt-2 w-60 rounded-2xl border border-gray-200 bg-white py-1.5 shadow-lg dark:border-slate-700 dark:bg-slate-900">
                    <div className="border-b border-gray-100 px-4 py-3 dark:border-slate-700">
                      <p className="text-sm font-medium text-gray-900 dark:text-slate-100">
                        {user?.full_name}
                      </p>
                      <p className="truncate text-xs text-gray-500 dark:text-slate-400">
                        @{user?.username}
                      </p>
                    </div>
                    <Link
                      to="/profile"
                      onClick={() => setProfileOpen(false)}
                      className="flex items-center gap-2 px-4 py-2.5 text-sm text-gray-900 hover:bg-gray-50 dark:text-slate-100 dark:hover:bg-slate-800"
                    >
                      <User size={16} /> Profile
                    </Link>
                    <Link
                      to="/my-threads"
                      onClick={() => setProfileOpen(false)}
                      className="flex items-center gap-2 px-4 py-2.5 text-sm text-gray-900 hover:bg-gray-50 dark:text-slate-100 dark:hover:bg-slate-800"
                    >
                      <List size={16} /> My Threads
                    </Link>
                    <Link
                      to="/my-activity"
                      onClick={() => setProfileOpen(false)}
                      className="flex items-center gap-2 px-4 py-2.5 text-sm text-gray-900 hover:bg-gray-50 dark:text-slate-100 dark:hover:bg-slate-800"
                    >
                      <Activity size={16} /> My Activity
                    </Link>
                    <Link
                      to="/settings"
                      onClick={() => setProfileOpen(false)}
                      className="flex items-center gap-2 px-4 py-2.5 text-sm text-gray-900 hover:bg-gray-50 dark:text-slate-100 dark:hover:bg-slate-800"
                    >
                      <Settings size={16} /> Settings
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="flex items-center gap-2 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 w-full text-left"
                    >
                      <LogOut size={16} /> Log out
                    </button>
                  </div>
                </>
              )}
            </div>

            {/* Mobile hamburger */}
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="rounded-lg p-2 text-gray-700 hover:bg-gray-100 md:hidden dark:text-slate-300 dark:hover:bg-slate-800"
            >
              {mobileOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileOpen && (
          <div className="mt-1 space-y-1 border-t border-gray-100 pb-4 pt-3 md:hidden dark:border-slate-700">
            <Link
              to="/threads/new"
              onClick={() => setMobileOpen(false)}
              className="block rounded-lg px-3 py-2 text-sm font-medium text-gray-900 hover:bg-gray-100 dark:text-slate-100 dark:hover:bg-slate-800"
            >
              New Thread
            </Link>
            <Link
              to="/search"
              onClick={() => setMobileOpen(false)}
              className="block rounded-lg px-3 py-2 text-sm font-medium text-gray-900 hover:bg-gray-100 dark:text-slate-100 dark:hover:bg-slate-800"
            >
              Search
            </Link>
            {isAdmin && (
              <Link
                to="/admin"
                onClick={() => setMobileOpen(false)}
                className="block rounded-lg px-3 py-2 text-sm font-medium text-gray-900 hover:bg-gray-100 dark:text-slate-100 dark:hover:bg-slate-800"
              >
                Admin Dashboard
              </Link>
            )}
            {isModerator && (
              <Link
                to="/moderation"
                onClick={() => setMobileOpen(false)}
                className="block rounded-lg px-3 py-2 text-sm font-medium text-gray-900 hover:bg-gray-100 dark:text-slate-100 dark:hover:bg-slate-800"
              >
                Moderation
              </Link>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}
