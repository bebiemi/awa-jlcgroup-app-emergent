/**
 * Hook pour accéder à la configuration de l'application
 * Retourne les valeurs de configuration par défaut
 * TODO: Charger depuis l'API backend quand les référentiels sont initialisés
 */

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

/**
 * Hook pour accéder aux rôles de l'application
 * Retourne les valeurs configurées depuis le backend
 */
export const useRoles = () => {
  // Valeurs de configuration par défaut
  // Ces valeurs correspondent à celles définies dans base.yaml
  return {
    admin: 'admin',
    super_admin: 'super_admin',
    company: 'company',
    interim: 'interim',
    agency: 'agency',
    commercial: 'commercial',
    validator: 'validator'
  }
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
  const { data: references = [] } = configurationApi.useGetReferencesByCategoryQuery('mission_statuses')
  
  const statuses = references.reduce((acc, ref) => {
    acc[ref.code] = ref.code
    return acc
  }, {} as Record<string, string>)
  
  return statuses && Object.keys(statuses).length > 0 ? statuses : {
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
  const { data: references = [] } = configurationApi.useGetReferencesByCategoryQuery('application_statuses')
  
  const statuses = references.reduce((acc, ref) => {
    acc[ref.code] = ref.code
    return acc
  }, {} as Record<string, string>)
  
  return statuses && Object.keys(statuses).length > 0 ? statuses : {
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
  const { data: references = [] } = configurationApi.useGetReferencesByCategoryQuery('validation_types')
  
  const types = references.reduce((acc, ref) => {
    acc[ref.code] = ref.code
    return acc
  }, {} as Record<string, string>)
  
  return types && Object.keys(types).length > 0 ? types : {
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
  const { data: missionStatusesRefs = [] } = configurationApi.useGetReferencesByCategoryQuery('mission_statuses')
  const { data: applicationStatusesRefs = [] } = configurationApi.useGetReferencesByCategoryQuery('application_statuses')
  const { data: validationStatusesRefs = [] } = configurationApi.useGetReferencesByCategoryQuery('validation_statuses')
  const { data: validationTypesRefs = [] } = configurationApi.useGetReferencesByCategoryQuery('validation_types')
  const { data: contractTypesRefs = [] } = configurationApi.useGetReferencesByCategoryQuery('contract_types')
  
  return {
    roles,
    userStatuses,
    missionStatuses: missionStatusesRefs.map(r => r.code),
    applicationStatuses: applicationStatusesRefs.map(r => r.code),
    validationStatuses: validationStatusesRefs.map(r => r.code),
    validationTypes: validationTypesRefs.map(r => r.code),
    contractTypes: contractTypesRefs.map(r => r.code),
  }
}
