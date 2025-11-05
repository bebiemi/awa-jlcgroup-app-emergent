import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAppDispatch } from '@/store/hooks'
import { setCredentials } from '../slices/authSlice'
import { useRoles, useUserStatuses } from '@/hooks/useAppConfig'
import toast from 'react-hot-toast'

export default function GoogleCallback() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const dispatch = useAppDispatch()
  const roles = useRoles()
  const userStatuses = useUserStatuses()

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code')
      const state = searchParams.get('state')
      const error = searchParams.get('error')

      // Check for errors
      if (error) {
        console.error('Google OAuth error:', error)
        toast.error(`Échec de la connexion Google: ${error}`)
        navigate('/login')
        return
      }

      if (!code || !state) {
        console.error('Missing code or state')
        toast.error('Paramètres OAuth manquants')
        navigate('/login')
        return
      }

      try {
        // Call backend to exchange code for tokens
        const redirectUri = `${window.location.origin}/auth/google/callback`
        
        const response = await fetch('/auth-api/auth/google/callback', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            code,
            state,
            redirect_uri: redirectUri,
          }),
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.detail || 'Authentification échouée')
        }

        const data = await response.json()

        // Check if this is a new user (needs role selection)
        if (data.user.status === userStatuses.pending && data.user.roles.length === 1 && data.user.roles[0] === roles.interim) {
          // This is a new user with default role, redirect to role selection
          navigate('/auth/role-selection', {
            state: {
              userData: data.user,
              tempToken: data.access_token,
            },
          })
          return
        }

        // Store credentials in Redux
        dispatch(
          setCredentials({
            user: data.user,
            token: data.access_token,
            refreshToken: data.refresh_token,
          })
        )

        toast.success(`Bienvenue, ${data.user.full_name || data.user.username}!`)

        // Redirect to appropriate dashboard based on user role
        const userRoles = data.user.roles || []
        let dashboardPath = '/profile'
        
        if (userRoles.includes('admin') || userRoles.includes('super_admin')) {
          dashboardPath = '/admin'
        } else if (userRoles.includes('interim')) {
          dashboardPath = '/interimaire'
        } else if (userRoles.includes('company')) {
          dashboardPath = '/entreprise'
        } else if (userRoles.includes('agency')) {
          dashboardPath = '/agence'
        }
        
        navigate(dashboardPath, { replace: true })
      } catch (error: any) {
        console.error('Google callback error:', error)
        toast.error(error.message || 'Échec de la connexion Google')
        navigate('/login')
      }
    }

    handleCallback()
  }, [searchParams, navigate, dispatch])

  return (
    <div className="min-h-screen bg-gradient-to-br from-jlc-purple-600 via-jlc-purple-700 to-jlc-purple-800 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-2xl p-8 max-w-md w-full">
        <div className="flex flex-col items-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-jlc-purple-600 mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-900">
            Connexion en cours...
          </h2>
          <p className="text-sm text-gray-500 mt-2 text-center">
            Authentification avec Google en cours, veuillez patienter.
          </p>
        </div>
      </div>
    </div>
  )
}
