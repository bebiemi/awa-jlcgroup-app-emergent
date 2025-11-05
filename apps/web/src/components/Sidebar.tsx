import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAppSelector, useAppDispatch } from '@/store/hooks'
import { logoutAction } from '@/features/auth/slices/authSlice'
import { useRoles } from '@/hooks/useAppConfig'
import {
  HomeIcon,
  UserGroupIcon,
  ClipboardDocumentCheckIcon,
  UserCircleIcon,
  Cog6ToothIcon,
  BriefcaseIcon,
  BuildingOfficeIcon,
  ArrowRightOnRectangleIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  Bars3Icon,
  ShieldCheckIcon,
  MapPinIcon,
} from '@heroicons/react/24/outline'

interface NavSection {
  title: string
  items: NavItem[]
}

interface NavItem {
  label: string
  path: string
  icon: React.ComponentType<{ className?: string }>
  roles?: string[]
}

export default function Sidebar() {
  const roles = useRoles()

  const [isCollapsed, setIsCollapsed] = useState(false)
  const [isMobileOpen, setIsMobileOpen] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const dispatch = useAppDispatch()
  const { user } = useAppSelector((state) => state.auth)

  const handleLogout = () => {
    dispatch(logoutAction())
    navigate('/login')
  }

  // Get dashboard path based on user role
  const getDashboardPath = () => {
    if (!user) return '/'
    if (user.roles.includes(roles.admin) || user.roles.includes(roles.super_admin)) return '/admin'
    if (user.roles.includes(roles.interim)) return '/interimaire'
    if (user.roles.includes(roles.company)) return '/entreprise'
    if (user.roles.includes(roles.agency)) return '/agence'
    return '/profile'
  }

  if (!user) return null

  const isAdmin = user.roles.includes(roles.admin) || user.roles.includes(roles.super_admin)
  const isInterim = user.roles.includes(roles.interim)
  const isCompany = user.roles.includes(roles.company)
  const isCommercial = user.roles.includes(roles.commercial)

  // Navigation sections based on user role
  const navigationSections: NavSection[] = []

  if (isAdmin) {
    navigationSections.push(
      {
        title: 'Tableau de bord',
        items: [
          { label: 'Vue d\'ensemble', path: '/admin', icon: HomeIcon },
        ],
      },
      {
        title: 'Gestion',
        items: [
          { label: 'Utilisateurs', path: '/admin/users', icon: UserGroupIcon },
          { label: 'Groupes', path: '/admin/groups', icon: UserGroupIcon },
          { label: 'Localisations', path: '/admin/locations', icon: MapPinIcon },
          { label: 'Validations', path: '/admin/validations', icon: ClipboardDocumentCheckIcon },
        ],
      },
      {
        title: 'Processus',
        items: [
          { label: 'Missions', path: '/missions', icon: BriefcaseIcon },
        ],
      },
      {
        title: 'Paramètres',
        items: [
          { label: 'Référentiels', path: '/admin/references', icon: Cog6ToothIcon },
          { label: 'Règles Métier', path: '/admin/rules', icon: Cog6ToothIcon },
          { label: 'Profils & Permissions', path: '/admin/profiles', icon: ShieldCheckIcon },
        ],
      },
      {
        title: 'Compte',
        items: [
          { label: 'Mon Profil', path: '/profile', icon: UserCircleIcon },
          { label: 'Sécurité', path: '/security', icon: ShieldCheckIcon },
        ],
      }
    )
  } else if (isCommercial) {
    navigationSections.push(
      {
        title: 'Tableau de bord',
        items: [
          { label: 'Vue d\'ensemble', path: '/commercial', icon: HomeIcon },
        ],
      },
      {
        title: 'Gestion',
        items: [
          { label: 'Utilisateurs', path: '/admin/users', icon: UserGroupIcon },
          { label: 'Localisations', path: '/admin/locations', icon: MapPinIcon },
        ],
      },
      {
        title: 'Processus',
        items: [
          { label: 'Missions', path: '/missions', icon: BriefcaseIcon },
        ],
      },
      {
        title: 'Compte',
        items: [
          { label: 'Mon Profil', path: '/profile', icon: UserCircleIcon },
          { label: 'Sécurité', path: '/security', icon: ShieldCheckIcon },
        ],
      }
    )
  } else if (isInterim) {
    navigationSections.push(
      {
        title: 'Tableau de bord',
        items: [
          { label: 'Vue d\'ensemble', path: '/interimaire', icon: HomeIcon },
        ],
      },
      {
        title: 'Missions',
        items: [
          { label: 'Offres disponibles', path: '/offres', icon: BriefcaseIcon },
          { label: 'Mes Candidatures', path: '/mes-candidatures', icon: ClipboardDocumentCheckIcon },
        ],
      },
      {
        title: 'Compte',
        items: [
          { label: 'Mon Profil', path: '/profile', icon: UserCircleIcon },
          { label: 'Sécurité', path: '/security', icon: ShieldCheckIcon },
        ],
      }
    )
  } else if (isCompany) {
    navigationSections.push(
      {
        title: 'Tableau de bord',
        items: [
          { label: 'Vue d\'ensemble', path: '/entreprise', icon: HomeIcon },
        ],
      },
      {
        title: 'Processus',
        items: [
          { label: 'Mes Missions', path: '/missions', icon: BriefcaseIcon },
        ],
      },
      {
        title: 'Compte',
        items: [
          { label: 'Mon Profil', path: '/profile', icon: UserCircleIcon },
          { label: 'Sécurité', path: '/security', icon: ShieldCheckIcon },
        ],
      }
    )
  }

  const isActive = (path: string) => {
    return location.pathname === path
  }

  const SidebarContent = () => (
    <div className="flex flex-col h-full bg-gradient-to-b from-jlc-purple-800 to-jlc-purple-900 text-white">
      {/* Header */}
      <div className="p-4 border-b border-jlc-purple-700">
        <div className="flex items-center justify-between">
          <Link to={getDashboardPath()} className="flex items-center space-x-3 hover:opacity-80 transition">
            <img 
              src="/logo-jlc.png" 
              alt="JLC Group" 
              className={`${isCollapsed ? 'h-10 w-10' : 'h-12 w-auto'} object-contain transition-all`}
            />
            {!isCollapsed && (
              <div>
                <p className="text-xs text-jlc-purple-300 mt-1">
                  {isAdmin ? 'Administration' : isInterim ? 'Intérimaire' : 'Entreprise'}
                </p>
              </div>
            )}
          </Link>
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-2 rounded-lg hover:bg-jlc-purple-700 transition-colors hidden lg:block"
          >
            {isCollapsed ? (
              <ChevronRightIcon className="h-5 w-5" />
            ) : (
              <ChevronLeftIcon className="h-5 w-5" />
            )}
          </button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-4 space-y-6">
        {navigationSections.map((section, idx) => (
          <div key={idx}>
            {!isCollapsed && (
              <h3 className="text-xs font-semibold text-jlc-purple-300 uppercase tracking-wider mb-3">
                {section.title}
              </h3>
            )}
            <ul className="space-y-1">
              {section.items.map((item) => {
                const Icon = item.icon
                const active = isActive(item.path)

                return (
                  <li key={item.path}>
                    <Link
                      to={item.path}
                      onClick={() => setIsMobileOpen(false)}
                      className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
                        active
                          ? 'bg-jlc-purple-700 text-white shadow-lg'
                          : 'text-jlc-purple-200 hover:bg-jlc-purple-700/50 hover:text-white'
                      }`}
                      title={isCollapsed ? item.label : undefined}
                    >
                      <Icon className="h-5 w-5 flex-shrink-0" />
                      {!isCollapsed && (
                        <span className="text-sm font-medium">{item.label}</span>
                      )}
                    </Link>
                  </li>
                )
              })}
            </ul>
          </div>
        ))}
      </nav>

      {/* User Info & Logout */}
      <div className="p-4 border-t border-jlc-purple-700">
        <div className="flex items-center gap-3 mb-3">
          <div className="h-10 w-10 rounded-full bg-gradient-to-br from-jlc-accent-yellow to-yellow-500 flex items-center justify-center text-jlc-purple-900 font-bold flex-shrink-0">
            {user.full_name?.charAt(0) || user.username.charAt(0)}
          </div>
          {!isCollapsed && (
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user.full_name || user.username}</p>
              <p className="text-xs text-jlc-purple-300 truncate">{user.email}</p>
            </div>
          )}
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-jlc-purple-200 hover:bg-red-600/20 hover:text-red-300 transition-all"
          title={isCollapsed ? 'Déconnexion' : undefined}
        >
          <ArrowRightOnRectangleIcon className="h-5 w-5 flex-shrink-0" />
          {!isCollapsed && <span className="text-sm font-medium">Déconnexion</span>}
        </button>
      </div>
    </div>
  )

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={() => setIsMobileOpen(!isMobileOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-jlc-purple-600 text-white rounded-lg shadow-lg"
      >
        <Bars3Icon className="h-6 w-6" />
      </button>

      {/* Mobile Overlay */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Mobile Sidebar */}
      <aside
        className={`fixed top-0 left-0 h-full w-64 z-40 transform transition-transform duration-300 lg:hidden ${
          isMobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <SidebarContent />
      </aside>

      {/* Desktop Sidebar */}
      <aside
        className={`hidden lg:block fixed top-0 left-0 h-full transition-all duration-300 z-30 ${
          isCollapsed ? 'w-20' : 'w-64'
        }`}
      >
        <SidebarContent />
      </aside>
    </>
  )
}
