/**
 * Email Verification Banner
 * Shows alert banner for unverified users
 * Feature Flag: feature.validation.email
 */
import { useState, useEffect } from 'react'
import { useAppSelector } from '@/store/hooks'
import { ExclamationTriangleIcon, XMarkIcon, PaperAirplaneIcon } from '@heroicons/react/24/outline'
import { toast } from 'react-hot-toast'

export default function EmailVerificationBanner() {
  const { user } = useAppSelector((state) => state.auth)
  const [isVisible, setIsVisible] = useState(false)
  const [verificationStatus, setVerificationStatus] = useState<any>(null)
  const [isSending, setIsSending] = useState(false)

  useEffect(() => {
    const checkStatus = async () => {
      if (!user) return

      try {
        const token = localStorage.getItem('access_token')
        const response = await fetch('/api/email-verification/status', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        })

        if (response.ok) {
          const data = await response.json()
          setVerificationStatus(data)
          
          // Show banner if verification is required and not verified
          if (data.verification_required && !data.is_verified) {
            setIsVisible(true)
          }
        }
      } catch (error) {
        console.error('Error checking verification status:', error)
      }
    }

    checkStatus()
  }, [user])

  const handleSendVerification = async () => {
    setIsSending(true)
    
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/email-verification/send', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      const data = await response.json()

      if (response.ok) {
        toast.success('Email de vérification envoyé ! Vérifiez votre boîte de réception.')
        
        // Update status
        setVerificationStatus({
          ...verificationStatus,
          pending_verification: true,
          can_resend: false
        })
      } else {
        toast.error(data.detail || 'Erreur lors de l\'envoi')
      }
    } catch (error) {
      toast.error('Erreur de connexion')
    } finally {
      setIsSending(false)
    }
  }

  const handleResend = async () => {
    setIsSending(true)
    
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/email-verification/resend', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      const data = await response.json()

      if (response.ok) {
        toast.success('Nouvel email envoyé !')
        setVerificationStatus({
          ...verificationStatus,
          can_resend: false
        })
      } else if (response.status === 429) {
        toast.error('Veuillez attendre 5 minutes avant de renvoyer')
      } else {
        toast.error(data.detail || 'Erreur')
      }
    } catch (error) {
      toast.error('Erreur de connexion')
    } finally {
      setIsSending(false)
    }
  }

  if (!isVisible || !verificationStatus) {
    return null
  }

  return (
    <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 relative">
      <div className="flex">
        <div className="flex-shrink-0">
          <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" />
        </div>
        <div className="ml-3 flex-1">
          <p className="text-sm text-yellow-800">
            <span className="font-medium">Vérification d'email requise.</span>{' '}
            Pour accéder à toutes les fonctionnalités, veuillez vérifier votre adresse email{' '}
            <span className="font-semibold">{verificationStatus.email}</span>.
          </p>
          <div className="mt-2 flex items-center gap-3">
            {!verificationStatus.pending_verification ? (
              <button
                onClick={handleSendVerification}
                disabled={isSending}
                className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-yellow-800 bg-yellow-100 hover:bg-yellow-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500 disabled:opacity-50"
              >
                <PaperAirplaneIcon className="h-4 w-4 mr-1" />
                {isSending ? 'Envoi...' : 'Envoyer l\'email de vérification'}
              </button>
            ) : (
              <>
                <span className="text-xs text-yellow-700">
                  Email envoyé. Vérifiez votre boîte de réception.
                </span>
                {verificationStatus.can_resend && (
                  <button
                    onClick={handleResend}
                    disabled={isSending}
                    className="text-xs font-medium text-yellow-800 hover:text-yellow-900 underline"
                  >
                    {isSending ? 'Envoi...' : 'Renvoyer'}
                  </button>
                )}
              </>
            )}
          </div>
        </div>
        <div className="ml-auto pl-3">
          <button
            onClick={() => setIsVisible(false)}
            className="inline-flex text-yellow-400 hover:text-yellow-500 focus:outline-none"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  )
}
