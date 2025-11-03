import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCompleteMfaLoginMutation } from '../api/mfaApi'
import toast from 'react-hot-toast'
import Button from '@/components/Button'
import { ShieldCheckIcon, ArrowPathIcon, KeyIcon } from '@heroicons/react/24/outline'

interface MfaVerificationPageProps {
  sessionId: string
  mfaMethod: 'totp' | 'email'
  onBack: () => void
}

export default function MfaVerificationPage({ sessionId, mfaMethod, onBack }: MfaVerificationPageProps) {
  const [code, setCode] = useState('')
  const [codeType, setCodeType] = useState<'totp' | 'email' | 'backup'>(mfaMethod)
  const [completeMfaLogin, { isLoading }] = useCompleteMfaLoginMutation()
  const [attemptsRemaining, setAttemptsRemaining] = useState(3)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!code.trim()) {
      toast.error('Veuillez entrer le code')
      return
    }

    try {
      const result = await completeMfaLogin({
        session_token: sessionId,
        code: code.trim(),
        method: codeType,
      }).unwrap()

      if (result.success && result.access_token && result.user) {
        toast.success('Authentification réussie!')

        // Redirect to appropriate dashboard based on user role
        const userRoles = result.user?.roles || []
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
      } else {
        toast.error(result.message || 'Code invalide')
        setAttemptsRemaining((prev) => prev - 1)
      }
    } catch (error: any) {
      console.error('MFA verification error:', error)
      const errorMessage = error?.data?.message || error?.data?.detail || 'Code invalide'
      toast.error(errorMessage)

      if (error?.data?.attempts_remaining !== undefined) {
        setAttemptsRemaining(error.data.attempts_remaining)
      } else {
        setAttemptsRemaining((prev) => Math.max(0, prev - 1))
      }

      if (attemptsRemaining <= 1) {
        toast.error('Trop de tentatives. Veuillez recommencer la connexion.')
        setTimeout(() => onBack(), 2000)
      }
    }
  }

  const getMethodTitle = () => {
    switch (codeType) {
      case 'totp':
        return 'Code Authenticator'
      case 'email':
        return 'Code Email'
      case 'backup':
        return 'Code de Secours'
      default:
        return 'Code de Vérification'
    }
  }

  const getMethodDescription = () => {
    switch (codeType) {
      case 'totp':
        return "Entrez le code à 6 chiffres de votre application d'authentification"
      case 'email':
        return 'Entrez le code à 6 chiffres envoyé à votre email'
      case 'backup':
        return 'Entrez un de vos codes de secours'
      default:
        return 'Entrez votre code de vérification'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-jlc-purple-600 via-jlc-purple-700 to-jlc-purple-800 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-2xl shadow-2xl overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-jlc-purple-600 to-jlc-purple-800 p-8 text-white text-center">
            <div className="flex justify-center mb-4">
              <ShieldCheckIcon className="h-16 w-16" />
            </div>
            <h1 className="text-2xl font-bold mb-2">Authentification à Deux Facteurs</h1>
            <p className="text-purple-100 text-sm">{getMethodDescription()}</p>
          </div>

          <div className="p-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Code Type Selector */}
              <div className="flex gap-2 mb-4">
                <button
                  type="button"
                  onClick={() => setCodeType(mfaMethod)}
                  className={`flex-1 px-3 py-2 rounded-lg text-sm font-medium transition ${
                    codeType === mfaMethod
                      ? 'bg-jlc-purple-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {mfaMethod === 'totp' ? 'Authenticator' : 'Email'}
                </button>
                <button
                  type="button"
                  onClick={() => setCodeType('backup')}
                  className={`flex-1 px-3 py-2 rounded-lg text-sm font-medium transition ${
                    codeType === 'backup'
                      ? 'bg-jlc-purple-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Code de Secours
                </button>
              </div>

              {/* Code Input */}
              <div>
                <label htmlFor="code" className="block text-sm font-medium text-gray-700 mb-2">
                  {getMethodTitle()}
                </label>
                <div className="relative">
                  <input
                    type="text"
                    id="code"
                    value={code}
                    onChange={(e) => setCode(e.target.value.replace(/[^0-9A-Za-z-]/g, ''))}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent transition font-mono text-center text-lg tracking-wider"
                    placeholder={codeType === 'backup' ? 'XXXX-XXXX-XXXX' : '123456'}
                    maxLength={codeType === 'backup' ? 14 : 6}
                    required
                    autoComplete="off"
                    autoFocus
                  />
                  <KeyIcon className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                </div>
              </div>

              {/* Attempts Remaining */}
              {attemptsRemaining < 3 && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                  <p className="text-sm text-yellow-800 text-center">
                    <span className="font-semibold">Attention:</span> {attemptsRemaining} tentative
                    {attemptsRemaining > 1 ? 's' : ''} restante{attemptsRemaining > 1 ? 's' : ''}
                  </p>
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-gradient-to-r from-jlc-purple-600 to-jlc-purple-800 text-white py-3 rounded-lg hover:from-jlc-purple-700 hover:to-jlc-purple-900 transition-all font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center shadow-lg"
              >
                {isLoading ? (
                  <>
                    <ArrowPathIcon className="w-5 h-5 mr-2 animate-spin" />
                    Vérification...
                  </>
                ) : (
                  'Vérifier'
                )}
              </button>
            </form>

            {/* Help Text */}
            <div className="mt-6 space-y-3">
              {codeType === 'email' && (
                <p className="text-sm text-gray-600 text-center">
                  Vous n'avez pas reçu de code ? Vérifiez votre dossier spam ou attendez quelques minutes.
                </p>
              )}

              {codeType === 'totp' && (
                <p className="text-sm text-gray-600 text-center">
                  Assurez-vous que l'heure de votre appareil est correctement synchronisée.
                </p>
              )}

              {codeType === 'recovery' && (
                <p className="text-sm text-gray-600 text-center">
                  Chaque code de secours ne peut être utilisé qu'une seule fois.
                </p>
              )}

              {/* Back Button */}
              <button
                type="button"
                onClick={onBack}
                className="w-full text-jlc-purple-600 hover:text-jlc-purple-700 font-medium text-sm py-2"
              >
                ← Retour à la connexion
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
