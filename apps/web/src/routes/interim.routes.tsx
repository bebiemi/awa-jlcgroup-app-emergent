import { Navigate } from 'react-router-dom'
import InterimDashboard from '@/features/interim/pages/InterimDashboard'
import PostulantMainDashboard from '@/features/postulant/pages/PostulantMainDashboard'
import { AppRoute } from './types'

export const interimRoutes: AppRoute[] = [
  {
    path: '/interimaire',
    element: <InterimDashboard />,
    requiredPermissions: ['missions.browse', 'missions.read.all', 'missions.read.own'],
  },
  {
    path: '/candidat',
    element: <PostulantMainDashboard />,
    requireAuth: true,
  },
  {
    path: '/postulant',
    element: <Navigate to="/candidat" replace />,
  },
  {
    path: '/postulant/profile-overview',
    element: <Navigate to="/candidat" replace />,
  },
  {
    path: '/missions-interim',
    element: <Navigate to="/offres" replace />,
    requiredPermissions: ['missions.browse', 'missions.read.all'],
  },
]
