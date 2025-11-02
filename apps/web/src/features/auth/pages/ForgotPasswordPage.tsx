import { useState } from 'react'
import { Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import { ArrowPathIcon, CheckCircleIcon, EnvelopeIcon } from '@heroicons/react/24/outline'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [emailSent, setEmailSent] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const response = await fetch('/auth-api/auth/forgot-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Échec de l\'envoi de l\'email')
      }

      setEmailSent(true)
      toast.success('Email de réinitialisation envoyé !')
    } catch (error: any) {
      console.error('Forgot password error:', error)
      toast.error(error.message || 'Échec de l\'envoi de l\'email')
    } finally {
      setIsLoading(false)
    }
  }

  if (emailSent) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-jlc-purple-600 via-jlc-purple-700 to-jlc-purple-800 flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8 text-center">
          <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-6">
            <CheckCircleIcon className="h-10 w-10 text-green-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Email envoyé !
          </h2>
          <p className="text-gray-600 mb-6">
            Nous avons envoyé un lien de réinitialisation à <span className="font-semibold">{email}</span>.
            Vérifiez votre boîte de réception et vos spams.
          </p>
          <Link
            to="/login"
            className="inline-block bg-jlc-purple-600 text-white px-6 py-3 rounded-lg hover:bg-jlc-purple-700 transition font-medium"
          >
            Retour à la connexion
          </Link>
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
              <EnvelopeIcon className="h-8 w-8" />
            </div>
            <h1 className="text-2xl font-bold mb-2">
              Mot de passe oublié ?
            </h1>
            <p className="text-purple-100 text-sm">
              Pas de souci, nous vous enverrons un lien de réinitialisation
            </p>
          </div>

          <div className="p-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                  Adresse email
                </label>
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent transition"
                  placeholder="votre@email.com"
                  required
                />
                <p className="mt-2 text-sm text-gray-500">
                  Entrez l'email associé à votre compte
                </p>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-gradient-to-r from-jlc-purple-600 to-jlc-purple-800 text-white py-3 rounded-lg hover:from-jlc-purple-700 hover:to-jlc-purple-900 transition-all font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center shadow-lg"
              >
                {isLoading ? (
                  <>
                    <ArrowPathIcon className="w-5 h-5 mr-2 animate-spin" />
                    Envoi en cours...
                  </>
                ) : (
                  'Envoyer le lien de réinitialisation'
                )}
              </button>
            </form>
          </div>

          {/* Footer */}
          <div className="px-8 pb-8 text-center border-t pt-6">
            <Link
              to="/login"
              className="text-sm text-jlc-purple-600 hover:text-jlc-purple-700 font-medium"
            >
              ← Retour à la connexion
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
