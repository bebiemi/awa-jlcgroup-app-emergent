/**
 * Sidebar Refactorisée V2
 * - Pilotée par configuration (navigation.config.ts)
 * - Utilise useSidebarItems() + useSidebar()
 * - Un seul état global isOpen
 */

import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAppSelector } from '@/store/hooks'
import { useSidebar } from '@/contexts/SidebarContext'
import { useSidebarItems, useCurrentContext } from '@/hooks/useNavigationConfig'
import { useDashboardPath } from '@/hooks/useDashboardPath'
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
  ChevronDownIcon,
  ChevronRightIcon,
} from '@heroicons/react/24/outline'

// Map des icônes (nom string → composant React)
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
}

export default function SidebarNew() {
  const location = useLocation()
  const { user } = useAppSelector((state) => state.auth)
  const { isOpen, closeSidebar } = useSidebar()
  const context = useCurrentContext()
  const dashboardPath = useDashboardPath()
  const sidebarItems = useSidebarItems()

  const [expandedSections, setExpandedSections] = useState<string[]>([])

  if (!user) return null

  const toggleSection = (sectionTitle: string) => {
    setExpandedSections((prev) =>
      prev.includes(sectionTitle)
        ? prev.filter((s) => s !== sectionTitle)
        : [...prev, sectionTitle]
    )
  }

  const isSectionExpanded = (sectionTitle: string) => {
    return expandedSections.includes(sectionTitle)
  }

  const isPathActive = (path: string) => {
    return (
      location.pathname === path ||
      location.pathname.startsWith(path + '/')
    )
  }

  // Grouper les items par parentId (construire la hiérarchie)
  const rootItems = sidebarItems.filter(
    (item) => !item.parentId && !item.hidden
  )

  const getChildren = (parentId: string) => {
    return sidebarItems.filter(
      (item) => item.parentId === parentId && !item.hidden
    )
  }

  const renderMenuItem = (item: any) => {
    const Icon = item.icon ? ICON_MAP[item.icon] : null
    const isActive = isPathActive(item.path)
    const children = getChildren(item.id)
    const hasChildren = children.length > 0
    const sectionKey = item.label || item.id
    const expanded = isSectionExpanded(sectionKey)

    if (item.path === '#' || hasChildren) {
      return (
        <div key={item.id}>
          <button
            type="button"
            onClick={() => toggleSection(sectionKey)}
            className="group w-full flex items-center justify-between px-4 py-2 text-sm font-medium text-gray-700 hover:bg-white/10 rounded-lg transition-colors"
          >
            <div className="flex items-center gap-3">
              {Icon && (
                <Icon className="h-5 w-5 text-gray-500 group-hover:text-jlc-purple-500 transition-colors" />
              )}
              <span>{item.label}</span>
            </div>
            {expanded ? (
              <ChevronDownIcon className="h-4 w-4 text-gray-400" />
            ) : (
              <ChevronRightIcon className="h-4 w-4 text-gray-400" />
            )}
          </button>

          {expanded && children.length > 0 && (
            <div className="ml-4 mt-1 space-y-1 border-l border-white/10 pl-2">
              {children.map(renderMenuItem)}
            </div>
          )}
        </div>
      )
    }

    // Item "simple" - Desktop: sidebar reste ouverte, Mobile: ferme
    return (
      <Link
        key={item.id}
        to={item.path}
        onClick={() => {
          if (window.innerWidth < 1024) closeSidebar() // mobile only
        }}
        className={`group relative flex items-center gap-3 px-4 py-2 text-sm rounded-lg transition-all ${
          isActive
            ? 'bg-white/10 text-white shadow-sm'
            : 'text-gray-100 hover:bg-white/5'
        }`}
      >
        {/* Barre active à gauche */}
        {isActive && (
          <span className="absolute left-0 top-1/2 -translate-y-1/2 h-7 w-1 rounded-full bg-jlc-accent-yellow" />
        )}

        <span className="flex items-center gap-3 pl-1">
          {Icon && (
            <Icon className="h-5 w-5 transition-transform group-hover:scale-110" />
          )}
          <span className="truncate">{item.label}</span>
        </span>
      </Link>
    )
  }

  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={closeSidebar}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 h-full w-64 bg-gradient-to-b from-jlc-purple-900 via-jlc-purple-800 to-slate-900 text-gray-100 shadow-2xl z-50 transform transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-4 border-b border-white/10">
            <Link
              to={dashboardPath}
              className="flex items-center gap-3"
            >
              <img
                src="/logo-jlc.png"
                alt="JLC Group"
                className="h-12 w-auto object-contain drop-shadow"
              />
            </Link>
          </div>

          {/* User info */}
          <div className="p-4 border-b border-white/10">
            <div className="flex items-center gap-3">
              <div className="flex-shrink-0">
                <div className="h-10 w-10 rounded-full bg-gradient-to-tr from-jlc-accent-yellow to-amber-400 flex items-center justify-center text-jlc-purple-900 font-semibold shadow-md">
                  {user.first_name?.[0] || user.username?.[0] || 'U'}
                </div>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">
                  {user.first_name} {user.last_name}
                </p>
                <p className="text-xs text-jlc-accent-yellow/80 truncate capitalize">
                  {context}
                </p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto p-4 space-y-2">
            {rootItems.map(renderMenuItem)}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-white/10">
            <p className="text-[11px] text-gray-300 text-center">
              © {new Date().getFullYear()} JLC Group
            </p>
          </div>
        </div>
      </aside>
    </>
  )
}
