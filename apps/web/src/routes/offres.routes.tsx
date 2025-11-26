import OffresPage from '@/features/missions/pages/OffresPage'
import MissionDetailPage from '@/features/missions/pages/MissionDetailPage'
import ApplyMissionPage from '@/features/missions/pages/ApplyMissionPage'
import { AppRoute } from './types'

export const offresRoutes: AppRoute[] = [
  {
    path: '/offres',
    element: <OffresPage />,
    requiredPermissions: ['missions.browse', 'missions.read.all'],
  },
  {
    path: '/offres/:id',
    element: <MissionDetailPage />,
    requiredPermissions: ['missions.read.all', 'missions.read.own', 'missions.browse'],
  },
  {
    path: '/offres/:id/postuler',
    element: <ApplyMissionPage />,
    requiredPermissions: ['applications.create', 'applications.create.own'],
  },
]
