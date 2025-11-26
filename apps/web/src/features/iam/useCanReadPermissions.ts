import { useHasAnyPermission } from '@/hooks/usePermission'
import { useAppSelector } from '@/store/hooks'

/**
 * Centralise la logique d'accès à la liste des permissions IAM.
 * Autorise l'appel uniquement si l'utilisateur dispose d'un scope IAM/Admin pertinent.
 */
export const useCanReadPermissions = () => {
  const { user } = useAppSelector((state) => state.auth)
  const { hasAnyPermission } = useHasAnyPermission([
    'iam.permissions.read',
    'iam.permissions.manage',
    'iam.profiles.manage',
    'iam.groups.manage',
    'admin.access',
    'admin.dashboard',
  ])

  // Les super_admins doivent toujours pouvoir charger les permissions
  const normalizedRoles = (user?.roles || []).map((r) => r.toLowerCase())
  const isSuperAdmin = normalizedRoles.includes('super_admin') || normalizedRoles.includes('superadmin')
  const hasWildcard = Boolean(user?.permissions?.includes('*.*'))

  return { canReadPermissions: hasAnyPermission || isSuperAdmin || hasWildcard }
}
