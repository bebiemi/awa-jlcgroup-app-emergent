/**
 * UI Constants
 * Centralized UI configuration values
 */

export const COLORS = {
  SUCCESS: {
    bg: 'bg-green-100',
    text: 'text-green-800',
    border: 'border-green-500',
    hover: 'hover:bg-green-200',
    full: '#10B981',
  },
  WARNING: {
    bg: 'bg-yellow-100',
    text: 'text-yellow-800',
    border: 'border-yellow-500',
    hover: 'hover:bg-yellow-200',
    full: '#F59E0B',
  },
  DANGER: {
    bg: 'bg-red-100',
    text: 'text-red-800',
    border: 'border-red-500',
    hover: 'hover:bg-red-200',
    full: '#EF4444',
  },
  INFO: {
    bg: 'bg-blue-100',
    text: 'text-blue-800',
    border: 'border-blue-500',
    hover: 'hover:bg-blue-200',
    full: '#3B82F6',
  },
  NEUTRAL: {
    bg: 'bg-gray-100',
    text: 'text-gray-800',
    border: 'border-gray-500',
    hover: 'hover:bg-gray-200',
    full: '#6B7280',
  },
  PRIMARY: {
    bg: 'bg-jlc-purple-100',
    text: 'text-jlc-purple-800',
    border: 'border-jlc-purple-500',
    hover: 'hover:bg-jlc-purple-200',
    full: '#6366F1',
  },
} as const

export const SPACING = {
  xs: 'p-1',
  sm: 'p-2',
  md: 'p-4',
  lg: 'p-6',
  xl: 'p-8',
} as const

export const SHADOWS = {
  sm: 'shadow-sm',
  md: 'shadow-md',
  lg: 'shadow-lg',
  xl: 'shadow-xl',
  none: 'shadow-none',
} as const

export const ROUNDED = {
  sm: 'rounded-sm',
  md: 'rounded-md',
  lg: 'rounded-lg',
  xl: 'rounded-xl',
  '2xl': 'rounded-2xl',
  full: 'rounded-full',
} as const

export const MODAL_SIZES = {
  sm: 'max-w-md',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
  xl: 'max-w-4xl',
  '2xl': 'max-w-6xl',
  full: 'max-w-full',
} as const

export const BADGE_VARIANTS = {
  success: `${COLORS.SUCCESS.bg} ${COLORS.SUCCESS.text}`,
  warning: `${COLORS.WARNING.bg} ${COLORS.WARNING.text}`,
  danger: `${COLORS.DANGER.bg} ${COLORS.DANGER.text}`,
  info: `${COLORS.INFO.bg} ${COLORS.INFO.text}`,
  neutral: `${COLORS.NEUTRAL.bg} ${COLORS.NEUTRAL.text}`,
  primary: `${COLORS.PRIMARY.bg} ${COLORS.PRIMARY.text}`,
} as const

export const BUTTON_VARIANTS = {
  primary: 'bg-jlc-purple-600 hover:bg-jlc-purple-700 text-white',
  secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-900',
  success: 'bg-green-600 hover:bg-green-700 text-white',
  danger: 'bg-red-600 hover:bg-red-700 text-white',
  warning: 'bg-yellow-600 hover:bg-yellow-700 text-white',
  ghost: 'bg-transparent hover:bg-gray-100 text-gray-700',
  outline: 'border-2 border-gray-300 hover:border-gray-400 bg-transparent',
} as const

export const ICON_SIZES = {
  xs: 'h-3 w-3',
  sm: 'h-4 w-4',
  md: 'h-5 w-5',
  lg: 'h-6 w-6',
  xl: 'h-8 w-8',
  '2xl': 'h-10 w-10',
} as const

export const TEXT_SIZES = {
  xs: 'text-xs',
  sm: 'text-sm',
  base: 'text-base',
  lg: 'text-lg',
  xl: 'text-xl',
  '2xl': 'text-2xl',
  '3xl': 'text-3xl',
} as const

export const FONT_WEIGHTS = {
  normal: 'font-normal',
  medium: 'font-medium',
  semibold: 'font-semibold',
  bold: 'font-bold',
} as const

// User Status Configuration
export const USER_STATUS_CONFIG = {
  active: {
    label: 'Actif',
    color: BADGE_VARIANTS.success,
    icon: '✓',
  },
  inactive: {
    label: 'Inactif',
    color: BADGE_VARIANTS.neutral,
    icon: '○',
  },
  suspended: {
    label: 'Suspendu',
    color: BADGE_VARIANTS.danger,
    icon: '⊗',
  },
  pending: {
    label: 'En attente',
    color: BADGE_VARIANTS.warning,
    icon: '⏱',
  },
} as const

// Document Types Configuration
export const DOCUMENT_TYPES = {
  ID_CARD: {
    code: 'id_card',
    label: 'Carte d\'identité',
    icon: '🪪',
    required: true,
  },
  PASSPORT: {
    code: 'passport',
    label: 'Passeport',
    icon: '📘',
    required: false,
  },
  CV: {
    code: 'cv',
    label: 'CV',
    icon: '📄',
    required: true,
  },
  DIPLOMA: {
    code: 'diploma',
    label: 'Diplôme',
    icon: '🎓',
    required: false,
  },
  CONTRACT: {
    code: 'contract',
    label: 'Contrat',
    icon: '📝',
    required: false,
  },
  PROOF_OF_ADDRESS: {
    code: 'proof_of_address',
    label: 'Justificatif de domicile',
    icon: '🏠',
    required: true,
  },
  SOCIAL_SECURITY: {
    code: 'social_security',
    label: 'Sécurité sociale',
    icon: '🏥',
    required: true,
  },
  WORK_PERMIT: {
    code: 'work_permit',
    label: 'Permis de travail',
    icon: '💼',
    required: false,
  },
  OTHER: {
    code: 'other',
    label: 'Autre',
    icon: '📎',
    required: false,
  },
} as const

// Modal Tab Configuration
export const USER_DETAIL_TABS = {
  INFO: {
    id: 'info',
    label: 'Informations',
    icon: '👤',
  },
  DOCUMENTS: {
    id: 'documents',
    label: 'Documents',
    icon: '📂',
  },
  PERMISSIONS: {
    id: 'permissions',
    label: 'Permissions & Groupes',
    icon: '🔐',
  },
  ACTIVITY: {
    id: 'activity',
    label: 'Activité',
    icon: '📊',
  },
} as const

// Action Configuration
export const USER_ACTIONS = {
  EDIT: {
    id: 'edit',
    label: 'Modifier',
    icon: '✏️',
    color: COLORS.INFO,
  },
  DELETE: {
    id: 'delete',
    label: 'Supprimer',
    icon: '🗑️',
    color: COLORS.DANGER,
  },
  SUSPEND: {
    id: 'suspend',
    label: 'Suspendre',
    icon: '🚫',
    color: COLORS.WARNING,
  },
  ACTIVATE: {
    id: 'activate',
    label: 'Activer',
    icon: '✅',
    color: COLORS.SUCCESS,
  },
  RESET_PASSWORD: {
    id: 'reset_password',
    label: 'Réinitialiser mot de passe',
    icon: '🔑',
    color: COLORS.WARNING,
  },
  RESET_MFA: {
    id: 'reset_mfa',
    label: 'Réinitialiser MFA',
    icon: '🔐',
    color: COLORS.WARNING,
  },
  SEND_NOTIFICATION: {
    id: 'send_notification',
    label: 'Envoyer notification',
    icon: '📧',
    color: COLORS.INFO,
  },
  VIEW_PROFILE: {
    id: 'view_profile',
    label: 'Voir profil',
    icon: '👁️',
    color: COLORS.PRIMARY,
  },
} as const

// Pagination Configuration
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 15,
  PAGE_SIZE_OPTIONS: [10, 15, 25, 50, 100],
} as const

// Export Configuration
export const EXPORT_FORMATS = {
  CSV: {
    format: 'csv',
    label: 'CSV',
    icon: '📊',
  },
  XLSX: {
    format: 'xlsx',
    label: 'Excel',
    icon: '📗',
  },
  PDF: {
    format: 'pdf',
    label: 'PDF',
    icon: '📕',
  },
} as const

export type ColorVariant = keyof typeof COLORS
export type BadgeVariant = keyof typeof BADGE_VARIANTS
export type ButtonVariant = keyof typeof BUTTON_VARIANTS
export type UserStatus = keyof typeof USER_STATUS_CONFIG
export type DocumentType = keyof typeof DOCUMENT_TYPES
export type UserDetailTab = keyof typeof USER_DETAIL_TABS
export type UserAction = keyof typeof USER_ACTIONS
