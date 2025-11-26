import React from 'react'
import { useMemo, useEffect } from 'react'
import { useLocation, useRoutes } from 'react-router-dom'
import { useAppSelector } from './store/hooks'
import { useInactivityLogout } from './hooks/useInactivityLogout'
import { useDashboardPath } from './hooks/useDashboardPath'
import { buildAppRoutes } from './routes'
import { mapRoutesToObjects } from './routes/utils'
import SidebarResolver from './components/SidebarResolver'
import RootLayout from './layouts/RootLayout'

function App() {
  const { isAuthenticated } = useAppSelector((state) => state.auth)
  const location = useLocation()

  // CRITICAL: Verify authentication on app load
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    const storedUser = localStorage.getItem('user')
    
    // If no token or user data, but app thinks user is authenticated, force logout
    if (isAuthenticated && (!token || !storedUser)) {
      console.error('🚨 Invalid session detected on app load - forcing logout')
      window.location.href = '/login'
    }
  }, [isAuthenticated])
  
  // Auto-logout after 30 minutes of inactivity
  useInactivityLogout()

  // Redirect to role-specific dashboard (IAM-based)
  const dashboardPath = useDashboardPath()
  const hasSession = useMemo(() => isAuthenticated || Boolean(localStorage.getItem('access_token')), [isAuthenticated])

  const routes = useMemo(
    () => buildAppRoutes({ isAuthenticated: hasSession, dashboardPath }),
    [hasSession, dashboardPath]
  )
  const routeObjects = useMemo(() => mapRoutesToObjects(routes), [routes])
  const element = useRoutes(routeObjects)

  const publicPaths = useMemo(
    () => new Set([
      '/',
      '/login',
      '/register',
      '/verify-email',
      '/forgot-password',
      '/reset-password',
      '/auth/google/callback',
      '/auth/role-selection',
    ]),
    []
  )

  const showShell = !publicPaths.has(location.pathname)

  if (!showShell) {
    return <>{element}</>
  }

  return (
    <>
      <SidebarResolver />
      <RootLayout>{element}</RootLayout>
    </>
  )
}

export default App
