import { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { useAppSelector } from '@/store/hooks'
import { useGetCurrentUserQuery } from '../api/authApi'
import { useHasAnyPermission, useHasAllPermissions } from '@/hooks/usePermission'

interface ProtectedRouteProps {
  children: ReactNode
  /** @deprecated Use requiredPermissions instead */
  requiredRoles?: string[]
  /** Permission-based access control (IAM) */
  requiredPermissions?: string[]
  /** Require ALL permissions (default: ANY) */
  requireAllPermissions?: boolean
}

export default function ProtectedRoute({
  children,
  requiredRoles,
  requiredPermissions,
  requireAllPermissions = false,
}: ProtectedRouteProps) {
  const { isAuthenticated, token } = useAppSelector((state) => state.auth)
  
  // CRITICAL: Also check localStorage for token persistence
  const localToken = localStorage.getItem('access_token')
  const localUser = localStorage.getItem('user')
  
  // FIXED: Check localStorage first (source of truth), then Redux state
  // This handles the case where Redux store hasn't hydrated yet
  const hasValidAuth = (localToken && localUser) || (isAuthenticated && token)
  
  if (!hasValidAuth) {
    console.warn('🚨 ProtectedRoute: No valid authentication found')
    console.warn('  - localStorage token:', !!localToken)
    console.warn('  - localStorage user:', !!localUser)
    console.warn('  - Redux isAuthenticated:', isAuthenticated)
    console.warn('  - Redux token:', !!token)
    return <Navigate to="/login" replace />
  }
  
  // Use localToken as fallback if Redux token not yet loaded
  const effectiveToken = token || localToken
  
  const { data: user, isLoading } = useGetCurrentUserQuery(undefined, {
    skip: !effectiveToken,
  })
  
  // Permission checks (IAM)
  const anyPermissionCheck = useHasAnyPermission(requiredPermissions || [])
  const allPermissionCheck = useHasAllPermissions(requiredPermissions || [])

  if (isLoading || anyPermissionCheck.isLoading || allPermissionCheck.isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
      </div>
    )
  }

  // NEW: Permission-based access control (IAM)
  if (requiredPermissions && requiredPermissions.length > 0) {
    const hasAccess = requireAllPermissions 
      ? allPermissionCheck.hasAllPermissions 
      : anyPermissionCheck.hasAnyPermission
    
    if (!hasAccess) {
      console.warn('🚫 ProtectedRoute: Permission denied. Required:', requiredPermissions)
      return <Navigate to="/" replace />
    }
  }

  // LEGACY: Role-based access control (deprecated)
  if (requiredRoles && user) {
    if (process.env.NODE_ENV === 'development') {
      console.warn('⚠️ ProtectedRoute: requiredRoles is DEPRECATED. Use requiredPermissions (IAM) instead.')
    }
    
    const hasRequiredRole = requiredRoles.some((role) => user.roles.includes(role))
    if (!hasRequiredRole) {
      console.warn('🚫 ProtectedRoute: Role denied. Required:', requiredRoles)
      return <Navigate to="/" replace />
    }
  }

  return <>{children}</>
}
