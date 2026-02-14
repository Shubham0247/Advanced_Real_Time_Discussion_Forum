import PropTypes from "prop-types";

export default function PageWrapper({ children, className = "" }) {
  return (
    <main className={`max-w-4xl mx-auto px-4 sm:px-6 py-6 ${className}`}>
      {children}
    </main>
  );
}

PageWrapper.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.string,
};
