import { Routes, Route, Navigate } from 'react-router-dom'
import { useAppSelector } from './store/hooks'
import { useInactivityLogout } from './hooks/useInactivityLogout'
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
import GroupsPage from './features/admin/pages/GroupsPage'
import ProfilesPage from './features/admin/pages/ProfilesPage'
import LocationManagementPage from './features/admin/pages/LocationManagementPage'
import InterimDashboard from './features/interim/pages/InterimDashboard'
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
import ProtectedRoute from './features/auth/components/ProtectedRoute'

function App() {
  const { isAuthenticated, user } = useAppSelector((state) => state.auth)
  
  // Auto-logout after 10 minutes of inactivity
  useInactivityLogout()

  // Redirect to role-specific dashboard
  const getDashboardPath = () => {
    if (!user) return '/login'
    if (user.roles.includes('admin')) return '/admin'
    if (user.roles.includes('interim')) return '/interimaire'
    if (user.roles.includes('company')) return '/entreprise'
    if (user.roles.includes('agency')) return '/agence'
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

      {/* Protected routes */}
      <Route
        path="/admin"
        element={
          <ProtectedRoute requiredRoles={['admin']}>
            <AdminDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/validations"
        element={
          <ProtectedRoute requiredRoles={['admin']}>
            <ValidationsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/users"
        element={
          <ProtectedRoute requiredRoles={['admin', 'super_admin']}>
            <UserManagementPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/users/new"
        element={
          <ProtectedRoute requiredRoles={['admin', 'super_admin']}>
            <CreateUserPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/groups"
        element={
          <ProtectedRoute requiredRoles={['admin', 'super_admin']}>
            <GroupsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/profiles"
        element={
          <ProtectedRoute requiredRoles={['admin', 'super_admin']}>
            <ProfilesPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/locations"
        element={
          <ProtectedRoute requiredRoles={['admin', 'super_admin']}>
            <LocationManagementPage />
          </ProtectedRoute>
        }
      />
      
      {/* Routes Missions - Admin & Commercial */}
      <Route
        path="/missions"
        element={
          <ProtectedRoute requiredRoles={['admin', 'super_admin', 'commercial', 'company']}>
            <MissionsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/missions/create"
        element={
          <ProtectedRoute requiredRoles={['admin', 'super_admin', 'commercial', 'company']}>
            <CreateMissionPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/missions/:id"
        element={
          <ProtectedRoute requiredRoles={['admin', 'super_admin', 'commercial', 'company']}>
            <MissionDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/missions/:id/edit"
        element={
          <ProtectedRoute requiredRoles={['admin', 'super_admin', 'commercial', 'company']}>
            <EditMissionPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/missions/:id/candidatures"
        element={
          <ProtectedRoute requiredRoles={['admin', 'super_admin', 'commercial']}>
            <ApplicationsManagementPage />
          </ProtectedRoute>
        }
      />
      
      {/* Routes Offres - Intérimaires */}
      <Route
        path="/offres"
        element={
          <ProtectedRoute requiredRoles={['interim']}>
            <OffresPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/offres/:id"
        element={
          <ProtectedRoute requiredRoles={['interim']}>
            <MissionDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/offres/:id/postuler"
        element={
          <ProtectedRoute requiredRoles={['interim']}>
            <ApplyMissionPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/mes-candidatures"
        element={
          <ProtectedRoute requiredRoles={['interim']}>
            <MyApplicationsPage />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/interimaire"
        element={
          <ProtectedRoute requiredRoles={['interim']}>
            <InterimDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/missions-interim"
        element={
          <ProtectedRoute requiredRoles={['interim']}>
            <Navigate to="/offres" replace />
          </ProtectedRoute>
        }
      />
      <Route
        path="/entreprise"
        element={
          <ProtectedRoute requiredRoles={['company']}>
            <CompanyDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/offres"
        element={
          <ProtectedRoute requiredRoles={['company']}>
            <Navigate to="/admin" replace />
          </ProtectedRoute>
        }
      />
      <Route
        path="/agence"
        element={
          <ProtectedRoute requiredRoles={['agency']}>
            <Navigate to="/admin" replace />
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
