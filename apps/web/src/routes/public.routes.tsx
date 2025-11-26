import LandingPage from '@/pages/LandingPage'
import LoginPage from '@/features/auth/pages/LoginPage'
import RegisterPage from '@/features/auth/pages/RegisterPage'
import VerifyEmailPage from '@/features/auth/pages/VerifyEmailPage'
import ForgotPasswordPage from '@/features/auth/pages/ForgotPasswordPage'
import ResetPasswordPage from '@/features/auth/pages/ResetPasswordPage'
import GoogleCallback from '@/features/auth/pages/GoogleCallback'
import RoleSelectionPage from '@/features/auth/pages/RoleSelectionPage'
import { AppRoute } from './types'

export const publicRoutes: AppRoute[] = [
  { path: '/', element: <LandingPage /> },
  { path: '/login', element: <LoginPage /> },
  { path: '/register', element: <RegisterPage /> },
  { path: '/verify-email', element: <VerifyEmailPage /> },
  { path: '/forgot-password', element: <ForgotPasswordPage /> },
  { path: '/reset-password', element: <ResetPasswordPage /> },
  { path: '/auth/google/callback', element: <GoogleCallback /> },
  { path: '/auth/role-selection', element: <RoleSelectionPage /> },
]
