import { Routes, Route, Navigate } from 'react-router-dom'
import { useAppSelector } from './store/hooks'
import LandingPage from './pages/LandingPage'
import LoginPage from './features/auth/pages/LoginPage'
import RegisterPage from './features/auth/pages/RegisterPage'
import ForgotPasswordPage from './features/auth/pages/ForgotPasswordPage'
import ResetPasswordPage from './features/auth/pages/ResetPasswordPage'
import GoogleCallback from './features/auth/pages/GoogleCallback'
import RoleSelectionPage from './features/auth/pages/RoleSelectionPage'
import AdminDashboard from './features/admin/pages/AdminDashboard'
import ValidationsList from './features/admin/pages/ValidationsList'
import UserManagementPage from './features/admin/pages/UserManagementPage'
import GroupsPage from './features/admin/pages/GroupsPage'
import InterimDashboard from './features/interim/pages/InterimDashboard'
import ProfilePage from './features/profile/pages/ProfilePage'
import ProtectedRoute from './features/auth/components/ProtectedRoute'

function App() {
  const { isAuthenticated, user } = useAppSelector((state) => state.auth)

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
            <ValidationsList />
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
        path="/interimaire"
        element={
          <ProtectedRoute requiredRoles={['interim']}>
            <InterimDashboard />
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
