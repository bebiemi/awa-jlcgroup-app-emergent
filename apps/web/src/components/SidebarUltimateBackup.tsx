import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAppSelector } from '@/store/hooks'
import { useSidebar } from '@/contexts/SidebarContext'
import { useSidebarItems, useCurrentContext } from '@/hooks/useNavigationConfig'
import { useDashboardPath } from '@/hooks/useDashboardPath'
import { useSidebarTheme } from '@/contexts/SidebarThemeContext'
import SidebarThemeSelector from '@/components/sidebar/SidebarThemeSelector'

import {
  HomeIcon,
  UserGroupIcon,
  BuildingOfficeIcon,
  MapPinIcon,
  ClipboardDocumentCheckIcon,
  BriefcaseIcon,
  ShieldCheckIcon,
  Cog6ToothIcon,
  UserCircleIcon,
  DocumentTextIcon,
  EnvelopeIcon,
  FlagIcon,
  GlobeAltIcon,
  ClockIcon,
  UsersIcon,
  PlusIcon,
  ChevronDownIcon,
  ChevronRightIcon,
  ChevronLeftIcon,
} from '@heroicons/react/24/outline'

/**
 * Table de correspondance des icônes
 */
const ICON_MAP: Record<string, any> = {
  HomeIcon,
  UserGroupIcon,
  BuildingOfficeIcon,
  MapPinIcon,
  ClipboardDocumentCheckIcon,
  BriefcaseIcon,
  ShieldCheckIcon,
  Cog6ToothIcon,
  UserCircleIcon,
  DocumentTextIcon,
  EnvelopeIcon,
  FlagIcon,
  GlobeAltIcon,
  ClockIcon,
  UsersIcon,
  PlusIcon,
}

export default function SidebarUltimate() {
  const location = useLocation()
  const { user } = useAppSelector((state) => state.auth)
  const { isOpen, closeSidebar, openSidebar } = useSidebar()
  const { themeConfig } = useSidebarTheme()
  

  const sidebarItems = useSidebarItems()
  const context = useCurrentContext()
  const dashboardPath = useDashboardPath()

  const [expanded, setExpanded] = useState<string[]>([])

  // Mode compact mémorisé
  const [isCompact, setIsCompact] = useState<boolean>(() => {
    try {
      return localStorage.getItem('sidebar_compact') === '1'
    } catch {
      return false
    }
  })

//   useEffect(() => {
//   if (window.innerWidth >= 1024) {
//     openSidebar();   // Desktop → ouvert
//   } else {
//     closeSidebar();  // Mobile → fermé
//   }
// }, []);

    // const [isReady, setIsReady] = useState(false);
  const toggleCompact = () => {
    setIsCompact((prev) => {
      const next = !prev
      try {
        localStorage.setItem('sidebar_compact', next ? '1' : '0')
      } catch {
        // ignore
      }
      return next
    })
  }

  const isPathActive = (path: string) =>
    location.pathname === path || location.pathname.startsWith(path + '/')

  /**
   * Auto-ouverture des sections correspondant à la route active
   */
  useEffect(() => {
    const ids = new Set(expanded)

    sidebarItems.forEach((item) => {
      if (item.parentId && isPathActive(item.path)) {
        ids.add(item.parentId)
      }
    })

    setExpanded(Array.from(ids))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.pathname, sidebarItems])

  if (!user) return null

  const toggleSection = (id: string) => {
    setExpanded((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    )
  }

  const roots = sidebarItems.filter((i) => !i.parentId && !i.hidden)
  const childrenOf = (id: string) =>
    sidebarItems.filter((i) => i.parentId === id && !i.hidden)

  // Classes de base pour l'effet ink ripple
  const baseRippleClasses =
    "relative overflow-hidden group before:content-[''] before:absolute before:inset-0 before:bg-[radial-gradient(circle_at_center,_rgba(255,255,255,0.35),_transparent_60%)] before:opacity-0 before:scale-0 active:before:opacity-100 active:before:scale-150 before:transition-transform before:duration-500 before:ease-out"

  /**
   * Rendu des items de navigation (sections + liens)
   */
  const renderItem = (item: any) => {
    const Icon = item.icon ? ICON_MAP[item.icon] : null
    const childList = childrenOf(item.id)
    const hasChildren = childList.length > 0
    const isActive = isPathActive(item.path)
    const sectionOpen = expanded.includes(item.id)

    // Section / groupe avec enfants
    if (hasChildren || item.path === '#') {
      return (
        <div key={item.id} className="mb-1 relative">
          <button
            type="button"
            onClick={() => toggleSection(item.id)}
            className={[
              baseRippleClasses,
              'w-full flex items-center justify-between rounded-xl text-sm transition-all duration-200 backdrop-blur-sm',
              themeConfig.sectionHover,
              isCompact ? 'px-3 py-2' : 'px-4 py-2',
            ].join(' ')}
          >
            <div
              className={[
                'flex items-center',
                isCompact ? 'justify-center w-full' : 'gap-3',
              ].join(' ')}
            >
              {Icon && (
                <Icon
                  className={[
                    'h-5 w-5 opacity-80 transition-transform',
                    isCompact ? 'mx-auto' : '',
                  ].join(' ')}
                />
              )}
              {!isCompact && <span className="truncate">{item.label}</span>}
            </div>

            {!isCompact && (
              sectionOpen ? (
                <ChevronDownIcon className="h-4 w-4 opacity-70" />
              ) : (
                <ChevronRightIcon className="h-4 w-4 opacity-70" />
              )
            )}
          </button>

          {/* Tooltip en mode compact */}
          {isCompact && (
            <div
              className="
                pointer-events-none
                absolute left-full top-1/2 ml-3 -translate-y-1/2
                whitespace-nowrap rounded-md border border-white/10
                bg-black/80 px-3 py-1.5 text-xs text-white shadow-xl
                opacity-0 transition-all duration-200
                group-hover:translate-x-0 group-hover:opacity-100
              "
            >
              {item.label}
            </div>
          )}

          {sectionOpen && childList.length > 0 && (
            <div className="ml-4 mt-1 space-y-1 border-l border-white/10 pl-3">
              {childList.map(renderItem)}
            </div>
          )}
        </div>
      )
    }

    // Item simple (lien)
    return (
      <div key={item.id} className="relative">
        <Link
          to={item.path}
          onClick={() => {
            if (window.innerWidth < 1024) closeSidebar()
          }}
          className={[
            baseRippleClasses,
            'flex items-center rounded-xl text-sm backdrop-blur-sm transition-all duration-200 ease-out',
            isCompact ? 'justify-center px-3 py-2' : 'gap-3 px-4 py-2',
            isActive
              ? [
                  themeConfig.activeHighlight,
                  'shadow-[0_0_18px_rgba(0,0,0,0.55)]',
                ].join(' ')
              : [
                  themeConfig.itemInactive,
                  'hover:shadow-[0_4px_16px_rgba(0,0,0,0.35)] hover:-translate-y-[1px]',
                ].join(' '),
          ].join(' ')}
        >
          {/* Halo Premium sous l’icône */}
          {isActive && (
            <span
              className="
                pointer-events-none absolute bottom-1 left-1/2 h-2 w-6
                -translate-x-1/2 rounded-full bg-jlc-accent-yellow/35 blur-md
              "
            />
          )}

          {Icon && (
            <Icon
              className={[
                'h-5 w-5 transition-all',
                isActive
                  ? 'scale-110 text-jlc-accent-yellow drop-shadow-[0_0_6px_rgba(255,235,59,0.55)]'
                  : 'opacity-80 group-hover:opacity-100 group-hover:scale-110',
              ].join(' ')}
            />
          )}

          {!isCompact && (
            <span
              className={[
                'truncate',
                isActive ? 'font-semibold' : 'opacity-90 group-hover:opacity-100',
              ].join(' ')}
            >
              {item.label}
            </span>
          )}
        </Link>

        {/* Tooltip compact premium */}
        {isCompact && (
          <div
            className="
              pointer-events-none absolute left-full top-1/2 ml-3
              -translate-y-1/2 whitespace-nowrap rounded-md border border-white/10
              bg-[#2b0f35]/95 px-3 py-1.5 text-xs text-white shadow-xl
              opacity-0 transition-all duration-200
              group-hover:translate-x-0 group-hover:opacity-100
            "
          >
            {item.label}
          </div>
        )}
      </div>
    )
  }

  return (
    <>
      {/* Overlay mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={closeSidebar}
        />
      )}

      <aside
        className={[
            'fixed top-0 left-0 z-50 h-full transform',
            // isReady ? 'transition-transform duration-300 ease-out' : '',
            isOpen ? 'translate-x-0' : '-translate-x-full',
            isCompact ? 'w-24' : 'w-72',
            'pointer-events-none',
        ].join(' ')}
        >
        {/* Container glassmorphism interne */}
        <div
          className={[
            'pointer-events-auto m-3 flex h[calc(100%-1.5rem)] flex-col',
            'rounded-3xl border border-white/20 shadow-[0_18px_45px_rgba(0,0,0,0.65)]',
            'bg-white/10 bg-blend-overlay backdrop-blur-2xl',
            themeConfig.bg,
            themeConfig.text,
          ].join(' ')}
        >
          {/* Header logo + toggle compact */}
          <div className="flex items-center justify-between border-b border-white/10 px-4 py-3">
            <Link to={dashboardPath} className="flex items-center gap-3">
              <img
                src="/logo-jlc.png"
                alt="JLC Group"
                className={[
                  'w-auto object-contain drop-shadow',
                  isCompact ? 'h-8' : 'h-10',
                ].join(' ')}
              />
            </Link>

            {/* Toggle compact / normal (desktop uniquement) */}
            <button
              type="button"
              onClick={toggleCompact}
              className={[
                baseRippleClasses,
                'relative hidden h-9 w-9 items-center justify-center rounded-full border border-white/25 bg-white/10 text-white shadow-md transition-all duration-200 hover:bg-white/20 lg:inline-flex',
              ].join(' ')}
              title={isCompact ? 'Agrandir la sidebar' : 'Réduire la sidebar'}
            >
              <span className="relative z-10 flex items-center justify-center">
                {isCompact ? (
                  <ChevronRightIcon className="h-4 w-4" />
                ) : (
                  <ChevronLeftIcon className="h-4 w-4" />
                )}
              </span>
            </button>
          </div>

          {/* User + sélecteur de thème */}
          <div className="border-b border-white/10 px-4 py-4">
            <div
              className={[
                'flex items-center',
                isCompact ? 'justify-center' : 'gap-3',
              ].join(' ')}
            >
              <div className="flex-shrink-0">
                <div
                  className={[
                    'flex items-center justify-center rounded-full bg-gradient-to-tr from-[#ffeb3b] to-[#ff9800] font-semibold text-[#362f50] shadow-md',
                    isCompact ? 'mx-auto h-8 w-8' : 'h-10 w-10',
                  ].join(' ')}
                >
                  {user.first_name?.[0] || user.username?.[0] || 'U'}
                </div>
              </div>

              {!isCompact && (
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium">
                    {user.first_name} {user.last_name}
                  </p>
                  <p className="truncate text-xs capitalize opacity-70">
                    {context}
                  </p>
                </div>
              )}
            </div>

            {!isCompact && <SidebarThemeSelector />}
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
            {roots.map(renderItem)}
          </nav>

          {/* Footer */}
          <div className="border-t border-white/10 px-4 py-3 text-center text-[11px] opacity-80">
            © {new Date().getFullYear()} JLC Group
          </div>
        </div>
      </aside>
    </>
  )
}