import React, { createContext, useContext, useEffect, useState } from "react";

export const THEMES = [
  {
    id: "paper-iris",
    name: "Paper / Iris",
    personality: "Editorial Magazine",
    description: "Warm paper ivory, deep charcoal typography, vibrant iris accent",
    mode: "light",
    preview: { bg: "#F9F8F5", surface: "#FFFFFF", accent: "#4F46E5", text: "#1C1C1E" }
  },
  {
    id: "midnight-nebula",
    name: "Midnight / Nebula",
    personality: "Deep AI Workspace",
    description: "Near-black navy, electric indigo glow, crisp warm white typography",
    mode: "dark",
    preview: { bg: "#0B0E14", surface: "#171B26", accent: "#6366F1", text: "#F1F3F9" }
  },
  {
    id: "clay-sunrise",
    name: "Clay / Sunrise",
    personality: "Creative Studio",
    description: "Warm cream, dark brown-charcoal, terracotta and coral warmth",
    mode: "light",
    preview: { bg: "#FAF6F0", surface: "#FFFFFF", accent: "#D9532F", text: "#261F1A" }
  },
  {
    id: "moss-graphite",
    name: "Moss / Graphite",
    personality: "Technical & Mature",
    description: "Soft graphite and stone, emerald moss accent, high clarity",
    mode: "dark",
    preview: { bg: "#181B1A", surface: "#252A28", accent: "#34D399", text: "#EDF2EE" }
  },
  {
    id: "ocean-mist",
    name: "Ocean / Mist",
    personality: "Analytical & Focused",
    description: "Misty white-blue, deep navy typography, deep teal accents",
    mode: "light",
    preview: { bg: "#F2F7FA", surface: "#FFFFFF", accent: "#0284C7", text: "#0E2233" }
  },
  {
    id: "cinema-night",
    name: "Cinema / Night",
    personality: "Atmospheric & Reflective",
    description: "Deep noir slate, warm amber gold accents, cinematic contrast",
    mode: "dark",
    preview: { bg: "#1C1B18", surface: "#25231E", accent: "#D4AD63", text: "#F0E8D7" }
  },
  {
    id: "mono-graphite",
    name: "Mono / Graphite",
    personality: "Technical Precision",
    description: "Precision graphite and stone, clean slate accents, high contrast",
    mode: "light",
    preview: { bg: "#E9E9E3", surface: "#F2F2EC", accent: "#414C49", text: "#292D2D" }
  },
];

const ALIASES = {
  paper: "paper-iris",
  "paper-ink": "paper-iris",
  editorial: "paper-iris",
  black: "midnight-nebula",
  "black-cobalt": "midnight-nebula",
  midnight: "midnight-nebula",
  clay: "clay-sunrise",
  "clay-poster": "clay-sunrise",
  botanical: "moss-graphite",
  "botanical-moss": "moss-graphite",
  graphite: "moss-graphite",
  ocean: "ocean-mist",
  cinema: "cinema-night",
  mono: "mono-graphite",
};

const ThemeContext = createContext({
  theme: "paper-iris",
  setTheme: () => {},
  themes: THEMES,
  currentThemeMeta: THEMES[0],
});

const THEME_STORAGE_KEY = "careerverse_theme_preference_v2";

export function ThemeProvider({ children }) {
  const [theme, setThemeState] = useState(() => {
    try {
      const saved = localStorage.getItem(THEME_STORAGE_KEY);
      if (saved) {
        const resolved = ALIASES[saved] || saved;
        if (THEMES.some((t) => t.id === resolved)) return resolved;
      }
    } catch {
      // localStorage not accessible
    }
    if (typeof window !== "undefined" && window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
      return "midnight-nebula";
    }
    return "paper-iris";
  });

  const setTheme = (newTheme) => {
    const resolved = ALIASES[newTheme] || newTheme;
    if (THEMES.some((t) => t.id === resolved)) {
      setThemeState(resolved);
      try {
        localStorage.setItem(THEME_STORAGE_KEY, resolved);
      } catch {
        // storage quota / unavailable
      }
    }
  };

  const currentThemeMeta = THEMES.find((t) => t.id === theme) || THEMES[0];

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    const isDark = currentThemeMeta.mode === "dark";
    document.documentElement.setAttribute("data-color-mode", isDark ? "dark" : "light");
    document.documentElement.style.colorScheme = isDark ? "dark" : "light";
  }, [theme, currentThemeMeta]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme, themes: THEMES, currentThemeMeta }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
}
