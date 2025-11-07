import { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { useAppSelector } from '@/store/hooks'
import { useGetCurrentUserQuery } from '../api/authApi'

interface ProtectedRouteProps {
  children: ReactNode
  requiredRoles?: string[]
}

export default function ProtectedRoute({
  children,
  requiredRoles,
}: ProtectedRouteProps) {
  const { isAuthenticated, token } = useAppSelector((state) => state.auth)
  
  // CRITICAL: Also check localStorage for token persistence
  const localToken = localStorage.getItem('access_token')
  const localUser = localStorage.getItem('user')
  
  // If no token in state OR localStorage, redirect to login
  if (!isAuthenticated || !token || !localToken || !localUser) {
    console.warn('🚨 ProtectedRoute: No valid authentication found, redirecting to login')
    return <Navigate to="/login" replace />
  }
  
  const { data: user, isLoading } = useGetCurrentUserQuery(undefined, {
    skip: !token,
  })

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
      </div>
    )
  }

  if (requiredRoles && user) {
    const hasRequiredRole = requiredRoles.some((role) => user.roles.includes(role))
    if (!hasRequiredRole) {
      return <Navigate to="/" replace />
    }
  }

  return <>{children}</>
}
