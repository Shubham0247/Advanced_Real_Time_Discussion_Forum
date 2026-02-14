import PropTypes from "prop-types";

export default function Input({
  label,
  error,
  id,
  className = "",
  ...props
}) {
  return (
    <div className="w-full">
      {label && (
        <label
          htmlFor={id}
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          {label}
        </label>
      )}
      <input
        id={id}
        className={`
          block w-full rounded-lg border px-3 py-2 text-sm
          placeholder-gray-400 shadow-sm transition-colors
          focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500
          ${error ? "border-red-400" : "border-gray-300"}
          ${className}
        `}
        {...props}
      />
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  );
}

Input.propTypes = {
  label: PropTypes.string,
  error: PropTypes.string,
  id: PropTypes.string,
  className: PropTypes.string,
};
