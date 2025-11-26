/**
 * IAM Constants
 * Centralized constants for roles, groups, and permissions
 * Keep in sync with backend: /auth-microservice/awana_auth/core/iam_constants.py
 */

// ============================================
// GROUPS
// ============================================
export const IAMGroups = {
  CANDIDAT: 'grp.candidat',
  POSTULANT: 'grp.postulant',
  INTERIMAIRE: 'grp.interimaire',
  COMPANY: 'grp.company',
  COLLABORATEUR: 'grp.collaborateur',
  ADMIN: 'grp.admin',
  SUPER_ADMIN: 'grp.super_admin',
} as const

// ============================================
// PROFILES / ROLES
// ============================================
export const IAMProfiles = {
  CANDIDAT: 'role.candidat',
  POSTULANT: 'role.postulant',
  INTERIM_USER: 'role.interim_user',
  COMPANY_ADMIN: 'role.company_admin',
  COLLABORATEUR: 'role.collaborateur',
  ADMIN: 'role.admin',
  SUPER_ADMIN: 'role.super_admin',
} as const

// ============================================
// PERMISSIONS
// ============================================
export const IAMPermissions = {
  // Missions
  MISSIONS_BROWSE: 'missions.browse',
  MISSIONS_READ: 'missions.read',
  MISSIONS_CREATE: 'missions.create',
  MISSIONS_UPDATE: 'missions.update',
  MISSIONS_DELETE: 'missions.delete',
  MISSIONS_MANAGE: 'missions.manage',
  
  // Applications
  APPLICATIONS_CREATE_OWN: 'applications.create_own',
  APPLICATIONS_READ_OWN: 'applications.read_own',
  APPLICATIONS_UPDATE_OWN: 'applications.update_own',
  APPLICATIONS_READ: 'applications.read',
  APPLICATIONS_MANAGE: 'applications.manage',
  
  // Profile
  PROFILE_MANAGE_OWN: 'profile.manage_own',
  PROFILE_READ: 'profile.read',
  PROFILE_MANAGE: 'profile.manage',
  
  // Auth & Security
  AUTH_MFA_MANAGE: 'auth.mfa.manage',
  SECURITY_EMAIL_DOMAINS_READ: 'security.email_domains.read',
  SECURITY_EMAIL_DOMAINS_MANAGE: 'security.email_domains.manage',
  
  // Admin
  ADMIN_DASHBOARD: 'admin.dashboard',
  USERS_EDIT: 'users.edit',
  USERS_EDIT_OWN: 'users.edit.own',
  USERS_EDIT_ALL: 'users.edit.all',
  USERS_READ: 'users.read',
  USERS_MANAGE: 'users.manage',
  USERS_PASSWORD_UPDATE: 'users.password.update',

  // Emails
  EMAILS_CONFIGURE: 'emails.configure',
  EMAILS_READ_CONFIG: 'emails.read_config',
  EMAILS_READ_HISTORY: 'emails.read_history',
  EMAILS_MANAGE_TEMPLATES: 'emails.manage_templates',
  EMAILS_TEST: 'emails.test',
  EMAIL_SETTINGS_READ: 'email.settings.read',
  EMAIL_SETTINGS_MANAGE: 'email.settings.manage',
  
  // IAM
  IAM_PROFILES_READ: 'iam.profiles.read',
  IAM_PROFILES_MANAGE: 'iam.profiles.manage',
  IAM_GROUPS_READ: 'iam.groups.read',
  IAM_GROUPS_MANAGE: 'iam.groups.manage',
  IAM_PERMISSIONS_READ: 'iam.permissions.read',

  // Besoins (Hiring Needs)
  BESOINS_CREATE: 'besoins.create',
  BESOINS_READ: 'besoins.read',
  BESOINS_EDIT: 'besoins.edit',
  BESOINS_DELETE: 'besoins.delete',
  BESOINS_SUBMIT: 'besoins.submit',
  BESOINS_VALIDATE: 'besoins.validate',
  BESOINS_CONVERT_TO_MISSION: 'besoins.convert_to_mission',
  BESOINS_COMMENT: 'besoins.comment',

  // Entreprises (Company Management)
  ENTREPRISES_CREATE: 'entreprises.create',
  ENTREPRISES_READ: 'entreprises.read',
  ENTREPRISES_EDIT: 'entreprises.edit',
  ENTREPRISES_DELETE: 'entreprises.delete',
  ENTREPRISES_VALIDATE: 'entreprises.validate',
  ENTREPRISES_LINK_EXISTING: 'entreprises.link_existing',
  ENTREPRISES_GROUP_REQUEST: 'entreprises.group_request',
  ENTREPRISES_GROUP_APPROVE: 'entreprises.group_approve',
  ENTREPRISES_VIEW_LINKED: 'entreprises.view_linked',

  // Forms & Configuration
  FORMS_MANAGE: 'forms.manage',
  CONFIG_READ: 'config.read',
  CONFIG_MANAGE: 'config.manage',

  // Documents (Phase 2)
  DOCUMENTS_READ_OWN: 'documents.read_own',
  DOCUMENTS_UPLOAD_OWN: 'documents.upload_own',
  DOCUMENTS_DELETE_OWN: 'documents.delete_own',
  DOCUMENTS_READ_ALL: 'documents.read_all',
  DOCUMENTS_VERIFY: 'documents.verify',
  DOCUMENTS_CONFIGURE: 'documents.configure',

  // Notifications (Phase 2)
  NOTIFICATIONS_READ_OWN: 'notifications.read_own',
  NOTIFICATIONS_MANAGE_OWN: 'notifications.manage_own',
  NOTIFICATIONS_SEND: 'notifications.send',

  // Dashboard (Phase 2)
  DASHBOARD_VIEW_OWN: 'dashboard.view_own',
  DASHBOARD_CUSTOMIZE: 'dashboard.customize',

  // Chat/Messages (Phase 3)
  MESSAGES_READ_OWN: 'messages.read_own',
  MESSAGES_SEND_OWN: 'messages.send_own',
  MESSAGES_READ_ALL: 'messages.read_all',
  MESSAGES_MANAGE: 'messages.manage',

  // Matching AI (Phase 3)
  MATCHING_VIEW_RECOMMENDATIONS: 'matching.view_recommendations',
  MATCHING_CONFIGURE: 'matching.configure',
} as const

// ============================================
// VALIDATION TYPES
// ============================================
export const ValidationTypes = {
  CANDIDAT: 'candidat',
  POSTULANT: 'postulant',
  INTERIM: 'interim',
  COMPANY: 'company',
  COLLABORATEUR: 'collaborateur',
} as const

// ============================================
// USER ROLES (Legacy - for backward compatibility)
// ============================================
export const UserRoles = {
  CANDIDAT: 'candidat',
  POSTULANT: 'postulant',
  INTERIM: 'interim',
  COMPANY: 'company',
  COLLABORATEUR: 'collaborateur',
  ADMIN: 'admin',
  SUPER_ADMIN: 'super_admin',
} as const

// ============================================
// ROLE LABELS (Human-readable)
// ============================================
export const RoleLabels: Record<string, string> = {
  [UserRoles.CANDIDAT]: 'Candidat',
  [UserRoles.POSTULANT]: 'Postulant',
  [UserRoles.INTERIM]: 'Intérimaire',
  [UserRoles.COMPANY]: 'Entreprise',
  [UserRoles.COLLABORATEUR]: 'Collaborateur',
  [UserRoles.ADMIN]: 'Administrateur',
  [UserRoles.SUPER_ADMIN]: 'Super Admin',
}

// ============================================
// ROLE COLORS (for badges)
// ============================================
export const RoleColors: Record<string, string> = {
  [UserRoles.ADMIN]: 'bg-purple-100 text-purple-800',
  [UserRoles.SUPER_ADMIN]: 'bg-red-100 text-red-800',
  [UserRoles.CANDIDAT]: 'bg-blue-100 text-blue-800',
  [UserRoles.POSTULANT]: 'bg-blue-50 text-blue-800',
  [UserRoles.INTERIM]: 'bg-teal-100 text-teal-800',
  [UserRoles.COMPANY]: 'bg-indigo-100 text-indigo-800',
  [UserRoles.COLLABORATEUR]: 'bg-green-100 text-green-800',
}

// ============================================
// HELPER FUNCTIONS
// ============================================
export function getGroupForRole(role: string): string {
  const roleToGroup: Record<string, string> = {
    [UserRoles.CANDIDAT]: IAMGroups.CANDIDAT,
    [UserRoles.POSTULANT]: IAMGroups.POSTULANT,
    [UserRoles.INTERIM]: IAMGroups.INTERIMAIRE,
    [UserRoles.COMPANY]: IAMGroups.COMPANY,
    [UserRoles.COLLABORATEUR]: IAMGroups.COLLABORATEUR,
    [UserRoles.ADMIN]: IAMGroups.ADMIN,
    [UserRoles.SUPER_ADMIN]: IAMGroups.SUPER_ADMIN,
  }
  return roleToGroup[role] || IAMGroups.CANDIDAT
}

export function getProfileForRole(role: string): string {
  const roleToProfile: Record<string, string> = {
    [UserRoles.CANDIDAT]: IAMProfiles.CANDIDAT,
    [UserRoles.POSTULANT]: IAMProfiles.POSTULANT,
    [UserRoles.INTERIM]: IAMProfiles.INTERIM_USER,
    [UserRoles.COMPANY]: IAMProfiles.COMPANY_ADMIN,
    [UserRoles.COLLABORATEUR]: IAMProfiles.COLLABORATEUR,
    [UserRoles.ADMIN]: IAMProfiles.ADMIN,
    [UserRoles.SUPER_ADMIN]: IAMProfiles.SUPER_ADMIN,
  }
  return roleToProfile[role] || IAMProfiles.CANDIDAT
}

export function getRoleLabel(role: string): string {
  return RoleLabels[role] || role
}

export function getRoleColor(role: string): string {
  return RoleColors[role] || 'bg-gray-100 text-gray-800'
}

// ============================================
// TYPE EXPORTS
// ============================================
export type IAMGroup = typeof IAMGroups[keyof typeof IAMGroups]
export type IAMProfile = typeof IAMProfiles[keyof typeof IAMProfiles]
export type IAMPermission = typeof IAMPermissions[keyof typeof IAMPermissions]
export type ValidationType = typeof ValidationTypes[keyof typeof ValidationTypes]
export type UserRole = typeof UserRoles[keyof typeof UserRoles]
