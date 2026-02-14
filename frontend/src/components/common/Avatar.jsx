import PropTypes from "prop-types";

const sizeMap = {
  sm: "h-8 w-8 text-xs",
  md: "h-10 w-10 text-sm",
  lg: "h-14 w-14 text-lg",
};

export default function Avatar({ name, avatarUrl, size = "md" }) {
  const initials = (name || "?")
    .split(" ")
    .map((w) => w[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  if (avatarUrl) {
    return (
      <img
        src={avatarUrl}
        alt={name}
        className={`${sizeMap[size]} rounded-full object-cover ring-2 ring-white`}
      />
    );
  }

  return (
    <div
      className={`${sizeMap[size]} rounded-full bg-indigo-100 text-indigo-700 font-semibold
        flex items-center justify-center ring-2 ring-white`}
    >
      {initials}
    </div>
  );
}

Avatar.propTypes = {
  name: PropTypes.string,
  avatarUrl: PropTypes.string,
  size: PropTypes.oneOf(["sm", "md", "lg"]),
};
