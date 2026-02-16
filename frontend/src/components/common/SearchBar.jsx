import { useState } from "react";
import { Search } from "lucide-react";
import PropTypes from "prop-types";

export default function SearchBar({
  placeholder = "Search...",
  onSearch,
  onChangeSearch,
  initialValue = "",
  className = "",
}) {
  const [value, setValue] = useState(initialValue);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(value.trim());
  };

  return (
    <form onSubmit={handleSubmit} className={`relative ${className}`}>
      <Search
        size={18}
        className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
      />
      <input
        type="text"
        value={value}
        onChange={(e) => {
          const next = e.target.value;
          setValue(next);
          if (onChangeSearch) onChangeSearch(next.trim());
        }}
        placeholder={placeholder}
        className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-300 text-sm
          placeholder-gray-400 shadow-sm transition-colors
          focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
      />
    </form>
  );
}

SearchBar.propTypes = {
  placeholder: PropTypes.string,
  onSearch: PropTypes.func.isRequired,
  onChangeSearch: PropTypes.func,
  initialValue: PropTypes.string,
  className: PropTypes.string,
};
