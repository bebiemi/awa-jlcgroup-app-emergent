import {
  createContext,
  useContext,
  useState,
  useMemo,
  type ReactNode,
} from 'react'
import { SIDEBAR_THEMES } from '@/config/sidebarThemes'

type ThemeName = keyof typeof SIDEBAR_THEMES

interface SidebarThemeContextValue {
  theme: ThemeName
  setTheme: (theme: ThemeName) => void
  themeConfig: (typeof SIDEBAR_THEMES)[ThemeName]
}

const SidebarThemeContext = createContext<SidebarThemeContextValue | undefined>(
  undefined,
)

function safeReadTheme(): ThemeName {
  if (typeof window === 'undefined') return 'dark'
  try {
    const stored = localStorage.getItem('sidebar_theme')
    if (stored && stored in SIDEBAR_THEMES) {
      return stored as ThemeName
    }
    return 'dark'
  } catch {
    return 'dark'
  }
}

export function SidebarThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<ThemeName>(safeReadTheme)

  const setTheme = (next: ThemeName) => {
    setThemeState(next)
    try {
      localStorage.setItem('sidebar_theme', next)
    } catch {
      // mode privé ou environnement restreint
    }
  }

  const value = useMemo<SidebarThemeContextValue>(
    () => ({
      theme,
      setTheme,
      themeConfig: SIDEBAR_THEMES[theme],
    }),
    [theme],
  )

  return (
    <SidebarThemeContext.Provider value={value}>
      {children}
    </SidebarThemeContext.Provider>
  )
}

export function useSidebarTheme(): SidebarThemeContextValue {
  const ctx = useContext(SidebarThemeContext)
  if (!ctx) {
    throw new Error('useSidebarTheme must be used within a SidebarThemeProvider')
  }
  return ctx
}