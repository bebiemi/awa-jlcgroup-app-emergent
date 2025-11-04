import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useLocalLoginMutation } from '../api/authApi'
import { useAppSelector } from '@/store/hooks'
import toast from 'react-hot-toast'
import Button from '@/components/Button'
import { ArrowPathIcon, ShieldCheckIcon } from '@heroicons/react/24/outline'
import MfaVerificationPage from './MfaVerificationPage'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [login, { isLoading }] = useLocalLoginMutation()
  const [googleLoading, setGoogleLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showMfaVerification, setShowMfaVerification] = useState(false)
  const [mfaSessionId, setMfaSessionId] = useState('')
  const [mfaMethod, setMfaMethod] = useState<'totp' | 'email'>('totp')
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const result = await login({ username, password }).unwrap()

      // Check if MFA is required
      if (result.mfa_required && result.mfa_session_token) {
        // Show MFA verification page
        setMfaSessionId(result.mfa_session_token)
        // Use first available method or default to totp
        const firstMethod = result.available_methods?.[0] || 'totp'
        setMfaMethod(firstMethod === 'backup' ? 'totp' : firstMethod as 'totp' | 'email')
        setShowMfaVerification(true)
        toast.success('Veuillez entrer votre code de vérification')
        return
      }

      // Normal login without MFA
      if (result.access_token && result.user) {
        toast.success('Connexion réussie!')

        // Redirect to appropriate dashboard based on user role
        const userRoles = result.user?.roles || []
        let dashboardPath = '/profile'

        if (userRoles.includes('admin') || userRoles.includes('super_admin')) {
          dashboardPath = '/admin'
        } else if (userRoles.includes('commercial')) {
          dashboardPath = '/commercial'
        } else if (userRoles.includes('interim')) {
          dashboardPath = '/interimaire'
        } else if (userRoles.includes('company')) {
          dashboardPath = '/entreprise'
        } else if (userRoles.includes('agency')) {
          dashboardPath = '/agence'
        }

        navigate(dashboardPath, { replace: true })
      }
    } catch (error: any) {
      console.error('Login error:', error)
      toast.error(error?.data?.detail || 'Identifiants incorrects')
    }
  }

  const handleBackFromMfa = () => {
    setShowMfaVerification(false)
    setMfaSessionId('')
    setPassword('')
  }

  const handleGoogleLogin = async () => {
    setGoogleLoading(true)
    
    try {
      const response = await fetch('/auth-api/auth/google/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          redirect_uri: `${window.location.origin}/auth/google/callback`,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Échec de l\'initialisation Google OAuth')
      }

      const data = await response.json()
      window.location.href = data.authorization_url
    } catch (error: any) {
      console.error('Google login error:', error)
      toast.error(error.message || 'Échec de l\'initialisation Google OAuth')
      setGoogleLoading(false)
    }
  }

  // Show MFA verification page if needed
  if (showMfaVerification) {
    return (
      <MfaVerificationPage
        sessionId={mfaSessionId}
        mfaMethod={mfaMethod}
        onBack={handleBackFromMfa}
      />
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-jlc-purple-600 via-jlc-purple-700 to-jlc-purple-800 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        {/* Card */}
        <div className="bg-white rounded-2xl shadow-2xl overflow-hidden">
          {/* Header with gradient */}
          <div className="bg-gradient-to-r from-jlc-purple-600 to-jlc-purple-800 p-8 text-white text-center">
            <div className="flex justify-center mb-4">
              <img 
                src="/logo-jlc.png" 
                alt="JLC GROUP" 
                className="h-20 w-auto object-contain"
              />
            </div>
            <p className="text-purple-100">
              Connectez-vous à votre espace
            </p>
          </div>

          <div className="p-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Username */}
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                  Nom d'utilisateur
                </label>
                <input
                  type="text"
                  id="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent transition"
                  placeholder="Votre nom d'utilisateur"
                  required
                />
              </div>

              {/* Password */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                    Mot de passe
                  </label>
                  <Link
                    to="/forgot-password"
                    className="text-sm text-jlc-purple-600 hover:text-jlc-purple-700 font-medium"
                  >
                    Mot de passe oublié ?
                  </Link>
                </div>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    id="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent transition"
                    placeholder="Votre mot de passe"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? '🙈' : '👁️'}
                  </button>
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-gradient-to-r from-jlc-purple-600 to-jlc-purple-800 text-white py-3 rounded-lg hover:from-jlc-purple-700 hover:to-jlc-purple-900 transition-all font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center shadow-lg"
              >
                {isLoading ? (
                  <>
                    <ArrowPathIcon className="w-5 h-5 mr-2 animate-spin" />
                    Connexion...
                  </>
                ) : (
                  'Se connecter'
                )}
              </button>
            </form>

            {/* Divider */}
            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-white text-gray-500">Ou continuer avec</span>
              </div>
            </div>

            {/* Social Login Buttons */}
            <div className="space-y-3">
              {/* Google */}
              <button
                type="button"
                onClick={handleGoogleLogin}
                disabled={googleLoading}
                className="w-full flex items-center justify-center px-4 py-3 border-2 border-gray-300 rounded-lg hover:border-gray-400 hover:bg-gray-50 transition-all font-medium text-gray-700 disabled:opacity-50"
              >
                {googleLoading ? (
                  <>
                    <ArrowPathIcon className="w-5 h-5 mr-2 animate-spin" />
                    Redirection...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24">
                      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                    </svg>
                    Se connecter avec Google
                  </>
                )}
              </button>

              {/* Microsoft (Coming Soon) */}
              <button
                type="button"
                disabled
                className="w-full flex items-center justify-center px-4 py-3 border-2 border-gray-200 rounded-lg bg-gray-50 cursor-not-allowed font-medium text-gray-400"
              >
                <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24">
                  <path fill="#f25022" d="M0 0h11v11H0z"/>
                  <path fill="#00a4ef" d="M13 0h11v11H13z"/>
                  <path fill="#7fba00" d="M0 13h11v11H0z"/>
                  <path fill="#ffb900" d="M13 13h11v11H13z"/>
                </svg>
                Microsoft (Bientôt disponible)
              </button>

              {/* Facebook (Coming Soon) */}
              <button
                type="button"
                disabled
                className="w-full flex items-center justify-center px-4 py-3 border-2 border-gray-200 rounded-lg bg-gray-50 cursor-not-allowed font-medium text-gray-400"
              >
                <svg className="w-5 h-5 mr-3" fill="#1877F2" viewBox="0 0 24 24">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
                Facebook (Bientôt disponible)
              </button>
            </div>

            {/* Info Box */}
            <div className="mt-6 p-4 bg-purple-50 border border-purple-200 rounded-lg">
              <div className="flex items-start">
                <ShieldCheckIcon className="h-5 w-5 text-jlc-purple-600 mr-2 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-gray-700">
                  <span className="font-semibold">Sécurité renforcée :</span> Activez l'authentification à deux facteurs après votre première connexion.
                </p>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="px-8 pb-8 text-center border-t pt-6">
            <p className="text-sm text-gray-600">
              Vous n'avez pas de compte ?{' '}
              <Link
                to="/register"
                className="text-jlc-purple-600 hover:text-jlc-purple-700 font-semibold"
              >
                S'inscrire gratuitement
              </Link>
            </p>
            <p className="text-xs text-gray-500 mt-3">
              Identifiants par défaut: <span className="font-mono bg-gray-100 px-2 py-1 rounded">admin</span> / <span className="font-mono bg-gray-100 px-2 py-1 rounded">awana2025</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
