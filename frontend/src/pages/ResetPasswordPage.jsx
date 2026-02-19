import { useState } from "react";
import { Link, useSearchParams, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import AuthLayout from "../components/layout/AuthLayout";
import Input from "../components/common/Input";
import Button from "../components/common/Button";
import { resetPassword } from "../api/authApi";

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const emailFromQuery = searchParams.get("email") || "";

  const [form, setForm] = useState({
    email: emailFromQuery,
    otp: "",
    new_password: "",
    confirmPassword: "",
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const validate = () => {
    const e = {};
    if (!form.email) e.email = "Email is required";
    if (!form.otp) e.otp = "OTP is required";
    if (!form.new_password || form.new_password.length < 8)
      e.new_password = "Password must be at least 8 characters";
    if (form.new_password !== form.confirmPassword)
      e.confirmPassword = "Passwords do not match";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    try {
      await resetPassword({
        email: form.email,
        otp: form.otp,
        new_password: form.new_password,
      });
      toast.success("Password reset successfully! Please sign in.");
      navigate("/login");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Reset failed. OTP may be invalid or expired.");
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
    if (errors[field]) setErrors((prev) => ({ ...prev, [field]: "" }));
  };

  return (
    <AuthLayout title="Set new password" subtitle="Enter OTP and your new password">
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          id="email"
          label="Email"
          type="email"
          placeholder="you@example.com"
          value={form.email}
          onChange={handleChange("email")}
          error={errors.email}
          autoFocus={!emailFromQuery}
        />
        <Input
          id="otp"
          label="OTP"
          placeholder="Enter the OTP from your email"
          value={form.otp}
          onChange={handleChange("otp")}
          error={errors.otp}
          autoFocus={!!emailFromQuery}
        />
        <Input
          id="new_password"
          label="New Password"
          type="password"
          placeholder="Min. 8 characters"
          value={form.new_password}
          onChange={handleChange("new_password")}
          error={errors.new_password}
        />
        <Input
          id="confirmPassword"
          label="Confirm Password"
          type="password"
          placeholder="Re-enter new password"
          value={form.confirmPassword}
          onChange={handleChange("confirmPassword")}
          error={errors.confirmPassword}
        />

        <Button type="submit" loading={loading} className="w-full">
          Reset Password
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-gray-500">
        <Link
          to="/login"
          className="font-medium text-indigo-600 hover:text-indigo-500"
        >
          Back to sign in
        </Link>
      </p>
    </AuthLayout>
  );
}
