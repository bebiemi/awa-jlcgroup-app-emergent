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
  const navigate = useNavigate()
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

    // Groupe (section + enfants)
    if (item.path === '#' || hasChildren) {
      return (
        <div key={item.id}>
          <button
            type="button"
            onClick={() => toggleSection(sectionKey)}
            className="w-full flex items-center justify-between px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <div className="flex items-center gap-3">
              {Icon && <Icon className="h-5 w-5" />}
              <span>{item.label}</span>
            </div>
            {expanded ? (
              <ChevronDownIcon className="h-4 w-4" />
            ) : (
              <ChevronRightIcon className="h-4 w-4" />
            )}
          </button>

          {expanded && children.length > 0 && (
            <div className="ml-4 mt-1 space-y-1">
              {children.map(renderMenuItem)}
            </div>
          )}
        </div>
      )
    }

    // Item "simple" - Desktop: sidebar reste ouverte, Mobile: ferme
    const handleClick = (e: React.MouseEvent) => {
      e.preventDefault()
      
      // Naviguer avec React Router (pas de rechargement)
      navigate(item.path)
      
      // Fermer seulement en mobile
      if (window.innerWidth < 1024) {
        closeSidebar()
      }
    }

    return (
      <a
        key={item.id}
        href={item.path}
        onClick={handleClick}
        className={`flex items-center gap-3 px-4 py-2 text-sm rounded-lg transition-colors cursor-pointer ${
          isActive
            ? 'bg-gradient-to-r from-jlc-purple-600 to-indigo-600 text-white'
            : 'text-gray-700 hover:bg-gray-100'
        }`}
      >
        {Icon && <Icon className="h-5 w-5" />}
        <span>{item.label}</span>
      </a>
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

      {/* Sidebar V2 - Classique */}
      <aside
        className={`fixed top-0 left-0 h-full w-64 bg-white shadow-xl z-50 transform transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Header avec logo */}
          <div className="p-4 border-b border-gray-200">
            <Link to={dashboardPath} className="flex items-center gap-3">
              <img
                src="/logo-jlc.png"
                alt="JLC Group"
                className="h-12 w-auto object-contain"
              />
            </Link>
          </div>

          {/* User info */}
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center gap-3">
              <div className="flex-shrink-0">
                <div className="h-10 w-10 rounded-full bg-gradient-to-r from-jlc-purple-600 to-indigo-600 flex items-center justify-center text-white font-semibold">
                  {user.first_name?.[0] || user.username?.[0] || 'U'}
                </div>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {user.first_name} {user.last_name}
                </p>
                <p className="text-xs text-gray-500 truncate capitalize">
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
          <div className="p-4 border-t border-gray-200">
            <p className="text-xs text-gray-500 text-center">
              © {new Date().getFullYear()} JLC Group
            </p>
          </div>
        </div>
      </aside>
    </>
  )
}
