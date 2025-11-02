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
  const { data: user, isLoading } = useGetCurrentUserQuery(undefined, {
    skip: !token,
  })

  if (!isAuthenticated || !token) {
    return <Navigate to="/login" replace />
  }

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
