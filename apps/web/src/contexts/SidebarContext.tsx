import {
  createContext,
  useCallback,
  useContext,
  useState,
  useMemo,
  useEffect,
  type ReactNode,
} from 'react'

/**
 * Lecture sécurisée du localStorage
 */
function safeReadOpenGroups(): string[] {
  if (typeof window === 'undefined') return []
  try {
    const stored = localStorage.getItem('sidebar_open_groups')
    return stored ? JSON.parse(stored) : []
  } catch {
    return []
  }
}

interface SidebarContextValue {
  isOpen: boolean
  isCompact: boolean
  openGroups: string[]
  sidebarWidth: number
  setSidebarWidth: (width: number) => void
  toggleCompact: () => void
  toggleGroup: (id: string) => void
  openSidebar: () => void
  closeSidebar: () => void
  toggleSidebar: () => void
}

const SidebarContext = createContext<SidebarContextValue | undefined>(undefined)

export function SidebarProvider({ children }: { children: ReactNode }) {
  /**
   * État initial aligné avec le viewport pour éviter le flash gauche/droite :
   * - Desktop (>=1024px) : ouvert
   * - Mobile : fermé
   */
  const [isOpen, setIsOpen] = useState(() => {
    if (typeof window === 'undefined') return false
    return window.matchMedia('(min-width: 1024px)').matches
  })

  /**
   * Mode compact persistant
   */
  const [isCompact, setIsCompact] = useState<boolean>(() => {
    try {
      return localStorage.getItem('sidebar_compact') === '1'
    } catch {
      return false
    }
  })

  /**
   * Listes des groupes ouverts
   */
  const [openGroups, setOpenGroups] = useState<string[]>(safeReadOpenGroups)

  /**
   * Largeur mesurée de la sidebar (pour aligner le layout dynamiquement)
   */
  const [sidebarWidth, setSidebarWidth] = useState<number>(0)

  /**
   * Initialisation responsive (desktop / mobile)
   */
  useEffect(() => {
    if (typeof window === 'undefined') return

    const mq = window.matchMedia('(min-width: 1024px)')
    const update = () => setIsOpen(mq.matches)

    update()
    mq.addEventListener('change', update)
    return () => mq.removeEventListener('change', update)
  }, [])

  /**
   * Compact toggle + persistance
   */
  const toggleCompact = useCallback(() => {
    setIsCompact((prev) => {
      const next = !prev
      try {
        localStorage.setItem('sidebar_compact', next ? '1' : '0')
      } catch {}
      return next
    })
  }, [])

  /**
   * Groupes
   */
  const toggleGroup = useCallback((id: string) => {
    setOpenGroups((prev) => {
      const next = prev.includes(id)
        ? prev.filter((g) => g !== id)
        : [...prev, id]

      try {
        localStorage.setItem('sidebar_open_groups', JSON.stringify(next))
      } catch {}

      return next
    })
  }, [])

  const value = useMemo<SidebarContextValue>(() => ({
    isOpen,
    isCompact,
    openGroups,
    sidebarWidth,
    setSidebarWidth,
    toggleCompact,
    toggleGroup,
    openSidebar: () => setIsOpen(true),
    closeSidebar: () => setIsOpen(false),
    toggleSidebar: () => setIsOpen((prev) => !prev),
  }), [isOpen, isCompact, openGroups, sidebarWidth, toggleCompact, toggleGroup])

  return (
    <SidebarContext.Provider value={value}>
      {children}
    </SidebarContext.Provider>
  )
}

export function useSidebar(): SidebarContextValue {
  const context = useContext(SidebarContext)
  if (!context) {
    throw new Error('useSidebar must be used within a SidebarProvider')
  }
  return context
}
