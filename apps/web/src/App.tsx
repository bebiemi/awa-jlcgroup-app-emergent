import { Routes, Route, Navigate } from 'react-router-dom'
import { useAppSelector } from './store/hooks'
import LoginPage from './features/auth/pages/LoginPage'
import RegisterPage from './features/auth/pages/RegisterPage'
import AdminDashboard from './features/admin/pages/AdminDashboard'
import ValidationsList from './features/admin/pages/ValidationsList'
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
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

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

      {/* Default redirects */}
      <Route
        path="/"
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
