import { useState } from 'react'
import { useResetUserMfaMutation } from '@/features/users/api/usersApi'
import toast from 'react-hot-toast'
import { XMarkIcon, ShieldExclamationIcon, ArrowPathIcon } from '@heroicons/react/24/outline'
import { usePermissions } from '@/hooks/usePermission'

interface ResetMfaModalProps {
  isOpen: boolean
  onClose: () => void
  user: {
    id: string
    username: string
    email: string
    full_name?: string
  }
}

export default function ResetMfaModal({ isOpen, onClose, user }: ResetMfaModalProps) {
  const [resetMfa, { isLoading }] = useResetUserMfaMutation()
  const [confirmed, setConfirmed] = useState(false)
  const { permissions } = usePermissions(['users.reset_mfa', 'users.manage'])

  const handleReset = async () => {
    if (!confirmed) {
      toast.error('Veuillez confirmer la réinitialisation')
      return
    }

    try {
      const result = await resetMfa(user.id).unwrap()
      toast.success(result.message || 'MFA réinitialisé avec succès')
      onClose()
      setConfirmed(false)
    } catch (error: any) {
      console.error('Reset MFA error:', error)
      toast.error(error?.data?.detail || 'Erreur lors de la réinitialisation du MFA')
    }
  }

  if (!isOpen) return null

  if (!(permissions['users.reset_mfa'] || permissions['users.manage'])) {
    return null
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-orange-100 rounded-lg">
              <ShieldExclamationIcon className="h-6 w-6 text-orange-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900">Réinitialiser MFA</h3>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        <div className="mb-6">
          <p className="text-sm text-gray-600 mb-4">
            Vous êtes sur le point de réinitialiser l'authentification à deux facteurs pour :
          </p>

          <div className="bg-gray-50 rounded-lg p-4 mb-4">
            <p className="font-semibold text-gray-900">{user.full_name || user.username}</p>
            <p className="text-sm text-gray-600">{user.email}</p>
          </div>

          <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-4">
            <p className="text-sm text-orange-800">
              <strong>Attention :</strong> Cette action va :
            </p>
            <ul className="mt-2 space-y-1 text-sm text-orange-700">
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <span>Désactiver toutes les méthodes MFA (TOTP, Email OTP)</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <span>Supprimer tous les secrets et codes de secours</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <span>Permettre à l'utilisateur de se connecter sans MFA</span>
              </li>
            </ul>
          </div>

          <label className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={confirmed}
              onChange={(e) => setConfirmed(e.target.checked)}
              className="w-4 h-4 text-orange-600 border-gray-300 rounded focus:ring-orange-500"
            />
            <span className="text-sm text-gray-700">
              Je confirme vouloir réinitialiser le MFA de cet utilisateur
            </span>
          </label>
        </div>

        <div className="flex space-x-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
          >
            Annuler
          </button>
          <button
            onClick={handleReset}
            disabled={!confirmed || isLoading}
            className="flex-1 bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {isLoading ? (
              <>
                <ArrowPathIcon className="w-5 h-5 mr-2 animate-spin" />
                Réinitialisation...
              </>
            ) : (
              'Réinitialiser MFA'
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
