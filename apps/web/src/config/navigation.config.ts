/**
 * Configuration Centralisée de la Navigation
 * 
 * Cette configuration pilote :
 * - Le breadcrumb (fil d'Ariane)
 * - La sidebar (menu latéral)
 * - Les menus contextuels
 * 
 * Pattern IAM unifié : resource.action.scope
 * Labels via i18n : nav.{context}.{item}
 */

export type NavigationContext = 'entreprise' | 'commercial' | 'candidat' | 'admin' | 'public'

export interface NavigationItem {
  id: string
  path: string
  labelKey: string // Clé i18n
  icon?: string // Nom de l'icône (HeroIcons)
  parentId?: string | null
  requiredPermissions?: string[] // Permissions IAM (OR)
  requiredAllPermissions?: string[] // Permissions IAM (AND)
  contexts: NavigationContext[]
  children?: string[] // IDs des enfants
  order?: number // Ordre d'affichage
  hidden?: boolean // Masqué de la navigation
  external?: boolean // Lien externe
  badge?: string // Badge (ex: "new", "beta")
}

/**
 * Configuration complète de navigation
 * Organisée par contexte pour lisibilité
 */
export const navigationConfig: Record<string, NavigationItem> = {
  // ==================== CONTEXTE ENTREPRISE ====================
  
  entrepriseDashboard: {
    id: 'entrepriseDashboard',
    path: '/entreprise',
    labelKey: 'nav.entreprise.dashboard',
    icon: 'HomeIcon',
    parentId: null,
    requiredPermissions: ['dashboard.company.access', 'besoins.create.own'],
    contexts: ['entreprise'],
    children: ['entrepriseBesoins', 'entrepriseCandidatures'],
    order: 1,
  },
  
  entrepriseBesoins: {
    id: 'entrepriseBesoins',
    path: '/entreprise/besoins',
    labelKey: 'nav.entreprise.besoins',
    icon: 'ClipboardDocumentCheckIcon',
    parentId: 'entrepriseDashboard',
    requiredPermissions: ['besoins.view.own', 'besoins.read'],
    contexts: ['entreprise'],
    children: ['entrepriseBesoinsCreate'],
    order: 2,
  },
  
  entrepriseBesoinsCreate: {
    id: 'entrepriseBesoinsCreate',
    path: '/entreprise/besoins/create',
    labelKey: 'nav.entreprise.besoins.create',
    icon: 'PlusIcon',
    parentId: 'entrepriseBesoins',
    requiredPermissions: ['besoins.create.own'],
    contexts: ['entreprise'],
    order: 1,
  },
  
  entrepriseBesoinDetail: {
    id: 'entrepriseBesoinDetail',
    path: '/entreprise/besoins/:id',
    labelKey: 'nav.entreprise.besoins.detail',
    parentId: 'entrepriseBesoins',
    requiredPermissions: ['besoins.view.own', 'besoins.read'],
    contexts: ['entreprise'],
    hidden: true, // Pas dans la sidebar
  },
  
  entrepriseBesoinEdit: {
    id: 'entrepriseBesoinEdit',
    path: '/entreprise/besoins/:id/edit',
    labelKey: 'nav.entreprise.besoins.edit',
    parentId: 'entrepriseBesoinDetail',
    requiredPermissions: ['besoins.edit.own'],
    contexts: ['entreprise'],
    hidden: true,
  },
  
  entrepriseCandidatures: {
    id: 'entrepriseCandidatures',
    path: '/entreprise/candidatures',
    labelKey: 'nav.entreprise.candidatures',
    icon: 'UserGroupIcon',
    parentId: 'entrepriseDashboard',
    requiredPermissions: ['applications.view.own', 'applications.read'],
    contexts: ['entreprise'],
    order: 3,
  },
  
  // ==================== CONTEXTE COMMERCIAL ====================
  
  commercialDashboard: {
    id: 'commercialDashboard',
    path: '/commercial',
    labelKey: 'nav.commercial.dashboard',
    icon: 'HomeIcon',
    parentId: null,
    requiredPermissions: ['dashboard.commercial.access'],
    contexts: ['commercial'],
    children: ['commercialBesoins', 'commercialMissions'],
    order: 1,
  },
  
  commercialBesoins: {
    id: 'commercialBesoins',
    path: '/entreprise/besoins', // Même route que entreprise, contexte différent
    labelKey: 'nav.commercial.besoins', // "Demandes clientes"
    icon: 'ClipboardDocumentCheckIcon',
    parentId: 'commercialDashboard',
    requiredPermissions: ['besoins.view.all', 'besoins.read'],
    contexts: ['commercial'],
    order: 2,
  },
  
  commercialMissions: {
    id: 'commercialMissions',
    path: '/missions',
    labelKey: 'nav.commercial.missions', // "Missions"
    icon: 'BriefcaseIcon',
    parentId: 'commercialDashboard',
    requiredPermissions: ['missions.read', 'missions.browse'],
    contexts: ['commercial'],
    order: 3,
  },
  
  // ==================== CONTEXTE CANDIDAT ====================
  
  candidatDashboard: {
    id: 'candidatDashboard',
    path: '/candidat',
    labelKey: 'nav.candidat.dashboard',
    icon: 'HomeIcon',
    parentId: null,
    requiredPermissions: ['dashboard.candidat.access'],
    contexts: ['candidat'],
    children: ['candidatOffres', 'candidatCandidatures'],
    order: 1,
  },
  
  candidatOffres: {
    id: 'candidatOffres',
    path: '/offres',
    labelKey: 'nav.candidat.offres',
    icon: 'BriefcaseIcon',
    parentId: 'candidatDashboard',
    requiredPermissions: ['missions.browse'],
    contexts: ['candidat'],
    order: 2,
  },
  
  candidatCandidatures: {
    id: 'candidatCandidatures',
    path: '/mes-candidatures',
    labelKey: 'nav.candidat.candidatures',
    icon: 'ClipboardDocumentCheckIcon',
    parentId: 'candidatDashboard',
    requiredPermissions: ['applications.read.own'],
    contexts: ['candidat'],
    order: 3,
  },
  
  // ==================== CONTEXTE ADMIN ====================
  
  adminDashboard: {
    id: 'adminDashboard',
    path: '/admin',
    labelKey: 'nav.admin.dashboard',
    icon: 'HomeIcon',
    parentId: null,
    requiredPermissions: ['admin.dashboard', 'admin.access'],
    contexts: ['admin'],
    children: ['adminGestion', 'adminIAM', 'adminConfig'],
    order: 1,
  },
  
  // --- Gestion ---
  adminGestion: {
    id: 'adminGestion',
    path: '#', // Groupe, pas une vraie route
    labelKey: 'nav.admin.gestion',
    icon: 'Cog6ToothIcon',
    parentId: 'adminDashboard',
    contexts: ['admin'],
    children: ['adminUsers', 'adminValidations', 'adminEntreprises', 'adminLocations'],
    order: 2,
  },
  
  adminUsers: {
    id: 'adminUsers',
    path: '/admin/users',
    labelKey: 'nav.admin.users',
    icon: 'UserGroupIcon',
    parentId: 'adminGestion',
    requiredPermissions: ['users.read', 'users.manage'],
    contexts: ['admin'],
    order: 1,
  },
  
  adminValidations: {
    id: 'adminValidations',
    path: '/admin/validations',
    labelKey: 'nav.admin.validations',
    icon: 'ClipboardDocumentCheckIcon',
    parentId: 'adminGestion',
    requiredPermissions: ['validations.manage', 'admin.access'],
    contexts: ['admin'],
    order: 2,
  },
  
  adminEntreprises: {
    id: 'adminEntreprises',
    path: '/admin/entreprises',
    labelKey: 'nav.admin.entreprises',
    icon: 'BuildingOfficeIcon',
    parentId: 'adminGestion',
    requiredPermissions: ['entreprises.read', 'entreprises.manage'],
    contexts: ['admin'],
    order: 3,
  },
  
  adminLocations: {
    id: 'adminLocations',
    path: '/admin/locations',
    labelKey: 'nav.admin.locations',
    icon: 'MapPinIcon',
    parentId: 'adminGestion',
    requiredPermissions: ['locations.manage'],
    contexts: ['admin'],
    order: 4,
  },
  
  // --- IAM & Sécurité ---
  adminIAM: {
    id: 'adminIAM',
    path: '#',
    labelKey: 'nav.admin.iam',
    icon: 'ShieldCheckIcon',
    parentId: 'adminDashboard',
    contexts: ['admin'],
    children: ['adminIAMProfiles', 'adminIAMGroups', 'adminIAMControl', 'adminRetention'],
    order: 3,
  },
  
  adminIAMProfiles: {
    id: 'adminIAMProfiles',
    path: '/admin/iam/profiles',
    labelKey: 'nav.admin.iam.profiles',
    icon: 'ShieldCheckIcon',
    parentId: 'adminIAM',
    requiredPermissions: ['iam.profiles.manage'],
    contexts: ['admin'],
    order: 1,
  },
  
  adminIAMGroups: {
    id: 'adminIAMGroups',
    path: '/admin/iam/groups',
    labelKey: 'nav.admin.iam.groups',
    icon: 'UsersIcon',
    parentId: 'adminIAM',
    requiredPermissions: ['iam.groups.manage'],
    contexts: ['admin'],
    order: 2,
  },
  
  adminIAMControl: {
    id: 'adminIAMControl',
    path: '/admin/iam/control',
    labelKey: 'nav.admin.iam.control',
    icon: 'ShieldCheckIcon',
    parentId: 'adminIAM',
    requiredPermissions: ['iam.groups.manage'],
    contexts: ['admin'],
    order: 3,
  },
  
  adminRetention: {
    id: 'adminRetention',
    path: '/admin/retention-config',
    labelKey: 'nav.admin.retention',
    icon: 'ClockIcon',
    parentId: 'adminIAM',
    requiredPermissions: ['users.manage'],
    contexts: ['admin'],
    order: 4,
  },
  
  // --- Configuration ---
  adminConfig: {
    id: 'adminConfig',
    path: '#',
    labelKey: 'nav.admin.config',
    icon: 'Cog6ToothIcon',
    parentId: 'adminDashboard',
    contexts: ['admin'],
    children: ['adminReferences', 'adminCountries', 'adminRules', 'adminFlags', 'adminEmails'],
    order: 4,
  },
  
  adminReferences: {
    id: 'adminReferences',
    path: '/admin/references',
    labelKey: 'nav.admin.references',
    icon: 'Cog6ToothIcon',
    parentId: 'adminConfig',
    requiredPermissions: ['references.manage'],
    contexts: ['admin'],
    order: 1,
  },
  
  adminCountries: {
    id: 'adminCountries',
    path: '/admin/countries',
    labelKey: 'nav.admin.countries',
    icon: 'GlobeAltIcon',
    parentId: 'adminConfig',
    requiredPermissions: ['admin.settings'],
    contexts: ['admin'],
    order: 2,
  },
  
  adminRules: {
    id: 'adminRules',
    path: '/admin/rules',
    labelKey: 'nav.admin.rules',
    icon: 'Cog6ToothIcon',
    parentId: 'adminConfig',
    requiredPermissions: ['rules.manage'],
    contexts: ['admin'],
    order: 3,
  },
  
  adminFlags: {
    id: 'adminFlags',
    path: '/admin/feature-flags',
    labelKey: 'nav.admin.flags',
    icon: 'FlagIcon',
    parentId: 'adminConfig',
    requiredPermissions: ['flags.manage', 'admin.access'],
    contexts: ['admin'],
    order: 4,
  },
  
  adminEmails: {
    id: 'adminEmails',
    path: '/admin/email-settings',
    labelKey: 'nav.admin.emails',
    icon: 'EnvelopeIcon',
    parentId: 'adminConfig',
    requiredPermissions: ['emails.configure', 'admin.access'],
    contexts: ['admin'],
    order: 5,
  },
  
  // ==================== MISSIONS (Multi-contexte) ====================
  
  missions: {
    id: 'missions',
    path: '/missions',
    labelKey: 'nav.missions.list',
    icon: 'BriefcaseIcon',
    parentId: null,
    requiredPermissions: ['missions.read', 'missions.browse'],
    contexts: ['admin', 'commercial', 'candidat'],
    children: ['missionDetail'],
    order: 10,
  },
  
  missionDetail: {
    id: 'missionDetail',
    path: '/missions/:id',
    labelKey: 'nav.missions.detail',
    parentId: 'missions',
    requiredPermissions: ['missions.read'],
    contexts: ['admin', 'commercial', 'candidat', 'entreprise'],
    hidden: true,
  },
  
  missionEdit: {
    id: 'missionEdit',
    path: '/missions/:id/edit',
    labelKey: 'nav.missions.edit',
    parentId: 'missionDetail',
    requiredPermissions: ['missions.edit.all', 'missions.edit.own'],
    contexts: ['admin', 'commercial'],
    hidden: true,
  },
  
  missionCandidatures: {
    id: 'missionCandidatures',
    path: '/missions/:id/candidatures',
    labelKey: 'nav.missions.candidatures',
    parentId: 'missionDetail',
    requiredPermissions: ['applications.manage'],
    contexts: ['admin', 'commercial'],
    hidden: true,
  },
  
  // ==================== PROFIL & COMPTE ====================
  
  profile: {
    id: 'profile',
    path: '/profile',
    labelKey: 'nav.profile',
    icon: 'UserCircleIcon',
    parentId: null,
    requiredPermissions: ['profile.read.own'],
    contexts: ['entreprise', 'commercial', 'candidat', 'admin'],
    order: 100,
  },
  
  security: {
    id: 'security',
    path: '/security',
    labelKey: 'nav.security',
    icon: 'ShieldCheckIcon',
    parentId: null,
    contexts: ['entreprise', 'commercial', 'candidat', 'admin'],
    order: 101,
  },
  
  documents: {
    id: 'documents',
    path: '/documents',
    labelKey: 'nav.documents',
    icon: 'DocumentTextIcon',
    parentId: null,
    requiredPermissions: ['documents.read.own'],
    contexts: ['entreprise', 'commercial', 'candidat', 'admin'],
    order: 102,
  },
}

/**
 * Utilitaires pour navigation
 */

// Trouver un item par path (gère les paramètres dynamiques)
export function findNavigationItemByPath(path: string): NavigationItem | undefined {
  const items = Object.values(navigationConfig)
  
  // Correspondance exacte d'abord
  const exactMatch = items.find(item => item.path === path)
  if (exactMatch) return exactMatch
  
  // Correspondance avec paramètres (:id, etc.)
  return items.find(item => {
    if (!item.path.includes(':')) return false
    
    const pattern = item.path.replace(/:[^/]+/g, '[^/]+')
    const regex = new RegExp(`^${pattern}$`)
    return regex.test(path)
  })
}

// Construire le chemin du breadcrumb
export function buildBreadcrumbPath(itemId: string): NavigationItem[] {
  const path: NavigationItem[] = []
  let currentItem = navigationConfig[itemId]
  
  while (currentItem) {
    path.unshift(currentItem)
    if (!currentItem.parentId) break
    currentItem = navigationConfig[currentItem.parentId]
  }
  
  return path
}

// Filtrer les items par contexte et permissions
export function filterNavigationItems(
  context: NavigationContext,
  userPermissions: string[]
): NavigationItem[] {
  return Object.values(navigationConfig).filter(item => {
    // Vérifier le contexte
    if (!item.contexts.includes(context)) return false
    
    // Vérifier les permissions si requises
    if (item.requiredPermissions && item.requiredPermissions.length > 0) {
      // OR: l'utilisateur doit avoir AU MOINS une des permissions
      const hasPermission = item.requiredPermissions.some(perm => 
        userPermissions.includes(perm)
      )
      if (!hasPermission) return false
    }
    
    if (item.requiredAllPermissions && item.requiredAllPermissions.length > 0) {
      // AND: l'utilisateur doit avoir TOUTES les permissions
      const hasAllPermissions = item.requiredAllPermissions.every(perm =>
        userPermissions.includes(perm)
      )
      if (!hasAllPermissions) return false
    }
    
    return true
  })
}

// Construire l'arbre de navigation
export function buildNavigationTree(
  items: NavigationItem[]
): NavigationItem[] {
  const itemsMap = new Map(items.map(item => [item.id, { ...item, children: [] }]))
  const roots: NavigationItem[] = []
  
  items.forEach(item => {
    const node = itemsMap.get(item.id)!
    if (!item.parentId || !itemsMap.has(item.parentId)) {
      roots.push(node)
    } else {
      const parent = itemsMap.get(item.parentId)!
      if (!parent.children) parent.children = []
      parent.children.push(node.id)
    }
  })
  
  // Trier par order
  const sortByOrder = (a: NavigationItem, b: NavigationItem) => 
    (a.order || 999) - (b.order || 999)
  
  roots.sort(sortByOrder)
  
  return roots
}
