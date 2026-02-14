import PropTypes from "prop-types";
import { MessageSquare } from "lucide-react";

/**
 * Centered card layout for login / register / password reset pages.
 */
export default function AuthLayout({ children, title, subtitle }) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-purple-50 px-4">
      <div className="mb-8 text-center">
        <div className="flex items-center justify-center gap-2 mb-2">
          <MessageSquare size={36} className="text-indigo-600" />
          <span className="text-2xl font-bold text-gray-900">Forum</span>
        </div>
        {subtitle && (
          <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
        )}
      </div>

      <div className="w-full max-w-md bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
        {title && (
          <h1 className="text-xl font-semibold text-gray-900 mb-6">{title}</h1>
        )}
        {children}
      </div>
    </div>
  );
}

AuthLayout.propTypes = {
  children: PropTypes.node.isRequired,
  title: PropTypes.string,
  subtitle: PropTypes.string,
};
