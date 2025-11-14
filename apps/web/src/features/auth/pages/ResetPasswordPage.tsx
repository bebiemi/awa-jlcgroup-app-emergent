import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import { ArrowPathIcon, CheckCircleIcon, XCircleIcon, ShieldCheckIcon } from '@heroicons/react/24/outline'

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token')

  const [formData, setFormData] = useState({
    password: '',
    confirmPassword: '',
  })
  const [isLoading, setIsLoading] = useState(false)
  const [passwordMatch, setPasswordMatch] = useState<boolean | null>(null)
  const [showPassword, setShowPassword] = useState(false)

  // Real-time password match validation
  useEffect(() => {
    if (formData.password && formData.confirmPassword) {
      setPasswordMatch(formData.password === formData.confirmPassword)
    } else {
      setPasswordMatch(null)
    }
  }, [formData.password, formData.confirmPassword])

  const getPasswordStrength = (password: string) => {
    if (!password) return { strength: 0, label: '', color: '' }
    
    let strength = 0
    if (password.length >= 8) strength += 25
    if (password.length >= 12) strength += 25
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength += 25
    if (/\d/.test(password)) strength += 15
    if (/[^a-zA-Z0-9]/.test(password)) strength += 10
    
    if (strength < 40) return { strength, label: 'Faible', color: 'bg-red-500' }
    if (strength < 70) return { strength, label: 'Moyen', color: 'bg-yellow-500' }
    return { strength, label: 'Fort', color: 'bg-green-500' }
  }

  const passwordStrength = getPasswordStrength(formData.password)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!token) {
      toast.error('Token de réinitialisation invalide')
      return
    }

    if (formData.password !== formData.confirmPassword) {
      toast.error('Les mots de passe ne correspondent pas')
      return
    }

    if (formData.password.length < 8) {
      toast.error('Le mot de passe doit contenir au moins 8 caractères')
      return
    }

    setIsLoading(true)

    try {
      const response = await fetch('/api/auth/reset-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token,
          new_password: formData.password,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Échec de la réinitialisation')
      }

      toast.success('Mot de passe réinitialisé avec succès !')
      setTimeout(() => navigate('/login'), 2000)
    } catch (error: any) {
      console.error('Reset password error:', error)
      toast.error(error.message || 'Échec de la réinitialisation')
    } finally {
      setIsLoading(false)
    }
  }

  if (!token) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-jlc-purple-600 via-jlc-purple-700 to-jlc-purple-800 flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8 text-center">
          <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-6">
            <XCircleIcon className="h-10 w-10 text-red-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Lien invalide
          </h2>
          <p className="text-gray-600 mb-6">
            Le lien de réinitialisation est invalide ou a expiré.
          </p>
          <button
            onClick={() => navigate('/forgot-password')}
            className="inline-block bg-jlc-purple-600 text-white px-6 py-3 rounded-lg hover:bg-jlc-purple-700 transition font-medium"
          >
            Demander un nouveau lien
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-jlc-purple-600 via-jlc-purple-700 to-jlc-purple-800 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-2xl shadow-2xl overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-jlc-purple-600 to-jlc-purple-800 p-8 text-white text-center">
            <div className="mx-auto w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mb-4">
              <ShieldCheckIcon className="h-8 w-8" />
            </div>
            <h1 className="text-2xl font-bold mb-2">
              Nouveau mot de passe
            </h1>
            <p className="text-purple-100 text-sm">
              Choisissez un mot de passe sécurisé
            </p>
          </div>

          <div className="p-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Password */}
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                  Nouveau mot de passe
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    id="password"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent transition"
                    placeholder="••••••••"
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
                {formData.password && (
                  <div className="mt-2">
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="text-gray-600">Force du mot de passe</span>
                      <span className={`font-medium ${
                        passwordStrength.strength < 40 ? 'text-red-600' :
                        passwordStrength.strength < 70 ? 'text-yellow-600' : 'text-green-600'
                      }`}>
                        {passwordStrength.label}
                      </span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div 
                        className={`h-full transition-all ${passwordStrength.color}`}
                        style={{ width: `${passwordStrength.strength}%` }}
                      ></div>
                    </div>
                  </div>
                )}
              </div>

              {/* Confirm Password */}
              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
                  Confirmer le mot de passe
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    id="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                    className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent transition ${
                      passwordMatch === false ? 'border-red-500' : 
                      passwordMatch === true ? 'border-green-500' : 'border-gray-300'
                    }`}
                    placeholder="••••••••"
                    required
                  />
                  {passwordMatch !== null && (
                    <div className="absolute right-3 top-1/2 -translate-y-1/2">
                      {passwordMatch ? (
                        <CheckCircleIcon className="h-5 w-5 text-green-500" />
                      ) : (
                        <XCircleIcon className="h-5 w-5 text-red-500" />
                      )}
                    </div>
                  )}
                </div>
                {passwordMatch === false && (
                  <p className="text-red-500 text-sm mt-1 flex items-center">
                    <XCircleIcon className="h-4 w-4 mr-1" />
                    Les mots de passe ne correspondent pas
                  </p>
                )}
                {passwordMatch === true && (
                  <p className="text-green-500 text-sm mt-1 flex items-center">
                    <CheckCircleIcon className="h-4 w-4 mr-1" />
                    Les mots de passe correspondent
                  </p>
                )}
              </div>

              {/* Security Tips */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-blue-900 mb-2">
                  Conseils de sécurité :
                </h4>
                <ul className="text-xs text-blue-800 space-y-1">
                  <li>• Au moins 8 caractères</li>
                  <li>• Mélange de majuscules et minuscules</li>
                  <li>• Au moins un chiffre</li>
                  <li>• Au moins un caractère spécial</li>
                </ul>
              </div>

              <button
                type="submit"
                disabled={isLoading || !passwordMatch}
                className="w-full bg-gradient-to-r from-jlc-purple-600 to-jlc-purple-800 text-white py-3 rounded-lg hover:from-jlc-purple-700 hover:to-jlc-purple-900 transition-all font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center shadow-lg"
              >
                {isLoading ? (
                  <>
                    <ArrowPathIcon className="w-5 h-5 mr-2 animate-spin" />
                    Réinitialisation...
                  </>
                ) : (
                  'Réinitialiser le mot de passe'
                )}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}
