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
    'dashboard.commercial.access',
    'dashboard.company.access',
    'admin.dashboard',
    'admin.access',
  ])

  if (!isAuthenticated || !user) {
    return '/login'
  }

  // Ordre de priorité pour la détermination du dashboard (IAM FIRST)
  // 1. Admin (le plus prioritaire)
  if (permissions['admin.dashboard'] || permissions['admin.access']) {
    return '/admin'
  }

  // 2. Commercial (AVANT entreprise pour éviter conflit)
  if (permissions['dashboard.commercial.access']) {
    return '/commercial'
  }

  // 3. Entreprise
  if (permissions['dashboard.company.access']) {
    return '/entreprise'
  }

  // 4. Candidat
  if (permissions['dashboard.candidat.access']) {
    return '/candidat'
  }

  // Par défaut : page de profil (si aucune permission dashboard)
  return '/profile'
}
