import { useState, useEffect } from "react";
import toast from "react-hot-toast";
import useAuthStore from "../stores/authStore";
import { updateProfile, uploadAvatar } from "../api/authApi";
import PageWrapper from "../components/layout/PageWrapper";
import Avatar from "../components/common/Avatar";
import Input from "../components/common/Input";
import Button from "../components/common/Button";

export default function ProfilePage() {
  const { user, setUser } = useAuthStore();

  const [form, setForm] = useState({
    full_name: "",
    bio: "",
  });
  const [selectedAvatar, setSelectedAvatar] = useState(null);
  const [avatarPreview, setAvatarPreview] = useState("");
  const [avatarObjectUrl, setAvatarObjectUrl] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) {
      setForm({
        full_name: user.full_name || "",
        bio: user.bio || "",
      });
      setAvatarPreview(user.avatar_url || "");
    }
  }, [user]);

  useEffect(() => {
    return () => {
      if (avatarObjectUrl) {
        URL.revokeObjectURL(avatarObjectUrl);
      }
    };
  }, [avatarObjectUrl]);

  const handleChange = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      let avatarUrl = user.avatar_url || "";
      if (selectedAvatar) {
        const avatarUpdatedUser = await uploadAvatar(selectedAvatar);
        avatarUrl = avatarUpdatedUser.avatar_url || avatarUrl;
      }

      const updated = await updateProfile({
        full_name: form.full_name,
        bio: form.bio,
        avatar_url: avatarUrl,
      });
      setUser(updated);
      setSelectedAvatar(null);
      setAvatarPreview(updated.avatar_url || "");
      toast.success("Profile updated!");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to update profile");
    } finally {
      setLoading(false);
    }
  };

  if (!user) return null;

  return (
    <PageWrapper className="max-w-2xl">
      <h1 className="text-2xl font-semibold tracking-tight text-gray-900 mb-6">Your Profile</h1>

      <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6 pb-6 border-b border-gray-200">
          <Avatar name={form.full_name || user.full_name} avatarUrl={avatarPreview} size="lg" />
          <div>
            <h2 className="text-lg font-semibold text-gray-900">
              {user.full_name}
            </h2>
            <p className="text-sm text-gray-500">@{user.username}</p>
            <p className="text-xs text-gray-400">{user.email}</p>
            <div className="flex gap-1.5 mt-1.5">
              {user.roles?.map((r) => (
                <span
                  key={r.id}
                  className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-indigo-50 text-indigo-600"
                >
                  {r.name}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Edit form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            id="full_name"
            label="Full Name"
            value={form.full_name}
            onChange={handleChange("full_name")}
            placeholder="Your full name"
          />
          <div>
            <label
              htmlFor="avatar_file"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Avatar Image
            </label>
            <input
              id="avatar_file"
              type="file"
              accept="image/png,image/jpeg,image/jpg,image/webp,image/gif"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (!file) return;
                setSelectedAvatar(file);
                const objectUrl = URL.createObjectURL(file);
                if (avatarObjectUrl) {
                  URL.revokeObjectURL(avatarObjectUrl);
                }
                setAvatarObjectUrl(objectUrl);
                setAvatarPreview(objectUrl);
              }}
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm
                file:mr-4 file:rounded-md file:border-0 file:bg-indigo-50 file:px-3 file:py-1.5
                file:text-xs file:font-medium file:text-indigo-600 hover:file:bg-indigo-100
                focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
            <p className="text-xs text-gray-400 mt-1">
              Upload PNG/JPG/WEBP/GIF up to 5MB
            </p>
          </div>
          <div>
            <label
              htmlFor="bio"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Bio
            </label>
            <textarea
              id="bio"
              rows={3}
              value={form.bio}
              onChange={handleChange("bio")}
              placeholder="Tell us about yourself..."
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm
                placeholder-gray-400 resize-y
                focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <div className="flex justify-end pt-2">
            <Button type="submit" loading={loading}>
              Save Changes
            </Button>
          </div>
        </form>
      </div>

    </PageWrapper>
  );
}
