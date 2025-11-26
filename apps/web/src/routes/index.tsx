import { Navigate } from 'react-router-dom'
import { adminRoutes } from './admin.routes'
import { besoinsRoutes } from './besoins.routes'
import { companyRoutes } from './company.routes'
import { entreprisesRoutes } from './entreprises.routes'
import { interimRoutes } from './interim.routes'
import { missionsRoutes } from './missions.routes'
import { offresRoutes } from './offres.routes'
import { profileRoutes } from './profile.routes'
import { publicRoutes } from './public.routes'
import { supportRoutes } from './support.routes'
import { AppRoute } from './types'

type BuildRoutesParams = {
  isAuthenticated: boolean
  dashboardPath: string
}

export const buildAppRoutes = ({ isAuthenticated, dashboardPath }: BuildRoutesParams): AppRoute[] => [
  ...publicRoutes,
  ...adminRoutes,
  ...entreprisesRoutes,
  ...besoinsRoutes,
  ...missionsRoutes,
  ...offresRoutes,
  ...interimRoutes,
  ...companyRoutes,
  ...profileRoutes,
  ...supportRoutes,
  {
    path: '/dashboard',
    element: isAuthenticated ? (
      <Navigate to={dashboardPath} replace />
    ) : (
      <Navigate to="/login" replace />
    ),
  },
  { path: '*', element: <Navigate to="/" replace /> },
]
