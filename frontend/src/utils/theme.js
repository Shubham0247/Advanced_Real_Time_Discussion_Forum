const THEME_KEY = "forum_theme";
const VALID_THEMES = new Set(["light", "dark", "system"]);

function normalizeTheme(theme) {
  const value = String(theme || "").toLowerCase();
  return VALID_THEMES.has(value) ? value : "system";
}

export function getStoredTheme() {
  return normalizeTheme(localStorage.getItem(THEME_KEY));
}

export function applyTheme(theme) {
  const normalizedTheme = normalizeTheme(theme);
  const resolved =
    normalizedTheme === "system"
      ? window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light"
      : normalizedTheme;

  const root = document.documentElement;
  root.classList.remove("dark");
  if (resolved === "dark") {
    root.classList.add("dark");
  }
  root.dataset.theme = resolved;
}

export function setTheme(theme) {
  const normalizedTheme = normalizeTheme(theme);
  localStorage.setItem(THEME_KEY, normalizedTheme);
  applyTheme(normalizedTheme);
}
