/**
 * Hook pour accéder à la configuration de l'application
 * Charge depuis l'API backend avec fallback sur valeurs par défaut
 */
import { useGetAllConfigQuery } from '@/features/admin/api/configurationApi'

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
    admin: 'admin',
    super_admin: 'super_admin',
    company: 'company',
    interim: 'interim',
    agency: 'agency',
    commercial: 'commercial',
    validator: 'validator'
  },
  userStatuses: {
    active: 'active',
    pending: 'pending',
    suspended: 'suspended',
    deleted: 'deleted',
    blocked: 'blocked'
  },
  missionStatuses: ['draft', 'published', 'closed', 'cancelled', 'archived'],
  applicationStatuses: ['submitted', 'review', 'interview_scheduled', 'interviewed', 'selected', 'rejected', 'medical_pending', 'medical_completed', 'contract_pending', 'contract_signed'],
  validationStatuses: ['pending', 'approved', 'rejected'],
  validationTypes: ['interim', 'company', 'collaborator'],
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
  return {
    active: 'active',
    pending: 'pending',
    suspended: 'suspended',
    deleted: 'deleted',
    blocked: 'blocked'
  }
}

/**
 * Hook pour accéder aux statuts de mission
 */
export const useMissionStatuses = () => {
  return {
    draft: 'draft',
    published: 'published',
    closed: 'closed',
    cancelled: 'cancelled',
    archived: 'archived'
  }
}

/**
 * Hook pour accéder aux statuts d'application
 */
export const useApplicationStatuses = () => {
  return {
    submitted: 'submitted',
    review: 'review',
    interview_scheduled: 'interview_scheduled',
    interviewed: 'interviewed',
    selected: 'selected',
    rejected: 'rejected',
    medical_pending: 'medical_pending',
    medical_completed: 'medical_completed',
    contract_pending: 'contract_pending',
    contract_signed: 'contract_signed'
  }
}

/**
 * Hook pour accéder aux types de validation
 */
export const useValidationTypes = () => {
  return {
    interim: 'interim',
    company: 'company',
    collaborator: 'collaborator'
  }
}

/**
 * Hook principal pour accéder à toute la configuration
 */
export const useAppConfig = (): AppConfig => {
  const roles = useRoles()
  const userStatuses = useUserStatuses()
  
  return {
    roles,
    userStatuses,
    missionStatuses: ['draft', 'published', 'closed', 'cancelled', 'archived'],
    applicationStatuses: ['submitted', 'review', 'interview_scheduled', 'interviewed', 'selected', 'rejected', 'medical_pending', 'medical_completed', 'contract_pending', 'contract_signed'],
    validationStatuses: ['pending', 'approved', 'rejected'],
    validationTypes: ['interim', 'company', 'collaborator'],
    contractTypes: ['cdi', 'cdd', 'interim', 'freelance', 'stage'],
  }
}
