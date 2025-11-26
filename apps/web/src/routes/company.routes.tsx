import CompanyDashboard from '@/features/company/pages/CompanyDashboard'
import CompanyCandidaturesPage from '@/features/company/pages/CompanyCandidaturesPage'
import CompanySettingsPage from '@/features/company/pages/CompanySettingsPageDynamic'
import GroupingRequestsPage from '@/features/company/pages/GroupingRequestsPage'
import AgencyDashboard from '@/features/agency/pages/AgencyDashboard'
import CommercialDashboard from '@/features/commercial/pages/CommercialDashboard'
import { AppRoute } from './types'

export const companyRoutes: AppRoute[] = [
  {
    path: '/entreprise',
    element: <CompanyDashboard />,
    requiredPermissions: ['dashboard.company.access'],
  },
  {
    path: '/entreprise/candidatures',
    element: <CompanyCandidaturesPage />,
    requiredPermissions: ['applications.read.all', 'applications.read.own'],
  },
  {
    path: '/entreprise/settings',
    element: <CompanySettingsPage />,
    requiredPermissions: ['entreprises.read.own', 'entreprises.edit.own'],
  },
  {
    path: '/entreprise/grouping',
    element: <GroupingRequestsPage />,
    requiredPermissions: ['entreprises.group_request'],
  },
  {
    path: '/agence',
    element: <AgencyDashboard />,
    requiredPermissions: ['admin.dashboard', 'admin.access'],
  },
  {
    path: '/commercial',
    element: <CommercialDashboard />,
    requiredPermissions: ['dashboard.commercial.access', 'missions.manage.all'],
    requireAllPermissions: true,
  },
]
