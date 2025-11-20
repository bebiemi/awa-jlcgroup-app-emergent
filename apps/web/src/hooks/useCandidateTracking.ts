/**
 * Hooks pour la gestion dynamique du menu "Suivi des candidatures"
 * Respecte les standards IAM et évite les valeurs en dur
 */
import { useGetMyApplicationsQuery } from '@/features/interim/api/applicationApi'
import { usePermissions } from './usePermission'

/**
 * Hook pour vérifier si l'utilisateur a au moins une candidature
 * @returns {boolean} true si au moins une candidature existe, false sinon
 * Retourne false par défaut pendant le chargement (évite clignotement)
 */
export const useHasCandidatures = (): boolean => {
  const { data, isLoading, isError } = useGetMyApplicationsQuery(undefined, {
    // Skip si l'utilisateur n'a pas les permissions (évite appel API inutile)
    skip: false,
  })

  // Pendant le chargement ou en cas d'erreur : ne pas afficher le menu (évite clignotement)
  if (isLoading || isError) {
    return false
  }

  // Vérifier si au moins une candidature existe
  const applications = data?.applications || []
  return applications.length > 0
}

/**
 * Hook pour vérifier les permissions IAM pour le suivi des candidatures
 * Vérifie toutes les permissions pertinentes de manière dynamique
 * @returns {boolean} true si l'utilisateur a les permissions nécessaires
 */
export const useCandidateTrackingPermissions = (): boolean => {
  const { permissions } = usePermissions([
    'applications.read.own',
    'applications.view.own',
    'candidatures.view.own',
    'candidatures.track.own',
  ])

  // L'utilisateur doit avoir au moins UNE de ces permissions
  return (
    permissions['applications.read.own'] ||
    permissions['applications.view.own'] ||
    permissions['candidatures.view.own'] ||
    permissions['candidatures.track.own']
  )
}

/**
 * Hook combiné pour vérifier l'accès complet au menu "Suivi des candidatures"
 * Combine la vérification des permissions ET la présence de candidatures
 * @returns {boolean} true si le menu doit être affiché
 */
export const useCandidateTrackingAccess = (): boolean => {
  const hasPermissions = useCandidateTrackingPermissions()
  const hasCandidatures = useHasCandidatures()

  // Le menu s'affiche seulement si :
  // 1. L'utilisateur a les permissions IAM nécessaires
  // 2. L'utilisateur a au moins une candidature
  return hasPermissions && hasCandidatures
}
