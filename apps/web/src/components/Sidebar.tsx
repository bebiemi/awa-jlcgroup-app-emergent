import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAppSelector, useAppDispatch } from '@/store/hooks'
import { useSidebar } from '@/contexts/SidebarContext'
import { logoutAction } from '@/features/auth/slices/authSlice'
import { useRoles } from '@/hooks/useAppConfig'
import { useTranslation } from 'react-i18next'
import LanguageSwitcher from './LanguageSwitcher'
import UserStatusDropdown from './UserStatusDropdown'
import { usePermissions } from '@/hooks/usePermission'
import { useCandidateTrackingAccess } from '@/hooks/useCandidateTracking'
import {
  HomeIcon,
  UserGroupIcon,
  UsersIcon,
  ClipboardDocumentCheckIcon,
  UserCircleIcon,
  Cog6ToothIcon,
  BriefcaseIcon,
  BuildingOfficeIcon,
  ArrowRightOnRectangleIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ChevronDownIcon,
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

  const { isCollapsed, setIsCollapsed } = useSidebar()
  const [isMobileOpen, setIsMobileOpen] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const dispatch = useAppDispatch()
  const { user } = useAppSelector((state) => state.auth)
  const [expandedSections, setExpandedSections] = useState<string[]>(() => {
    // Load from localStorage or default to all expanded
    const saved = localStorage.getItem('expandedSections')
    return saved ? JSON.parse(saved) : []
  })

  // Hook pour vérifier l'accès au suivi des candidatures (IAM + présence de candidatures)
  const showCandidatureTracking = useCandidateTrackingAccess()

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

  const toggleSection = (sectionTitle: string) => {
    const newExpanded = expandedSections.includes(sectionTitle)
      ? expandedSections.filter((s) => s !== sectionTitle)
      : [...expandedSections, sectionTitle]
    
    setExpandedSections(newExpanded)
    localStorage.setItem('expandedSections', JSON.stringify(newExpanded))
  }

  const isSectionExpanded = (sectionTitle: string) => {
    return expandedSections.includes(sectionTitle)
  }

  if (!user) return null

  // IAM: Check permissions instead of roles
  const { permissions: userPermissions } = usePermissions([
    'admin.dashboard',
    'admin.access',
    'users.read',
    'users.manage',
    'groups.manage',
    'locations.manage',
    'validations.manage',
    'missions.manage.all',
    'missions.browse',
    'missions.read',
    'missions.create.all',
    'missions.create.own',
    'besoins.create.all',
    'besoins.create.own',
    'besoins.read',
    'besoins.view.all',
    'besoins.view.own',
    'applications.read.all',
    'applications.read.own',
    'iam.profiles.manage',
    'iam.groups.manage',
    'profiles.manage',
    'references.manage',
    'rules.manage',
    'flags.manage',
    'config.manage',
    'config.read',
    'forms.read',
    'forms.manage',
    'emails.configure',
    'emails.read_history',
    'emails.manage_templates',
    'profile.manage.own',
    'profile.view.own',
    'profile.edit.own',
    'rbac.assign_profiles',
    'rbac.assign_groups',
    'forms.enterprise.manage',
    'entreprises.manage',
    'entreprises.read',
    'dashboard.access',
    'dashboard.candidat.access',
  ])

  // Get dashboard path based on user permissions (IAM)
  const getDashboardPath = () => {
    if (!user) return '/'
    if (userPermissions['admin.dashboard']) return '/admin'
    if (userPermissions['dashboard.commercial.access']) return '/commercial'
    if (userPermissions['dashboard.company.access']) return '/entreprise'
    if (userPermissions['dashboard.candidat.access']) return '/candidat'
    // Fallback pour anciens profils
    if (user.roles.includes(roles.admin) || user.roles.includes(roles.super_admin)) return '/admin'
    if (user.roles.includes(roles.interim)) return '/interimaire'
    if (user.roles.includes(roles.company)) return '/entreprise'
    if (user.roles.includes(roles.agency)) return '/agence'
    if (user.roles.includes('postulant') || user.roles.includes('candidat')) return '/postulant'
    return '/profile'
  }

  // Navigation sections based on user permissions (IAM)
  const navigationSections: NavSection[] = []

  if (userPermissions['admin.dashboard']) {
    navigationSections.push(
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
          { label: 'Gestion des Groupes', path: '/admin/iam/groups', icon: UsersIcon },
          { label: 'Contrôle d\'Accès (Groupes)', path: '/admin/iam/control', icon: ShieldCheckIcon },
          // Note: "Rôles IAM" a été fusionné avec "Gestion des Groupes" dans la nouvelle architecture
          // { label: 'Rôles IAM (Hybride)', path: '/admin/iam/roles', icon: ShieldCheckIcon },
          { label: 'Rétention des Données', path: '/admin/retention-config', icon: ClockIcon },
          { label: 'Domaines Email', path: '/admin/security/email-domains', icon: GlobeAltIcon },
        ],
      },
      {
        title: 'Configuration',
        items: [
          { label: 'Formulaire Entreprise', path: '/admin/config/entreprises', icon: BuildingOfficeIcon },
          { label: 'Pays et Devises', path: '/admin/countries', icon: GlobeAltIcon },
          { label: 'Référentiels', path: '/admin/references', icon: Cog6ToothIcon },
          { label: 'Règles Métier', path: '/admin/rules', icon: Cog6ToothIcon },
          { label: 'Feature Flags', path: '/admin/feature-flags', icon: FlagIcon },
          { label: 'Versions Config', path: '/admin/versions', icon: ClockIcon },
          { label: 'Configuration Email', path: '/admin/email-settings', icon: EnvelopeIcon },
        ],
      },
      {
        title: 'Support',
        items: [
          { label: 'Mes Tickets', path: '/support/tickets', icon: InboxIcon },
        ],
      },
      {
        title: 'Documents',
        items: [
          { label: 'Mes Documents', path: '/documents', icon: DocumentTextIcon },
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
  } else if (userPermissions['dashboard.commercial.access'] || 
             (userPermissions['missions.manage.all'] && !userPermissions['admin.dashboard']) ||
             user.roles?.includes('commercial')) {
    // Commercial role (IAM-based + fallback roles)
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
          ...(userPermissions['besoins.read'] || userPermissions['besoins.view.all'] 
            ? [{ label: 'Demandes clientes', path: '/entreprise/besoins', icon: ClipboardDocumentCheckIcon }]
            : []),
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
  } else if (userPermissions['dashboard.candidat.access'] || 
             (userPermissions['applications.read.own'] && userPermissions['missions.browse'])) {
    // Candidat role - IAM-based (anciennement postulant/intérimaire)
    
    // Construire dynamiquement les items de la section Missions
    const missionsItems = [
      { label: 'Offres disponibles', path: '/offres', icon: BriefcaseIcon },
    ]
    
    // Ajouter "Mes Candidatures" seulement si l'utilisateur a des candidatures ET les permissions
    if (showCandidatureTracking) {
      missionsItems.push({ 
        label: 'Mes Candidatures', 
        path: '/mes-candidatures', 
        icon: ClipboardDocumentCheckIcon 
      })
    }
    
    navigationSections.push(
      {
        title: 'Tableau de bord',
        items: [
          { label: 'Vue d\'ensemble', path: '/candidat', icon: HomeIcon },
        ],
      },
      {
        title: 'Missions',
        items: missionsItems,
      },
      {
        title: 'Mon profil',
        items: [
          { label: 'Mon Profil', path: '/profile', icon: UserCircleIcon },
          { label: 'Mes documents', path: '/documents', icon: DocumentTextIcon },
        ],
      },
      {
        title: 'Support',
        items: [
          { label: 'Mes Tickets', path: '/support/tickets', icon: InboxIcon },
        ],
      },
      {
        title: 'Compte',
        items: [
          { label: 'Sécurité', path: '/security', icon: ShieldCheckIcon },
        ],
      }
    )
  } else if (userPermissions['besoins.create.own'] || userPermissions['besoins.create.all'] || 
             userPermissions['missions.create.own'] || userPermissions['missions.create.all']) {
    // Company role (can create missions/besoins with .own or .all scope)
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
          { label: 'Suivi Candidatures', path: '/entreprise/candidatures', icon: UserGroupIcon },
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
  } else if (userPermissions['rbac.assign_profiles'] || userPermissions['rbac.assign_groups']) {
    // Users avec permissions de gestion d'équipe
    navigationSections.push(
      {
        title: 'Mon Équipe',
        items: [
          { label: 'Gérer mon équipe', path: '/settings/my-team', icon: UserGroupIcon },
        ],
      },
      {
        title: 'Mon profil',
        items: [
          { label: 'Mon Profil', path: '/profile', icon: UserCircleIcon },
          { label: 'Mes documents', path: '/documents', icon: DocumentTextIcon },
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
    <div className="flex flex-col h-full bg-gradient-to-b from-jlc-neon-pink-gray to-jlc-indigo-dark text-white">
      {/* Header */}
      <div className="p-4 border-b border-jlc-neon-pink/30">
        <div className="flex items-center justify-between gap-2">
          <Link to={getDashboardPath()} className="flex items-center space-x-3 hover:opacity-80 transition flex-1 min-w-0">
            <img 
              src="/logo-jlc.png" 
              alt="JLC Group" 
              className={`${isCollapsed ? 'h-10 w-auto' : 'h-14 w-auto max-w-[180px]'} object-contain transition-all flex-shrink-0`}
            />
            {!isCollapsed && (
              <div className="min-w-0">
                <h2 className="font-bold text-xl text-jlc-neon-pink truncate">JLC Group</h2>
                <p className="text-xs text-white/60 truncate">
                  {user?.roles.includes(roles.admin) ? 'Administration' : 
                   user?.roles.includes(roles.interim) || user?.roles.includes('intérimaire') ? 'Intérimaire' : 
                   user?.roles.includes(roles.company) || user?.roles.includes('entreprise') ? 'Entreprise' :
                   user?.roles.includes('candidat') || user?.roles.includes('postulant') ? 'Candidat' :
                   'Utilisateur'}
                </p>
              </div>
            )}
          </Link>
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-2 rounded-lg hover:bg-jlc-magenta/30 transition-colors hidden lg:block flex-shrink-0"
            title={isCollapsed ? 'Étendre le menu' : 'Réduire le menu'}
          >
            {isCollapsed ? (
              <ChevronRightIcon className="h-5 w-5 text-white" />
            ) : (
              <ChevronLeftIcon className="h-5 w-5 text-white" />
            )}
          </button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* Vue d'ensemble - Always visible, not collapsible */}
        {userPermissions['admin.dashboard'] && (
          <Link
            to="/admin"
            className={`flex items-center ${
              isCollapsed ? 'justify-center' : 'justify-start'
            } px-3 py-2.5 rounded-lg transition-all ${
              isActive('/admin')
                ? 'bg-jlc-magenta text-white'
                : 'text-white/80 hover:bg-jlc-magenta/30 hover:text-white'
            }`}
          >
            <HomeIcon className={`h-5 w-5 ${isCollapsed ? '' : 'mr-3'} flex-shrink-0`} />
            {!isCollapsed && <span className="font-medium">Vue d'ensemble</span>}
          </Link>
        )}

        {navigationSections.map((section, idx) => {
          const sectionExpanded = isSectionExpanded(section.title)
          
          return (
            <div key={idx}>
              {!isCollapsed && (
                <button
                  onClick={() => toggleSection(section.title)}
                  className="w-full flex items-center justify-between text-xs font-semibold text-white/60 uppercase tracking-wider mb-3 hover:text-white/80 transition-colors"
                >
                  <span>{section.title}</span>
                  {sectionExpanded ? (
                    <ChevronDownIcon className="h-4 w-4" />
                  ) : (
                    <ChevronRightIcon className="h-4 w-4" />
                  )}
                </button>
              )}
              {(isCollapsed || sectionExpanded) && (
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
              )}
            </div>
          )
        })}
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
