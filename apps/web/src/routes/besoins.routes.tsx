import BesoinsListPage from '@/features/besoins/pages/BesoinsListPage'
import CreateBesoinPage from '@/features/besoins/pages/CreateBesoinPage'
import BesoinDetailPage from '@/features/besoins/pages/BesoinDetailPage'
import { AppRoute } from './types'

export const besoinsRoutes: AppRoute[] = [
  {
    path: '/entreprise/besoins',
    element: <BesoinsListPage />,
    requiredPermissions: ['besoins.read.all', 'besoins.read.own'],
  },
  {
    path: '/entreprise/besoins/create',
    element: <CreateBesoinPage />,
    requiredPermissions: ['besoins.create.all', 'besoins.create.own'],
  },
  {
    path: '/entreprise/besoins/:id',
    element: <BesoinDetailPage />,
    requiredPermissions: ['besoins.read.all', 'besoins.read.own'],
  },
  {
    path: '/entreprise/besoins/:id/edit',
    element: <CreateBesoinPage />,
    requiredPermissions: ['besoins.edit.all', 'besoins.edit.own'],
  },
]
