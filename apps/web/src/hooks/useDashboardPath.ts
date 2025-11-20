/**
 * Hook pour déterminer le chemin du dashboard en fonction des permissions IAM
 * Pas de valeurs en dur - 100% IAM dynamique
 */
import { usePermissions } from './usePermission'
import { useAppSelector } from '@/store/hooks'
import { useRoles } from './useAppConfig'

export const useDashboardPath = (): string => {
  const { user, isAuthenticated } = useAppSelector((state) => state.auth)
  const roles = useRoles()
  
  // Récupérer les permissions de l'utilisateur
  const { permissions } = usePermissions([
    'dashboard.access',
    'dashboard.candidat.access',
    'admin.dashboard',
    'admin.access',
  ])

  if (!isAuthenticated || !user) {
    return '/login'
  }

  // Ordre de priorité pour la détermination du dashboard
  // 1. Admin (le plus prioritaire)
  if (user.roles?.includes(roles.admin) || permissions['admin.access']) {
    return '/admin'
  }

  // 2. Intérimaire
  if (user.roles?.includes(roles.interim)) {
    return '/interimaire'
  }

  // 3. Entreprise
  if (user.roles?.includes(roles.company)) {
    return '/entreprise'
  }

  // 4. Agence
  if (user.roles?.includes(roles.agency)) {
    return '/agence'
  }

  // 5. Candidat (basé sur permission IAM, pas sur rôle)
  if (permissions['dashboard.candidat.access']) {
    return '/candidat'
  }

  // 6. Par défaut : page de profil
  return '/profile'
}
