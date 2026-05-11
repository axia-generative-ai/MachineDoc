import { useEffect, useState } from 'react';

export type ThemePreference = 'dark' | 'light';

const THEME_KEY = 'MachineDoc.theme';

function isThemePreference(value: string | null): value is ThemePreference {
  return value === 'dark' || value === 'light';
}

export function getStoredThemePreference(): ThemePreference {
  if (typeof window === 'undefined') return 'dark';

  const stored = window.localStorage.getItem(THEME_KEY);
  return isThemePreference(stored) ? stored : 'dark';
}

export function applyThemePreference(theme: ThemePreference) {
  if (typeof document === 'undefined') return;

  document.documentElement.dataset.theme = theme;
  document.documentElement.style.colorScheme = theme;
}

export function setStoredThemePreference(theme: ThemePreference) {
  window.localStorage.setItem(THEME_KEY, theme);
  applyThemePreference(theme);
}

export function initializeThemePreference() {
  applyThemePreference(getStoredThemePreference());
}

export function useThemePreference() {
  const [theme, setTheme] = useState<ThemePreference>(() => getStoredThemePreference());

  useEffect(() => {
    applyThemePreference(theme);
  }, [theme]);

  const updateTheme = (nextTheme: ThemePreference) => {
    setTheme(nextTheme);
    setStoredThemePreference(nextTheme);
  };

  return {
    theme,
    isLightMode: theme === 'light',
    setTheme: updateTheme,
  };
}
