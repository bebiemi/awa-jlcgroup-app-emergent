import { ReactNode } from 'react'
import { RouteObject } from 'react-router-dom'
import ProtectedRoute from '@/features/auth/components/ProtectedRoute'
import { AppRoute } from './types'

const wrapWithProtection = (route: AppRoute): ReactNode => {
  const shouldProtect = route.requireAuth || (route.requiredPermissions && route.requiredPermissions.length > 0)

  if (!shouldProtect) {
    return route.element
  }

  return (
    <ProtectedRoute
      requiredPermissions={route.requiredPermissions}
      requireAllPermissions={route.requireAllPermissions}
    >
      {route.element}
    </ProtectedRoute>
  )
}

export const mapRoutesToObjects = (routes: AppRoute[]): RouteObject[] =>
  routes.map((route) => ({
    path: route.path,
    element: wrapWithProtection(route),
    children: route.children ? mapRoutesToObjects(route.children) : undefined,
  }))
