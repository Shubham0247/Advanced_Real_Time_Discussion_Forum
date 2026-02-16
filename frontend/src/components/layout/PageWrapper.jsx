import PropTypes from "prop-types";

export default function PageWrapper({ children, className = "" }) {
  return (
    <main className={`max-w-5xl mx-auto px-4 sm:px-6 py-7 ${className}`}>
      {children}
    </main>
  );
}

PageWrapper.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.string,
};
