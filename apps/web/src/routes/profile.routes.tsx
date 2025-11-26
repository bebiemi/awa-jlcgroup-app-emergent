import ProfilePage from '@/features/profile/pages/ProfilePage'
import DocumentsPage from '@/features/profile/pages/DocumentsPage'
import MyDocumentsPage from '@/features/documents/pages/MyDocumentsPage'
import SecuritySettingsPage from '@/pages/SecuritySettingsPage'
import MyTeamSettingsPage from '@/features/settings/pages/MyTeamSettingsPage'
import { AppRoute } from './types'

export const profileRoutes: AppRoute[] = [
  {
    path: '/profile',
    element: <ProfilePage />,
    requireAuth: true,
    requiredPermissions: ['profile.read.own'],
  },
  {
    path: '/documents',
    element: <MyDocumentsPage />,
    requireAuth: true,
    requiredPermissions: ['documents.read.own', 'documents.read.all'],
  },
  {
    path: '/documents/library',
    element: <DocumentsPage />,
    requireAuth: true,
    requiredPermissions: ['documents.read.all', 'documents.view_cv.all'],
  },
  {
    path: '/security',
    element: <SecuritySettingsPage />,
    requireAuth: true,
  },
  {
    path: '/settings/my-team',
    element: <MyTeamSettingsPage />,
    requiredPermissions: ['rbac.assign_profiles', 'rbac.assign_groups'],
    requireAllPermissions: false,
  },
]
