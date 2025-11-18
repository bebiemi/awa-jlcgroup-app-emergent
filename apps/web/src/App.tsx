import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAppSelector } from './store/hooks'
import { useInactivityLogout } from './hooks/useInactivityLogout'
import { useRoles } from './hooks/useAppConfig'
import LandingPage from './pages/LandingPage'
import LoginPage from './features/auth/pages/LoginPage'
import RegisterPage from './features/auth/pages/RegisterPage'
import VerifyEmailPage from './features/auth/pages/VerifyEmailPage'
import ForgotPasswordPage from './features/auth/pages/ForgotPasswordPage'
import ResetPasswordPage from './features/auth/pages/ResetPasswordPage'
import GoogleCallback from './features/auth/pages/GoogleCallback'
import RoleSelectionPage from './features/auth/pages/RoleSelectionPage'
import AdminDashboard from './features/admin/pages/AdminDashboard'
import ValidationsPage from './features/admin/pages/ValidationsPage'
import UserManagementPage from './features/admin/pages/UserManagementPage'
import CreateUserPage from './features/admin/pages/CreateUserPage'
// OLD: import GroupsPage from './features/admin/pages/GroupsPage' // DEPRECATED - Use IAMControlPage
// OLD: import ProfilesPage from './features/admin/pages/ProfilesPage' // DEPRECATED - Use ProfilesManagementPage
import ProfilesManagementPage from './features/iam/pages/ProfilesManagementPage'
import GroupsManagementPage from './features/iam/pages/GroupsManagementPage'
import IAMControlPage from './features/iam/pages/IAMControlPage'
import IAMRolesManagementPage from './features/iam/pages/IAMRolesManagementPage'
import MyTeamSettingsPage from './features/settings/pages/MyTeamSettingsPage'
import LocationManagementPage from './features/admin/pages/LocationManagementPage'
import ReferencesManagementPage from './features/admin/pages/ReferencesManagementPage'
import CountryConfigPage from './features/admin/pages/CountryConfigPage'
import RetentionConfigPage from './features/admin/pages/RetentionConfigPage'
import BusinessRulesPage from './features/admin/pages/BusinessRulesPage'
import ConfigurationVersionsPage from './features/admin/pages/ConfigurationVersionsPage'
import FeatureFlagsPage from './features/admin/pages/FeatureFlagsPage'
import { EmailSettingsPage } from './features/admin/pages/EmailSettingsPage'
import { EmailHistoryPage } from './features/admin/pages/EmailHistoryPage'
import { EmailTemplatesPage } from './features/admin/pages/EmailTemplatesPage'
import InterimDashboard from './features/interim/pages/InterimDashboard'
import UnifiedDashboard from './features/dashboard/pages/UnifiedDashboard'
import MesCandidaturesPage from './features/interim/pages/MesCandidaturesPage'
import ProfilePage from './features/profile/pages/ProfilePage'
import DocumentsPage from './features/profile/pages/DocumentsPage'
import SecuritySettingsPage from './pages/SecuritySettingsPage'
import EmailDomainsPage from './features/admin/pages/EmailDomainsPage'
import MissionsPage from './features/missions/pages/MissionsPage'
import OffresPage from './features/missions/pages/OffresPage'
import MissionDetailPage from './features/missions/pages/MissionDetailPage'
import CreateMissionPage from './features/missions/pages/CreateMissionPage'
import EditMissionPage from './features/missions/pages/EditMissionPage'
import BesoinsListPage from './features/besoins/pages/BesoinsListPage'
import CreateBesoinPage from './features/besoins/pages/CreateBesoinPage'
import BesoinDetailPage from './features/besoins/pages/BesoinDetailPage'
import ApplyMissionPage from './features/missions/pages/ApplyMissionPage'
import ApplicationsManagementPage from './features/missions/pages/ApplicationsManagementPage'
import MyApplicationsPage from './features/missions/pages/MyApplicationsPage'
import CompanyDashboard from './features/company/pages/CompanyDashboard'
import CompanySettingsPage from './features/company/pages/CompanySettingsPage'
import CompanyCandidaturesPage from './features/company/pages/CompanyCandidaturesPage'
import EntreprisesManagementPage from './features/admin/pages/EntreprisesManagementPage'
import AgencyDashboard from './features/agency/pages/AgencyDashboard'
import CommercialDashboard from './features/commercial/pages/CommercialDashboard'
import PostulantMainDashboard from './features/postulant/pages/PostulantMainDashboard'
import ProfileOverviewPage from './features/postulant/pages/ProfileOverviewPage'
import ProtectedRoute from './features/auth/components/ProtectedRoute'
import SupportTicketsPage from './features/support/pages/SupportTicketsPage'
import CreateTicketPage from './features/support/pages/CreateTicketPage'
import TicketDetailPage from './features/support/pages/TicketDetailPage'
import MyDocumentsPage from './features/documents/pages/MyDocumentsPage'

function App() {
  const { isAuthenticated, user } = useAppSelector((state) => state.auth)
  const roles = useRoles()
  
  // CRITICAL: Verify authentication on app load
  React.useEffect(() => {
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

  // Redirect to role-specific dashboard
  const getDashboardPath = () => {
    if (!user) return '/login'
    if (user.roles.includes(roles.admin)) return '/admin'
    if (user.roles.includes(roles.interim)) return '/interimaire'
    if (user.roles.includes(roles.company)) return '/entreprise'
    if (user.roles.includes(roles.agency)) return '/agence'
    if (user.roles.includes('postulant') || user.roles.includes('candidat')) return '/postulant'
    return '/profile'
  }

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/verify-email" element={<VerifyEmailPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />
      <Route path="/auth/google/callback" element={<GoogleCallback />} />
      <Route path="/auth/role-selection" element={<RoleSelectionPage />} />

      {/* Protected routes - IAM Permissions */}
      <Route
        path="/admin"
        element={
          <ProtectedRoute requiredPermissions={['admin.dashboard']}>
            <AdminDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/validations"
        element={
          <ProtectedRoute requiredPermissions={['validations.manage']}>
            <ValidationsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/users"
        element={
          <ProtectedRoute requiredPermissions={['users.read']}>
            <UserManagementPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/users/new"
        element={
          <ProtectedRoute requiredPermissions={['users.create']}>
            <CreateUserPage />
          </ProtectedRoute>
        }
      />
      {/* DEPRECATED: Old profiles/groups pages - Redirect to IAM */}
      <Route
        path="/admin/groups"
        element={<Navigate to="/admin/iam/control" replace />}
      />
      <Route
        path="/admin/profiles"
        element={<Navigate to="/admin/iam/profiles" replace />}
      />
      <Route
        path="/admin/locations"
        element={
          <ProtectedRoute requiredPermissions={['locations.manage']}>
            <LocationManagementPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/entreprises"
        element={
          <ProtectedRoute requiredPermissions={['entreprises.read']}>
            <EntreprisesManagementPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/references"
        element={
          <ProtectedRoute requiredPermissions={['references.manage']}>
            <ReferencesManagementPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/countries"
        element={
          <ProtectedRoute requiredPermissions={['admin.settings']}>
            <CountryConfigPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/rules"
        element={
          <ProtectedRoute requiredPermissions={['rules.manage']}>
            <BusinessRulesPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/versions"
        element={
          <ProtectedRoute requiredPermissions={['config.manage']}>
            <ConfigurationVersionsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/feature-flags"
        element={
          <ProtectedRoute requiredPermissions={['flags.manage']}>
            <FeatureFlagsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/email-settings"
        element={
          <ProtectedRoute requiredPermissions={['emails.configure']}>
            <EmailSettingsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/email-history"
        element={
          <ProtectedRoute requiredPermissions={['emails.read_history']}>
            <EmailHistoryPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/email-templates"
        element={
          <ProtectedRoute requiredPermissions={['emails.manage_templates']}>
            <EmailTemplatesPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/retention-config"
        element={
          <ProtectedRoute requiredPermissions={['users.manage']}>
            <RetentionConfigPage />
          </ProtectedRoute>
        }
      />
      
      {/* Routes IAM - SuperAdmin & Admin */}
      <Route
        path="/admin/iam/profiles"
        element={
          <ProtectedRoute requiredPermissions={['iam.profiles.manage']}>
            <ProfilesManagementPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/iam/groups"
        element={
          <ProtectedRoute requiredPermissions={['iam.groups.manage']}>
            <GroupsManagementPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/iam/control"
        element={
          <ProtectedRoute requiredPermissions={['iam.groups.manage']}>
            <IAMControlPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/iam/roles"
        element={
          <ProtectedRoute requiredPermissions={['rbac.manage_profile_roles', 'rbac.manage_group_roles']} requireAll={false}>
            <IAMRolesManagementPage />
          </ProtectedRoute>
        }
      />
      
      {/* Routes Missions - Admin & Commercial - IAM */}
      <Route
        path="/missions"
        element={
          <ProtectedRoute requiredPermissions={['missions.read', 'missions.manage']}>
            <MissionsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/missions/create"
        element={
          <ProtectedRoute requiredPermissions={['missions.create']}>
            <CreateMissionPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/missions/:id"
        element={
          <ProtectedRoute requiredPermissions={['missions.read']}>
            <MissionDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/missions/:id/edit"
        element={
          <ProtectedRoute requiredPermissions={['missions.edit']}>
            <EditMissionPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/missions/:id/candidatures"
        element={
          <ProtectedRoute requiredPermissions={['applications.manage']}>
            <ApplicationsManagementPage />
          </ProtectedRoute>
        }
      />
      
      {/* Routes Offres - IAM Permissions (postulants, candidats, intérimaires) */}
      <Route
        path="/offres"
        element={
          <ProtectedRoute requiredPermissions={['missions.browse']}>
            <OffresPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/offres/:id"
        element={
          <ProtectedRoute requiredPermissions={['missions.read']}>
            <MissionDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/offres/:id/postuler"
        element={
          <ProtectedRoute requiredPermissions={['applications.create']}>
            <ApplyMissionPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/mes-candidatures"
        element={
          <ProtectedRoute requiredPermissions={['applications.read_own']}>
            <MyApplicationsPage />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/interimaire"
        element={
          <ProtectedRoute requiredPermissions={['missions.browse']}>
            <InterimDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/postulant"
        element={
          <ProtectedRoute>
            <PostulantMainDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/postulant/profile-overview"
        element={
          <ProtectedRoute>
            <ProfileOverviewPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <UnifiedDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/missions-interim"
        element={
          <ProtectedRoute requiredPermissions={['missions.browse']}>
            <Navigate to="/offres" replace />
          </ProtectedRoute>
        }
      />
      <Route
        path="/mes-candidatures"
        element={
          <ProtectedRoute requiredPermissions={['applications.read_own']}>
            <MesCandidaturesPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/entreprise"
        element={
          <ProtectedRoute requiredPermissions={['besoins.create']}>
            <CompanyDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/entreprise/besoins"
        element={
          <ProtectedRoute requiredPermissions={['besoins.create']}>
            <BesoinsListPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/entreprise/besoins/create"
        element={
          <ProtectedRoute requiredPermissions={['besoins.create']}>
            <CreateBesoinPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/entreprise/besoins/:id"
        element={
          <ProtectedRoute requiredPermissions={['besoins.read']}>
            <BesoinDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/entreprise/besoins/:id/edit"
        element={
          <ProtectedRoute requiredPermissions={['besoins.edit']}>
            <CreateBesoinPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/entreprise/candidatures"
        element={
          <ProtectedRoute requiredPermissions={['applications.read']}>
            <CompanyCandidaturesPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/entreprise/settings"
        element={
          <ProtectedRoute requiredPermissions={['entreprises.read']}>
            <CompanySettingsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/offres"
        element={
          <ProtectedRoute requiredPermissions={['missions.create']}>
            <Navigate to="/admin" replace />
          </ProtectedRoute>
        }
      />
      <Route
        path="/agence"
        element={
          <ProtectedRoute requiredPermissions={['admin.dashboard']}>
            <AgencyDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/commercial"
        element={
          <ProtectedRoute requiredPermissions={['missions.manage']}>
            <CommercialDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/profile"
        element={
          <ProtectedRoute>
            <ProfilePage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings/my-team"
        element={
          <ProtectedRoute requiredPermissions={['rbac.assign_profiles', 'rbac.assign_groups']} requireAll={false}>
            <MyTeamSettingsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/documents"
        element={
          <ProtectedRoute>
            <DocumentsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/security"
        element={
          <ProtectedRoute>
            <SecuritySettingsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/security/email-domains"
        element={
          <ProtectedRoute requiredPermissions={['security.email_domains.read']}>
            <EmailDomainsPage />
          </ProtectedRoute>
        }
      />

      {/* Dashboard redirect for authenticated users */}
      <Route
        path="/dashboard"
        element={
          isAuthenticated ? (
            <Navigate to={getDashboardPath()} replace />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />

      {/* Support Routes */}
      <Route
        path="/support/tickets"
        element={
          <ProtectedRoute>
            <SupportTicketsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/support/tickets/new"
        element={
          <ProtectedRoute>
            <CreateTicketPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/support/tickets/:id"
        element={
          <ProtectedRoute>
            <TicketDetailPage />
          </ProtectedRoute>
        }
      />

      {/* Documents Route */}
      <Route
        path="/documents"
        element={
          <ProtectedRoute>
            <MyDocumentsPage />
          </ProtectedRoute>
        }
      />
      
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
