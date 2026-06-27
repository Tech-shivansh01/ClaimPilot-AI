"use client";

import { useTheme } from "../lib/ThemeContext";

export default function ThemeToggle() {
  const ctx = useTheme();
  if (!ctx) return null;
  const { theme, toggleTheme } = ctx;

  return (
    <button className="theme-toggle" onClick={toggleTheme} aria-label="Toggle dark mode" title="Toggle dark mode">
      {theme === "light" ? "🌙" : "☀️"}
    </button>
  );
}
