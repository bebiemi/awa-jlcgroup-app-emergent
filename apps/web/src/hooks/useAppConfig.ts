/**
 * Hook pour accéder à la configuration de l'application
 * Charge depuis l'API backend avec fallback sur valeurs par défaut
 */
import { useGetAllConfigQuery } from '@/features/admin/api/configurationApi'
import { ValidationTypes, UserRoles } from '@/constants/iamConstants'

export interface AppConfig {
  roles: {
    admin: string
    super_admin: string
    company: string
    interim: string
    agency: string
    commercial: string
    validator: string
  }
  userStatuses: {
    active: string
    pending: string
    suspended: string
    deleted: string
    blocked: string
    archived: string
  }
  missionStatuses: string[]
  applicationStatuses: string[]
  validationStatuses: string[]
  validationTypes: string[]
  contractTypes: string[]
}

// Valeurs par défaut (fallback si API échoue)
const DEFAULT_CONFIG: AppConfig = {
  roles: {
    admin: UserRoles.ADMIN,
    super_admin: UserRoles.SUPER_ADMIN,
    company: UserRoles.COMPANY,
    interim: UserRoles.INTERIM,
    agency: 'agency',
    commercial: 'commercial',
    validator: 'validator'
  },
  userStatuses: {
    active: 'active',
    pending: 'pending',
    suspended: 'suspended',
    deleted: 'deleted',
    blocked: 'blocked',
    archived: 'archived'
  },
  missionStatuses: ['draft', 'published', 'closed', 'cancelled', 'archived'],
  applicationStatuses: ['submitted', 'review', 'interview_scheduled', 'interviewed', 'selected', 'rejected', 'medical_pending', 'medical_completed', 'contract_pending', 'contract_signed'],
  validationStatuses: ['pending', 'approved', 'rejected'],
  validationTypes: [
    ValidationTypes.CANDIDAT,
    ValidationTypes.POSTULANT,
    ValidationTypes.INTERIM,
    ValidationTypes.COMPANY,
    ValidationTypes.COLLABORATEUR,
  ],
  contractTypes: ['cdi', 'cdd', 'interim', 'freelance', 'stage'],
}

/**
 * Hook pour accéder aux rôles de l'application
 * Charge depuis l'API backend avec fallback
 */
export const useRoles = () => {
  const { data, isLoading, isError } = useGetAllConfigQuery()
  
  // Si chargement ou erreur, utiliser valeurs par défaut
  if (isLoading || isError || !data) {
    return DEFAULT_CONFIG.roles
  }
  
  return data.roles
}

/**
 * Hook pour accéder aux statuts utilisateur
 */
export const useUserStatuses = () => {
  const { data, isLoading, isError } = useGetAllConfigQuery()
  
  if (isLoading || isError || !data) {
    return DEFAULT_CONFIG.userStatuses
  }
  
  return data.user_statuses
}

/**
 * Hook pour accéder aux statuts de mission
 */
export const useMissionStatuses = () => {
  const { data, isLoading, isError } = useGetAllConfigQuery()

  if (isLoading || isError || !data) {
    return DEFAULT_CONFIG.missionStatuses.reduce((acc, status) => {
      acc[status] = status
      return acc
    }, {} as Record<string, string>)
  }

  // Convertir array en objet pour compatibilité
  const statuses = data.mission_statuses
  return statuses.reduce((acc, status) => {
    acc[status] = status
    return acc
  }, {} as Record<string, string>)
}

/**
 * Hook pour accéder aux statuts d'application
 */
export const useApplicationStatuses = () => {
  const { data, isLoading, isError } = useGetAllConfigQuery()

  if (isLoading || isError || !data) {
    return DEFAULT_CONFIG.applicationStatuses.reduce((acc, status) => {
      acc[status] = status
      return acc
    }, {} as Record<string, string>)
  }

  const statuses = data.application_statuses
  return statuses.reduce((acc, status) => {
    acc[status] = status
    return acc
  }, {} as Record<string, string>)
}

/**
 * Hook pour accéder aux types de validation
 */
export const useValidationTypes = () => {
  const { data, isLoading, isError } = useGetAllConfigQuery()

  const fallbackTypes = {
    [ValidationTypes.CANDIDAT]: ValidationTypes.CANDIDAT,
    [ValidationTypes.POSTULANT]: ValidationTypes.POSTULANT,
    [ValidationTypes.INTERIM]: ValidationTypes.INTERIM,
    [ValidationTypes.COMPANY]: ValidationTypes.COMPANY,
    [ValidationTypes.COLLABORATEUR]: ValidationTypes.COLLABORATEUR,
    collaborator: ValidationTypes.COLLABORATEUR,
  }

  const types = !isLoading && !isError && data ? data.validation_types : DEFAULT_CONFIG.validationTypes
  return types.reduce((acc, type) => {
    acc[type] = type
    return acc
  }, { ...fallbackTypes } as Record<string, string>)
}

/**
 * Hook principal pour accéder à toute la configuration
 * Charge depuis l'API avec fallback sur DEFAULT_CONFIG
 */
export const useAppConfig = (): AppConfig => {
  const { data, isLoading, isError } = useGetAllConfigQuery()
  
  // Si chargement ou erreur, retourner config par défaut
  if (isLoading || isError || !data) {
    return DEFAULT_CONFIG
  }
  
  return {
    roles: data.roles,
    userStatuses: data.user_statuses,
    missionStatuses: data.mission_statuses,
    applicationStatuses: data.application_statuses,
    validationStatuses: data.validation_statuses,
    validationTypes: data.validation_types,
    contractTypes: data.contract_types,
  }
}
