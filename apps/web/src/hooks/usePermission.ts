/**
 * Permission Management Hooks for IAM
 * Provides React hooks to check user permissions
 */
import { useMemo } from 'react'
import { useAppSelector } from '@/store/hooks'
import { useGetUserPermissionsQuery } from '@/features/iam/api/iamApi'

/**
 * Hook to check if current user has a specific permission
 * @param permissionCode - Permission code to check (e.g., "users.manage")
 * @returns Object with hasPermission boolean and isLoading state
 */
export function usePermission(permissionCode: string) {
  const { user } = useAppSelector((state) => state.auth)

  const hasPermission = useMemo(() => {
    if (!user) return false
    
    // SuperAdmin has all permissions
    if (user.roles.includes('super_admin')) return true
    
    // Get permissions from JWT (stored in user object)
    const allPermissions = user.permissions || []
    
    // Direct match
    if (allPermissions.includes(permissionCode)) return true
    
    // Wildcard matching (e.g., "users.*" matches "users.manage")
    const parts = permissionCode.split('.')
    for (let i = 0; i < parts.length; i++) {
      const wildcard = parts.slice(0, i + 1).join('.') + '.*'
      if (allPermissions.includes(wildcard)) return true
    }
    
    return false
  }, [user, permissionCode])

  return {
    hasPermission,
    isLoading: false,  // No API call, so never loading
  }
}

/**
 * Hook to check multiple permissions at once
 * @param permissionCodes - Array of permission codes to check
 * @returns Object with permissions map and isLoading state
 */
export function usePermissions(permissionCodes: string[]) {
  const { user } = useAppSelector((state) => state.auth)
  
  const { data: userPermissions, isLoading } = useGetUserPermissionsQuery(
    user?.id || '',
    {
      skip: !user?.id,
    }
  )

  const permissions = useMemo(() => {
    const result: Record<string, boolean> = {}
    
    if (!user) {
      permissionCodes.forEach(code => {
        result[code] = false
      })
      return result
    }
    
    // SuperAdmin has all permissions
    if (user.roles.includes('super_admin')) {
      permissionCodes.forEach(code => {
        result[code] = true
      })
      return result
    }
    
    if (!userPermissions) {
      permissionCodes.forEach(code => {
        result[code] = false
      })
      return result
    }
    
    const allPermissions = userPermissions.all_permissions.map(p => p.code)
    
    permissionCodes.forEach(code => {
      // Direct match
      if (allPermissions.includes(code)) {
        result[code] = true
        return
      }
      
      // Wildcard matching
      const parts = code.split('.')
      let hasWildcard = false
      for (let i = 0; i < parts.length; i++) {
        const wildcard = parts.slice(0, i + 1).join('.') + '.*'
        if (allPermissions.includes(wildcard)) {
          hasWildcard = true
          break
        }
      }
      
      result[code] = hasWildcard
    })
    
    return result
  }, [user, userPermissions, permissionCodes])

  return {
    permissions,
    isLoading,
  }
}

/**
 * Hook to check if user has ANY of the specified permissions
 * @param permissionCodes - Array of permission codes
 * @returns Object with hasAnyPermission boolean and isLoading state
 */
export function useHasAnyPermission(permissionCodes: string[]) {
  const { permissions, isLoading } = usePermissions(permissionCodes)
  
  const hasAnyPermission = useMemo(() => {
    return Object.values(permissions).some(hasPermission => hasPermission)
  }, [permissions])

  return {
    hasAnyPermission,
    isLoading,
  }
}

/**
 * Hook to check if user has ALL of the specified permissions
 * @param permissionCodes - Array of permission codes
 * @returns Object with hasAllPermissions boolean and isLoading state
 */
export function useHasAllPermissions(permissionCodes: string[]) {
  const { permissions, isLoading } = usePermissions(permissionCodes)
  
  const hasAllPermissions = useMemo(() => {
    return Object.values(permissions).every(hasPermission => hasPermission)
  }, [permissions])

  return {
    hasAllPermissions,
    isLoading,
  }
}

/**
 * DEPRECATED: Use usePermission instead
 * Legacy hook for role-based access
 */
export function useHasRole(role: string) {
  const { user } = useAppSelector((state) => state.auth)
  
  const hasRole = useMemo(() => {
    if (!user) return false
    return user.roles.includes(role)
  }, [user, role])

  return {
    hasRole,
    isLoading: false,
  }
}
