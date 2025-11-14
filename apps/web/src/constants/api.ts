/**
 * API Constants
 * Centralized API endpoint configuration
 * 
 * IMPORTANT: Ces chemins sont RELATIFS et seront préfixés par /api automatiquement
 * par createBaseQueryWithAuth(). Ne PAS inclure /api dans ces constantes.
 */

// Base paths (SANS /api - sera ajouté par baseQuery)
export const API_BASE = {
  AUTH: 'auth',
  IAM: 'iam',
  USERS: 'users',
  ADMIN: 'admin',
  SECURITY: 'security',
} as const

// IAM API Endpoints (chemins relatifs sans /api)
export const IAM_ENDPOINTS = {
  USERS: {
    LIST: `${API_BASE.IAM}/users`,
    DETAIL: (id: string) => `${API_BASE.IAM}/users/${id}`,
    CREATE: `${API_BASE.IAM}/users`,
    UPDATE: (id: string) => `${API_BASE.IAM}/users/${id}`,
    DELETE: (id: string) => `${API_BASE.IAM}/users/${id}`,
    STATUS: (id: string) => `${API_BASE.IAM}/users/${id}/status`,
    DOCUMENTS: (id: string) => `${API_BASE.IAM}/users/${id}/documents`,
    DOCUMENT_VERIFY: (id: string, docId: string) => 
      `${API_BASE.IAM}/users/${id}/documents/${docId}/verify`,
    DOCUMENT_DELETE: (id: string, docId: string) => 
      `${API_BASE.IAM}/users/${id}/documents/${docId}`,
    GROUPS: (id: string) => `${API_BASE.IAM}/users/${id}/groups`,
    PROFILES: (id: string) => `${API_BASE.IAM}/users/${id}/profiles`,
    PERMISSIONS: (id: string) => `${API_BASE.IAM}/users/${id}/permissions`,
    ACTIVITY: (id: string) => `${API_BASE.IAM}/users/${id}/activity`,
    RESET_PASSWORD: (id: string) => `${API_BASE.IAM}/users/${id}/reset-password`,
    RESET_MFA: (id: string) => `${API_BASE.IAM}/users/${id}/reset-mfa`,
    SEND_NOTIFICATION: (id: string) => `${API_BASE.IAM}/users/${id}/notify`,
  },
  GROUPS: {
    LIST: `${API_BASE.IAM}/groups`,
    DETAIL: (id: string) => `${API_BASE.IAM}/groups/${id}`,
    CREATE: `${API_BASE.IAM}/groups`,
    UPDATE: (id: string) => `${API_BASE.IAM}/groups/${id}`,
    DELETE: (id: string) => `${API_BASE.IAM}/groups/${id}`,
    MEMBERS: (id: string) => `${API_BASE.IAM}/groups/${id}/members`,
  },
  PROFILES: {
    LIST: `${API_BASE.IAM}/profiles`,
    DETAIL: (id: string) => `${API_BASE.IAM}/profiles/${id}`,
    CREATE: `${API_BASE.IAM}/profiles`,
    UPDATE: (id: string) => `${API_BASE.IAM}/profiles/${id}`,
    DELETE: (id: string) => `${API_BASE.IAM}/profiles/${id}`,
    PERMISSIONS: (id: string) => `${API_BASE.IAM}/profiles/${id}/permissions`,
  },
  PERMISSIONS: {
    LIST: `${API_BASE.IAM}/permissions`,
    DETAIL: (id: string) => `${API_BASE.IAM}/permissions/${id}`,
  },
} as const

// Admin API Endpoints
export const ADMIN_ENDPOINTS = {
  USERS: {
    LIST: `${API_BASE.ADMIN}/users`,
    DETAIL: (id: string) => `${API_BASE.ADMIN}/users/${id}`,
    UPDATE_STATUS: (id: string) => `${API_BASE.ADMIN}/users/${id}/status`,
    EXPORT: `${API_BASE.ADMIN}/users/export`,
  },
  VALIDATIONS: {
    LIST: `${API_BASE.ADMIN}/validations`,
    APPROVE: (id: string) => `${API_BASE.ADMIN}/validations/${id}/approve`,
    REJECT: (id: string) => `${API_BASE.ADMIN}/validations/${id}/reject`,
    STATS: `${API_BASE.ADMIN}/validations/stats`,
  },
  EMAIL: {
    SETTINGS: `${API_BASE.ADMIN}/email/settings`,
    TEST: `${API_BASE.ADMIN}/email/test`,
    HISTORY: `${API_BASE.ADMIN}/email/history`,
  },
} as const

// Auth API Endpoints
export const AUTH_ENDPOINTS = {
  LOGIN: `${API_BASE.AUTH}/login`,
  LOGOUT: `${API_BASE.AUTH}/logout`,
  REGISTER: `${API_BASE.AUTH}/register`,
  REFRESH: `${API_BASE.AUTH}/refresh`,
  MFA: {
    ENABLE: `${API_BASE.AUTH}/mfa/enable`,
    DISABLE: `${API_BASE.AUTH}/mfa/disable`,
    VERIFY: `${API_BASE.AUTH}/mfa/verify`,
  },
} as const

// Security API Endpoints
export const SECURITY_ENDPOINTS = {
  EMAIL_DOMAINS: {
    LIST: `${API_BASE.SECURITY}/email-domains`,
    VERIFY: `${API_BASE.SECURITY}/email-domains/verify`,
    CREATE: `${API_BASE.SECURITY}/email-domains`,
    UPDATE: (id: string) => `${API_BASE.SECURITY}/email-domains/${id}`,
    DELETE: (id: string) => `${API_BASE.SECURITY}/email-domains/${id}`,
  },
} as const

// Query Keys for React Query / RTK Query
export const QUERY_KEYS = {
  USERS: 'users',
  USER_DETAIL: 'userDetail',
  USER_DOCUMENTS: 'userDocuments',
  USER_GROUPS: 'userGroups',
  USER_PROFILES: 'userProfiles',
  USER_PERMISSIONS: 'userPermissions',
  USER_ACTIVITY: 'userActivity',
  GROUPS: 'groups',
  PROFILES: 'profiles',
  PERMISSIONS: 'permissions',
  VALIDATIONS: 'validations',
  EMAIL_SETTINGS: 'emailSettings',
  EMAIL_DOMAINS: 'emailDomains',
} as const

// HTTP Status Codes
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  INTERNAL_SERVER_ERROR: 500,
} as const

// API Response Messages
export const API_MESSAGES = {
  SUCCESS: {
    USER_CREATED: 'Utilisateur créé avec succès',
    USER_UPDATED: 'Utilisateur mis à jour avec succès',
    USER_DELETED: 'Utilisateur supprimé avec succès',
    USER_STATUS_UPDATED: 'Statut utilisateur mis à jour',
    PASSWORD_RESET: 'Mot de passe réinitialisé',
    MFA_RESET: 'MFA réinitialisé',
    NOTIFICATION_SENT: 'Notification envoyée',
    DOCUMENT_VERIFIED: 'Document vérifié avec succès',
    DOCUMENT_DELETED: 'Document supprimé avec succès',
    GROUP_ASSIGNED: 'Groupe assigné avec succès',
    GROUP_REMOVED: 'Groupe retiré avec succès',
    PROFILE_ASSIGNED: 'Profil assigné avec succès',
    EXPORT_SUCCESS: 'Export réussi',
  },
  ERROR: {
    USER_NOT_FOUND: 'Utilisateur non trouvé',
    UNAUTHORIZED: 'Non autorisé',
    FORBIDDEN: 'Accès interdit',
    INVALID_DATA: 'Données invalides',
    NETWORK_ERROR: 'Erreur réseau',
    SERVER_ERROR: 'Erreur serveur',
    DOCUMENT_NOT_FOUND: 'Document non trouvé',
    GROUP_NOT_FOUND: 'Groupe non trouvé',
    PROFILE_NOT_FOUND: 'Profil non trouvé',
    EXPORT_FAILED: 'Échec de l\'export',
  },
} as const

// Request Timeout Configuration
export const API_CONFIG = {
  TIMEOUT: 30000, // 30 seconds
  RETRY_COUNT: 3,
  RETRY_DELAY: 1000, // 1 second
} as const

export type QueryKey = typeof QUERY_KEYS[keyof typeof QUERY_KEYS]
export type HttpStatus = typeof HTTP_STATUS[keyof typeof HTTP_STATUS]
