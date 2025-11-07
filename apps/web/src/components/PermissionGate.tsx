/**
 * PermissionGate Component
 * Conditionally renders children based on user permissions
 */
import React from 'react'
import { usePermission, useHasAnyPermission, useHasAllPermissions } from '@/hooks/usePermission'

interface PermissionGateProps {
  /** Single permission code required */
  permission?: string
  /** Array of permissions - user needs ANY of them */
  anyPermissions?: string[]
  /** Array of permissions - user needs ALL of them */
  allPermissions?: string[]
  /** Content to show if user has permission */
  children: React.ReactNode
  /** Optional fallback content if permission denied */
  fallback?: React.ReactNode
  /** Show loading state */
  showLoading?: boolean
}

/**
 * Gate component that shows/hides content based on permissions
 * 
 * Usage examples:
 * 
 * // Single permission
 * <PermissionGate permission="users.manage">
 *   <button>Manage Users</button>
 * </PermissionGate>
 * 
 * // Any of multiple permissions
 * <PermissionGate anyPermissions={["users.read", "users.manage"]}>
 *   <UserList />
 * </PermissionGate>
 * 
 * // All of multiple permissions
 * <PermissionGate allPermissions={["users.delete", "admin.access"]}>
 *   <DeleteUserButton />
 * </PermissionGate>
 * 
 * // With fallback
 * <PermissionGate permission="admin.access" fallback={<div>Access Denied</div>}>
 *   <AdminPanel />
 * </PermissionGate>
 */
export default function PermissionGate({
  permission,
  anyPermissions,
  allPermissions,
  children,
  fallback = null,
  showLoading = false,
}: PermissionGateProps) {
  // Single permission check
  const singlePermissionCheck = usePermission(permission || '')
  
  // Any permissions check
  const anyPermissionCheck = useHasAnyPermission(anyPermissions || [])
  
  // All permissions check
  const allPermissionCheck = useHasAllPermissions(allPermissions || [])

  // Determine which check to use
  let hasAccess = false
  let isLoading = false

  if (permission) {
    hasAccess = singlePermissionCheck.hasPermission
    isLoading = singlePermissionCheck.isLoading
  } else if (anyPermissions && anyPermissions.length > 0) {
    hasAccess = anyPermissionCheck.hasAnyPermission
    isLoading = anyPermissionCheck.isLoading
  } else if (allPermissions && allPermissions.length > 0) {
    hasAccess = allPermissionCheck.hasAllPermissions
    isLoading = allPermissionCheck.isLoading
  }

  // Show loading state if requested
  if (showLoading && isLoading) {
    return (
      <div className="flex items-center justify-center p-4">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  // Show children if user has access, otherwise show fallback
  return hasAccess ? <>{children}</> : <>{fallback}</>
}

/**
 * Higher-Order Component version of PermissionGate
 * Wraps a component and only renders it if user has permission
 */
export function withPermission<P extends object>(
  Component: React.ComponentType<P>,
  permission: string,
  fallback?: React.ReactNode
) {
  return function PermissionWrappedComponent(props: P) {
    return (
      <PermissionGate permission={permission} fallback={fallback}>
        <Component {...props} />
      </PermissionGate>
    )
  }
}

/**
 * Hook-based alternative - returns boolean for manual control
 * Use this when you need more control over the rendering logic
 */
export function usePermissionGate(config: {
  permission?: string
  anyPermissions?: string[]
  allPermissions?: string[]
}) {
  const singlePermissionCheck = usePermission(config.permission || '')
  const anyPermissionCheck = useHasAnyPermission(config.anyPermissions || [])
  const allPermissionCheck = useHasAllPermissions(config.allPermissions || [])

  let hasAccess = false
  let isLoading = false

  if (config.permission) {
    hasAccess = singlePermissionCheck.hasPermission
    isLoading = singlePermissionCheck.isLoading
  } else if (config.anyPermissions && config.anyPermissions.length > 0) {
    hasAccess = anyPermissionCheck.hasAnyPermission
    isLoading = anyPermissionCheck.isLoading
  } else if (config.allPermissions && config.allPermissions.length > 0) {
    hasAccess = allPermissionCheck.hasAllPermissions
    isLoading = allPermissionCheck.isLoading
  }

  return {
    hasAccess,
    isLoading,
  }
}
