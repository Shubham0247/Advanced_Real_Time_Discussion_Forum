export default function Footer() {
  return (
    <footer className="border-t border-gray-100 bg-white mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between text-xs text-gray-400">
        <p>&copy; {new Date().getFullYear()} Discussion Forum</p>
        <p>Built with React &middot; Tailwind CSS</p>
      </div>
    </footer>
  );
}
