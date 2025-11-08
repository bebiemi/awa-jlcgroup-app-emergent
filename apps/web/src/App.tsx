import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAppSelector } from './store/hooks'
import { useInactivityLogout } from './hooks/useInactivityLogout'
import { useRoles } from './hooks/useAppConfig'
import LandingPage from './pages/LandingPage'
import LoginPage from './features/auth/pages/LoginPage'
import RegisterPage from './features/auth/pages/RegisterPage'
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
import IAMControlPage from './features/iam/pages/IAMControlPage'
import LocationManagementPage from './features/admin/pages/LocationManagementPage'
import ReferencesManagementPage from './features/admin/pages/ReferencesManagementPage'
import BusinessRulesPage from './features/admin/pages/BusinessRulesPage'
import ConfigurationVersionsPage from './features/admin/pages/ConfigurationVersionsPage'
import FeatureFlagsPage from './features/admin/pages/FeatureFlagsPage'
import { EmailSettingsPage } from './features/admin/pages/EmailSettingsPage'
import { EmailHistoryPage } from './features/admin/pages/EmailHistoryPage'
import { EmailTemplatesPage } from './features/admin/pages/EmailTemplatesPage'
import InterimDashboard from './features/interim/pages/InterimDashboard'
import MesCandidaturesPage from './features/interim/pages/MesCandidaturesPage'
import ProfilePage from './features/profile/pages/ProfilePage'
import SecuritySettingsPage from './pages/SecuritySettingsPage'
import MissionsPage from './features/missions/pages/MissionsPage'
import OffresPage from './features/missions/pages/OffresPage'
import MissionDetailPage from './features/missions/pages/MissionDetailPage'
import CreateMissionPage from './features/missions/pages/CreateMissionPage'
import EditMissionPage from './features/missions/pages/EditMissionPage'
import ApplyMissionPage from './features/missions/pages/ApplyMissionPage'
import ApplicationsManagementPage from './features/missions/pages/ApplicationsManagementPage'
import MyApplicationsPage from './features/missions/pages/MyApplicationsPage'
import CompanyDashboard from './features/company/pages/CompanyDashboard'
import AgencyDashboard from './features/agency/pages/AgencyDashboard'
import CommercialDashboard from './features/commercial/pages/CommercialDashboard'
import ProtectedRoute from './features/auth/components/ProtectedRoute'

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
    return '/profile'
  }

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
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
      <Route
        path="/admin/groups"
        element={
          <ProtectedRoute requiredPermissions={['groups.manage']}>
            <GroupsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/profiles"
        element={
          <ProtectedRoute requiredPermissions={['profiles.manage']}>
            <ProfilesPage />
          </ProtectedRoute>
        }
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
        path="/admin/references"
        element={
          <ProtectedRoute requiredPermissions={['references.manage']}>
            <ReferencesManagementPage />
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
        path="/admin/iam/control"
        element={
          <ProtectedRoute requiredPermissions={['iam.groups.manage']}>
            <IAMControlPage />
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
      
      {/* Routes Offres - Intérimaires - IAM */}
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
          <ProtectedRoute requiredPermissions={['missions.browse']}>
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
          <ProtectedRoute requiredPermissions={['missions.create']}>
            <CompanyDashboard />
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
        path="/security"
        element={
          <ProtectedRoute>
            <SecuritySettingsPage />
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
      
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
