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
  USERS_READ: 'users.read',
  USERS_MANAGE: 'users.manage',
  
  // Email Settings
  EMAIL_SETTINGS_READ: 'email.settings.read',
  EMAIL_SETTINGS_MANAGE: 'email.settings.manage',
  
  // IAM
  IAM_PROFILES_READ: 'iam.profiles.read',
  IAM_PROFILES_MANAGE: 'iam.profiles.manage',
  IAM_GROUPS_READ: 'iam.groups.read',
  IAM_GROUPS_MANAGE: 'iam.groups.manage',
  IAM_PERMISSIONS_READ: 'iam.permissions.read',
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
