import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAppDispatch } from '@/store/hooks'
import { setCredentials } from '../slices/authSlice'
import toast from 'react-hot-toast'
import { ArrowPathIcon } from '@heroicons/react/24/outline'

type UserRole = 'interim' | 'company'

export default function RoleSelectionPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const dispatch = useAppDispatch()
  const [selectedRole, setSelectedRole] = useState<UserRole | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  // Get user data from location state (passed from GoogleCallback)
  const userData = location.state?.userData
  const tempToken = location.state?.tempToken

  if (!userData || !tempToken) {
    // Redirect to login if no user data
    navigate('/login')
    return null
  }

  const handleRoleSelect = (role: UserRole) => {
    setSelectedRole(role)
  }

  const handleSubmit = async () => {
    if (!selectedRole) {
      toast.error('Veuillez choisir un type de profil')
      return
    }

    setIsLoading(true)

    try {
      // Call backend to update user role
      const response = await fetch('/auth-api/auth/google/complete-registration', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${tempToken}`,
        },
        body: JSON.stringify({
          role: selectedRole,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Échec de l\'enregistrement')
      }

      const data = await response.json()

      // Store credentials in Redux
      dispatch(
        setCredentials({
          user: data.user,
          token: data.access_token,
          refreshToken: data.refresh_token,
        })
      )

      toast.success('Inscription terminée avec succès !')
      navigate('/')
    } catch (error: any) {
      console.error('Role selection error:', error)
      toast.error(error.message || 'Échec de la sélection du rôle')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-jlc-purple-600 via-jlc-purple-700 to-jlc-purple-800 flex items-center justify-center px-4">
      <div className="max-w-2xl w-full bg-white rounded-lg shadow-2xl p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-jlc-purple-800 mb-2">
            JLC GROUP ⭐
          </h1>
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">
            Bienvenue, {userData.full_name || userData.username} !
          </h2>
          <p className="text-gray-600">
            Pour terminer votre inscription, veuillez choisir votre type de profil
          </p>
        </div>

        {/* Role Selection */}
        <div className="mb-8">
          <label className="block text-sm font-medium text-gray-700 mb-4 text-center">
            Type de profil *
          </label>
          <div className="grid grid-cols-2 gap-6">
            {/* Interim Role */}
            <button
              type="button"
              onClick={() => handleRoleSelect('interim')}
              disabled={isLoading}
              className={`p-6 border-2 rounded-lg transition-all ${
                selectedRole === 'interim'
                  ? 'border-jlc-purple-600 bg-jlc-purple-50 ring-2 ring-jlc-purple-500'
                  : 'border-gray-300 hover:border-jlc-purple-400 bg-white'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              <div className="text-center">
                <div className="text-5xl mb-3">👤</div>
                <div className="font-semibold text-gray-900 text-lg mb-2">
                  Intérimaire
                </div>
                <div className="text-sm text-gray-500">
                  Je recherche des missions
                </div>
              </div>
            </button>

            {/* Company Role */}
            <button
              type="button"
              onClick={() => handleRoleSelect('company')}
              disabled={isLoading}
              className={`p-6 border-2 rounded-lg transition-all ${
                selectedRole === 'company'
                  ? 'border-jlc-purple-600 bg-jlc-purple-50 ring-2 ring-jlc-purple-500'
                  : 'border-gray-300 hover:border-jlc-purple-400 bg-white'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              <div className="text-center">
                <div className="text-5xl mb-3">🏢</div>
                <div className="font-semibold text-gray-900 text-lg mb-2">
                  Société
                </div>
                <div className="text-sm text-gray-500">
                  Je propose des missions
                </div>
              </div>
            </button>
          </div>
        </div>

        {/* Submit Button */}
        <button
          onClick={handleSubmit}
          disabled={!selectedRole || isLoading}
          className="w-full bg-jlc-purple-600 text-white py-3 rounded-md hover:bg-jlc-purple-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
        >
          {isLoading ? (
            <>
              <ArrowPathIcon className="w-5 h-5 mr-2 animate-spin" />
              Finalisation en cours...
            </>
          ) : (
            'Continuer'
          )}
        </button>

        {/* User Info */}
        <div className="mt-6 p-4 bg-gray-50 rounded-md">
          <p className="text-sm text-gray-600 text-center">
            Connecté avec : <span className="font-medium text-gray-900">{userData.email}</span>
          </p>
        </div>
      </div>
    </div>
  )
}
