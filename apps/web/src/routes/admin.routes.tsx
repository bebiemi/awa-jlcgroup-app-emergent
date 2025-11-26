import { Navigate } from 'react-router-dom'
import AdminDashboard from '@/features/admin/pages/AdminDashboard'
import { ValidationsPage } from '@/features/validations'
import { UsersPage } from '@/features/users'
import CreateUserPage from '@/features/admin/pages/CreateUserPage'
import LocationManagementPage from '@/features/admin/pages/LocationManagementPage'
import ReferencesManagementPage from '@/features/admin/pages/ReferencesManagementPage'
import CountryConfigPage from '@/features/admin/pages/CountryConfigPage'
import BusinessRulesPage from '@/features/admin/pages/BusinessRulesPage'
import ConfigurationVersionsPage from '@/features/admin/pages/ConfigurationVersionsPage'
import FeatureFlagsPage from '@/features/admin/pages/FeatureFlagsPage'
import { EmailSettingsPage } from '@/features/admin/pages/EmailSettingsPage'
import { EmailHistoryPage } from '@/features/admin/pages/EmailHistoryPage'
import { EmailTemplatesPage } from '@/features/admin/pages/EmailTemplatesPage'
import RetentionConfigPage from '@/features/admin/pages/RetentionConfigPage'
import ProfilesManagementPage from '@/features/iam/pages/ProfilesManagementPage'
import GroupsManagementPage from '@/features/iam/pages/GroupsManagementPage'
import IAMControlPage from '@/features/iam/pages/IAMControlPage'
import EmailDomainsPage from '@/features/admin/pages/EmailDomainsPage'
import { EntreprisesPage } from '@/features/entreprises'
import EntrepriseFormConfigPage from '@/features/admin/pages/EntrepriseFormConfigPage'
import { BesoinsPage } from '@/features/besoins'
import { MissionsPage } from '@/features/missions'
import CreateMissionPage from '@/features/missions/pages/CreateMissionPage'
import { AppRoute } from './types'

export const adminRoutes: AppRoute[] = [
  {
    path: '/admin',
    element: <AdminDashboard />,
    requiredPermissions: ['admin.dashboard', 'admin.access'],
    requireAllPermissions: true,
  },
  {
    path: '/admin/validations',
    element: <ValidationsPage />,
    requiredPermissions: ['validations.read.all'],
  },
  {
    path: '/admin/users',
    element: <UsersPage />,
    requiredPermissions: ['users.read', 'users.manage'],
  },
  {
    path: '/admin/users/new',
    element: <CreateUserPage />,
    requiredPermissions: ['users.manage', 'users.create'],
    requireAllPermissions: true,
  },
  {
    path: '/admin/groups',
    element: <Navigate to="/admin/iam/control" replace />,
  },
  {
    path: '/admin/profiles',
    element: <Navigate to="/admin/iam/profiles" replace />,
  },
  {
    path: '/admin/locations',
    element: <LocationManagementPage />,
    requiredPermissions: ['locations.manage'],
  },
  {
    path: '/admin/entreprises',
    element: <EntreprisesPage />,
    requiredPermissions: ['entreprises.read.all'],
  },
  {
    path: '/admin/config/entreprises',
    element: <EntrepriseFormConfigPage />,
    requiredPermissions: ['entreprises.read.all', 'entreprises.manage'],
    requireAllPermissions: true,
  },
  {
    path: '/admin/besoins',
    element: <BesoinsPage />,
    requiredPermissions: ['besoins.read.all'],
  },
  {
    path: '/admin/missions',
    element: <MissionsPage />,
    requiredPermissions: ['missions.read.all'],
  },
  {
    path: '/admin/missions/new',
    element: <CreateMissionPage />,
    requiredPermissions: ['missions.create.all'],
    requireAllPermissions: true,
  },
  {
    path: '/admin/references',
    element: <ReferencesManagementPage />,
    requiredPermissions: ['references.manage'],
  },
  {
    path: '/admin/countries',
    element: <CountryConfigPage />,
    requiredPermissions: ['admin.settings'],
  },
  {
    path: '/admin/rules',
    element: <BusinessRulesPage />,
    requiredPermissions: ['rules.manage'],
  },
  {
    path: '/admin/versions',
    element: <ConfigurationVersionsPage />,
    requiredPermissions: ['config.manage', 'admin.access'],
    requireAllPermissions: true,
  },
  {
    path: '/admin/feature-flags',
    element: <FeatureFlagsPage />,
    requiredPermissions: ['flags.manage', 'admin.access'],
    requireAllPermissions: true,
  },
  {
    path: '/admin/email-settings',
    element: <EmailSettingsPage />,
    requiredPermissions: ['emails.configure', 'admin.access'],
    requireAllPermissions: true,
  },
  {
    path: '/admin/email-history',
    element: <EmailHistoryPage />,
    requiredPermissions: ['emails.read_history'],
  },
  {
    path: '/admin/email-templates',
    element: <EmailTemplatesPage />,
    requiredPermissions: ['emails.manage_templates'],
  },
  {
    path: '/admin/retention-config',
    element: <RetentionConfigPage />,
    requiredPermissions: ['users.manage'],
  },
  {
    path: '/admin/iam/profiles',
    element: <ProfilesManagementPage />,
    requiredPermissions: ['iam.profiles.manage', 'iam.groups.manage'],
    requireAllPermissions: true,
  },
  {
    path: '/admin/iam/groups',
    element: <GroupsManagementPage />,
    requiredPermissions: ['iam.groups.manage', 'iam.profiles.manage'],
    requireAllPermissions: true,
  },
  {
    path: '/admin/iam/control',
    element: <IAMControlPage />,
    requiredPermissions: ['iam.groups.manage', 'iam.profiles.manage'],
    requireAllPermissions: true,
  },
  {
    path: '/admin/iam/roles',
    element: <Navigate to="/admin/iam/groups" replace />,
  },
  {
    path: '/admin/security/email-domains',
    element: <EmailDomainsPage />,
    requiredPermissions: ['security.email_domains.read'],
  },
]
