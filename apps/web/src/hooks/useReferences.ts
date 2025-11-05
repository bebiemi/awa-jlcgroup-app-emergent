import { useMemo } from 'react'
import { useGetReferencesQuery } from '@/features/admin/api/configurationApi'

export interface ReferenceOption {
  value: string
  label: string
  color?: string
  icon?: string
  metadata?: Record<string, any>
}

export function useReferences(category: string) {
  const { data, isLoading, error } = useGetReferencesQuery({
    category,
    is_active: true
  })

  const options: ReferenceOption[] = useMemo(() => {
    if (!data?.references) return []
    
    return data.references.map(ref => ({
      value: ref.code,
      label: ref.label_fr,
      color: ref.metadata?.color,
      icon: ref.metadata?.icon,
      metadata: ref.metadata
    }))
  }, [data])

  const getLabel = (code: string): string => {
    const ref = options.find(opt => opt.value === code)
    return ref?.label || code
  }

  const getMetadata = (code: string): Record<string, any> => {
    const ref = options.find(opt => opt.value === code)
    return ref?.metadata || {}
  }

  return {
    options,
    isLoading,
    error,
    getLabel,
    getMetadata
  }
}

// Hooks spécialisés pour les différentes catégories
export const useMissionStatuses = () => useReferences('mission_statuses')
export const useApplicationStatuses = () => useReferences('application_statuses')
export const useContractTypes = () => useReferences('contract_types')
export const useMedicalAptitudes = () => useReferences('medical_aptitudes')
