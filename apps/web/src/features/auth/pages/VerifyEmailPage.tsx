/**
 * Email Verification Page
 * Handles email verification via token from email link
 */
import { useEffect, useState } from 'react'
import { useSearchParams, useNavigate, Link } from 'react-router-dom'
import Card from '@/components/Card'
import { CheckCircleIcon, XCircleIcon, ArrowPathIcon } from '@heroicons/react/24/outline'

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('')
  const token = searchParams.get('token')

  useEffect(() => {
    const verifyEmail = async () => {
      if (!token) {
        setStatus('error')
        setMessage('Token de vérification manquant')
        return
      }

      try {
        const response = await fetch('/api/email-verification/verify', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ token }),
        })

        const data = await response.json()

        if (response.ok) {
          setStatus('success')
          setMessage('Votre email a été vérifié avec succès !')
          
          // Redirect to login after 3 seconds
          setTimeout(() => {
            navigate('/login')
          }, 3000)
        } else {
          setStatus('error')
          setMessage(data.detail || 'Erreur lors de la vérification')
        }
      } catch (error) {
        setStatus('error')
        setMessage('Erreur de connexion au serveur')
      }
    }

    verifyEmail()
  }, [token, navigate])

  return (
    <div className="min-h-screen bg-gradient-to-br from-jlc-purple-600 via-jlc-indigo-dark to-jlc-neon-pink-600 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <div className="text-center p-8">
          {status === 'loading' && (
            <>
              <ArrowPathIcon className="h-16 w-16 text-jlc-purple-600 animate-spin mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Vérification en cours...
              </h2>
              <p className="text-gray-600">
                Veuillez patienter pendant la vérification de votre email.
              </p>
            </>
          )}

          {status === 'success' && (
            <>
              <CheckCircleIcon className="h-16 w-16 text-green-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Email vérifié ! ✓
              </h2>
              <p className="text-gray-600 mb-4">{message}</p>
              <p className="text-sm text-gray-500">
                Redirection vers la page de connexion...
              </p>
            </>
          )}

          {status === 'error' && (
            <>
              <XCircleIcon className="h-16 w-16 text-red-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Erreur de vérification
              </h2>
              <p className="text-red-600 mb-6">{message}</p>
              <div className="space-y-3">
                <Link
                  to="/login"
                  className="block w-full px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 transition"
                >
                  Retour à la connexion
                </Link>
                <p className="text-sm text-gray-600">
                  Besoin d'aide ?{' '}
                  <a href="mailto:support@jlcgroup.ga" className="text-jlc-purple-600 hover:underline">
                    Contactez le support
                  </a>
                </p>
              </div>
            </>
          )}
        </div>
      </Card>
    </div>
  )
}
