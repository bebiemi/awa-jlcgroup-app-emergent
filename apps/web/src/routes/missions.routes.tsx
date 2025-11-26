import { MissionsPage } from '@/features/missions'
import MissionDetailPage from '@/features/missions/pages/MissionDetailPage'
import CreateMissionPage from '@/features/missions/pages/CreateMissionPage'
import EditMissionPage from '@/features/missions/pages/EditMissionPage'
import ApplicationsManagementPage from '@/features/missions/pages/ApplicationsManagementPage'
import MyApplicationsPage from '@/features/missions/pages/MyApplicationsPage'
import MesCandidaturesPage from '@/features/interim/pages/MesCandidaturesPage'
import { AppRoute } from './types'

export const missionsRoutes: AppRoute[] = [
  {
    path: '/missions',
    element: <MissionsPage />,
    requiredPermissions: ['missions.read.all', 'missions.read.own', 'missions.browse'],
  },
  {
    path: '/missions/create',
    element: <CreateMissionPage />,
    requiredPermissions: ['missions.create.all', 'missions.create.own'],
  },
  {
    path: '/missions/:id',
    element: <MissionDetailPage />,
    requiredPermissions: ['missions.read.all', 'missions.read.own', 'missions.browse'],
  },
  {
    path: '/missions/:id/edit',
    element: <EditMissionPage />,
    requiredPermissions: ['missions.edit.all', 'missions.edit.own'],
  },
  {
    path: '/missions/:id/candidatures',
    element: <ApplicationsManagementPage />,
    requiredPermissions: ['applications.manage', 'applications.read.all'],
  },
  {
    path: '/my-applications',
    element: <MyApplicationsPage />,
    requiredPermissions: ['applications.read.own'],
  },
  {
    path: '/mes-candidatures',
    element: <MesCandidaturesPage />,
    requiredPermissions: ['applications.read.all', 'applications.read.own'],
  },
]
