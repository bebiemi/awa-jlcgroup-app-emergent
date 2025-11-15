import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAppSelector, useAppDispatch } from '@/store/hooks'
import { logoutAction } from '@/features/auth/slices/authSlice'
import { useRoles } from '@/hooks/useAppConfig'
import { useTranslation } from 'react-i18next'
import LanguageSwitcher from './LanguageSwitcher'
import UserStatusDropdown from './UserStatusDropdown'
import { usePermissions } from '@/hooks/usePermission'
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
  ClockIcon,
  FlagIcon,
  EnvelopeIcon,
  InboxIcon,
  DocumentTextIcon,
  GlobeAltIcon,
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
  const { t } = useTranslation()
  const roles = useRoles()

  const [isCollapsed, setIsCollapsed] = useState(false)
  const [isMobileOpen, setIsMobileOpen] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const dispatch = useAppDispatch()
  const { user } = useAppSelector((state) => state.auth)

  const handleLogout = async () => {
    try {
      // 1. FIRST: Set user status to "offline" in backend
      await fetch('/api/users/presence/me', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ status: 'offline' })
      }).catch(() => {}) // Silent fail if network error
      
      // 2. Clear all API caches to prevent stale data
      dispatch({ type: 'presenceApi/resetApiState' })
      dispatch({ type: 'api/resetApiState' })
      
      // 3. Logout and clear localStorage
      dispatch(logoutAction())
      
      // 4. Redirect to homepage
      navigate('/', { replace: true })
    } catch (error) {
      console.error('Logout error:', error)
      // Logout anyway even if status update fails
      dispatch({ type: 'presenceApi/resetApiState' })
      dispatch({ type: 'api/resetApiState' })
      dispatch(logoutAction())
      navigate('/', { replace: true })
    }
  }

  // Get dashboard path based on user role
  const getDashboardPath = () => {
    if (!user) return '/'
    if (user.roles.includes(roles.admin) || user.roles.includes(roles.super_admin)) return '/admin'
    if (user.roles.includes(roles.interim)) return '/interimaire'
    if (user.roles.includes(roles.company)) return '/entreprise'
    if (user.roles.includes(roles.agency)) return '/agence'
    if (user.roles.includes('postulant')) return '/postulant'
    return '/profile'
  }

  if (!user) return null

  // IAM: Check permissions instead of roles
  const { permissions: userPermissions } = usePermissions([
    'admin.dashboard',
    'users.read',
    'groups.manage',
    'locations.manage',
    'validations.manage',
    'missions.manage',
    'missions.browse',
    'missions.create',
    'applications.read_own',
    'iam.profiles.manage',
    'iam.groups.manage',
    'profiles.manage',
    'references.manage',
    'rules.manage',
    'flags.manage',
    'config.manage',
    'emails.configure',
    'emails.read_history',
    'emails.manage_templates',
    'profile.manage_own',
  ])

  // Navigation sections based on user permissions (IAM)
  const navigationSections: NavSection[] = []

  if (userPermissions['admin.dashboard']) {
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
          { label: 'Localisations', path: '/admin/locations', icon: MapPinIcon },
          { label: 'Validations', path: '/admin/validations', icon: ClipboardDocumentCheckIcon },
          { label: 'Entreprises', path: '/admin/entreprises', icon: BuildingOfficeIcon },
        ],
      },
      {
        title: 'Processus',
        items: [
          { label: 'Missions', path: '/missions', icon: BriefcaseIcon },
        ],
      },
      {
        title: 'IAM & Sécurité',
        items: [
          { label: 'Gestion des Profils', path: '/admin/iam/profiles', icon: ShieldCheckIcon },
          { label: 'Contrôle d\'Accès (Groupes)', path: '/admin/iam/control', icon: ShieldCheckIcon },
          { label: 'Rétention des Données', path: '/admin/retention-config', icon: ClockIcon },
          { label: 'Domaines Email', path: '/admin/security/email-domains', icon: GlobeAltIcon },
        ],
      },
      {
        title: 'Paramètres',
        items: [
          { label: 'Pays et Devises', path: '/admin/countries', icon: GlobeAltIcon },
          { label: 'Référentiels', path: '/admin/references', icon: Cog6ToothIcon },
          { label: 'Règles Métier', path: '/admin/rules', icon: Cog6ToothIcon },
          { label: 'Feature Flags', path: '/admin/feature-flags', icon: FlagIcon },
          { label: 'Versions Config', path: '/admin/versions', icon: ClockIcon },
          { label: 'Configuration Email', path: '/admin/email-settings', icon: EnvelopeIcon },
        ],
      },
      {
        title: 'Notifications',
        items: [
          { label: 'Historique Emails', path: '/admin/email-history', icon: InboxIcon },
          { label: 'Templates Email', path: '/admin/email-templates', icon: DocumentTextIcon },
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
  } else if (userPermissions['missions.manage'] && !userPermissions['admin.dashboard']) {
    // Commercial role (has missions.manage but not full admin)
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
          { label: 'Validations', path: '/admin/validations', icon: ClipboardDocumentCheckIcon },
          { label: 'Entreprises', path: '/admin/entreprises', icon: BuildingOfficeIcon },
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
  } else if (userPermissions['missions.browse']) {
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
  } else if (userPermissions['missions.create']) {
    // Company role (can create missions)
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
          { label: 'Mes Besoins', path: '/entreprise/besoins', icon: DocumentTextIcon },
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
  } else if (user?.roles?.includes('postulant')) {
    // Postulant role (applicant in onboarding process)
    navigationSections.push(
      {
        title: 'Tableau de bord',
        items: [
          { label: 'Mon parcours', path: '/postulant', icon: HomeIcon },
        ],
      },
      {
        title: 'Mon profil',
        items: [
          { label: 'Compléter mon profil', path: '/profile', icon: UserCircleIcon },
          { label: 'Mes documents', path: '/profile?tab=documents', icon: DocumentTextIcon },
        ],
      },
      {
        title: 'Compte',
        items: [
          { label: 'Sécurité', path: '/security', icon: ShieldCheckIcon },
        ],
      }
    )
  }

  const isActive = (path: string) => {
    return location.pathname === path
  }

  const SidebarContent = () => (
    <div className="flex flex-col h-full bg-gradient-to-b from-jlc-indigo-dark to-jlc-neon-pink-gray text-white">
      {/* Header */}
      <div className="p-4 border-b border-jlc-neon-pink/30">
        <div className="flex items-center justify-between">
          <Link to={getDashboardPath()} className="flex items-center space-x-3 hover:opacity-80 transition">
            <img 
              src="/logo-jlc.png" 
              alt="JLC Group" 
              className={`${isCollapsed ? 'h-10 w-auto' : 'h-14 w-auto max-w-[180px]'} object-contain transition-all`}
            />
            {!isCollapsed && (
              <div>
                <p className="text-xs text-white/70 mt-1">
                  {userPermissions['admin.dashboard'] ? 'Administration' : 
                   userPermissions['missions.browse'] ? 'Intérimaire' : 
                   userPermissions['missions.create'] ? 'Entreprise' : 
                   'Utilisateur'}
                </p>
              </div>
            )}
          </Link>
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-2 rounded-lg hover:bg-jlc-magenta/30 transition-colors hidden lg:block"
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
              <h3 className="text-xs font-semibold text-white/60 uppercase tracking-wider mb-3">
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
                          ? 'bg-jlc-magenta text-white shadow-lg'
                          : 'text-white/80 hover:bg-jlc-magenta/50 hover:text-white'
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

      {/* Language Switcher & User Info */}
      <div className="p-4 border-t border-jlc-purple-700">
        {/* Language Switcher */}
        {!isCollapsed && (
          <div className="mb-3">
            <LanguageSwitcher />
          </div>
        )}
        
        {/* User Info with Status Dropdown */}
        <div className="mb-3">
          <UserStatusDropdown 
            userName={user.full_name || user.username}
            userEmail={user.email}
            compact={isCollapsed}
          />
        </div>
        
        {/* Logout Button */}
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-white/80 hover:bg-red-600/20 hover:text-red-300 transition-all"
          title={isCollapsed ? t('common.logout') : undefined}
        >
          <ArrowRightOnRectangleIcon className="h-5 w-5 flex-shrink-0" />
          {!isCollapsed && <span className="text-sm font-medium">{t('common.logout')}</span>}
        </button>
      </div>
    </div>
  )

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={() => setIsMobileOpen(!isMobileOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-jlc-magenta text-white rounded-lg shadow-lg"
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
