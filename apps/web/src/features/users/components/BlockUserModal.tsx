import { useState } from 'react'
import { XMarkIcon, NoSymbolIcon, CheckCircleIcon } from '@heroicons/react/24/outline'
import { useUpdateUserStatusMutation, type User } from '@/features/users/api/usersApi'
import { usePermissions } from '@/hooks/usePermission'

interface BlockUserModalProps {
  user: User
  isOpen: boolean
  onClose: () => void
}

export default function BlockUserModal({ user, isOpen, onClose }: BlockUserModalProps) {
  const [updateStatus, { isLoading }] = useUpdateUserStatusMutation()
  const { permissions } = usePermissions(['users.manage_status', 'users.manage'])
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  const isSuspended = user.status === 'suspended'
  const action = isSuspended ? 'unblock' : 'block'
  const newStatus = isSuspended ? 'active' : 'suspended'

  const handleStatusChange = async () => {
    setError('')

    try {
      await updateStatus({
        user_id: user.id,
        status: newStatus,
      }).unwrap()

      setSuccess(true)
      setTimeout(() => {
        onClose()
      }, 1500)
    } catch (err: any) {
      setError(err?.data?.detail || 'Erreur lors de la modification du statut')
    }
  }

  if (!isOpen) return null

  const canManageStatus = permissions['users.manage_status'] || permissions['users.manage']
  if (!canManageStatus) {
    return null
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        {/* Backdrop */}
        <div className="fixed inset-0 bg-black bg-opacity-50 transition-opacity" onClick={onClose} />

        {/* Modal */}
        <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full p-6 z-10">
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div
                className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                  isSuspended ? 'bg-green-100' : 'bg-orange-100'
                }`}
              >
                {isSuspended ? (
                  <CheckCircleIcon className="h-6 w-6 text-green-600" />
                ) : (
                  <NoSymbolIcon className="h-6 w-6 text-orange-600" />
                )}
              </div>
              <h3 className="text-xl font-semibold text-gray-900">
                {isSuspended ? 'Débloquer' : 'Bloquer'} l'utilisateur
              </h3>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500 transition-colors"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          {/* Content */}
          <div className="space-y-4">
            {isSuspended ? (
              <>
                <p className="text-gray-600">
                  Êtes-vous sûr de vouloir débloquer l'utilisateur{' '}
                  <span className="font-semibold">{user.full_name || user.username}</span> (
                  {user.email})?
                </p>

                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <p className="text-sm text-green-800">
                    <strong>✓ Déblocage :</strong> L'utilisateur pourra à nouveau se connecter et
                    accéder à la plateforme.
                  </p>
                </div>
              </>
            ) : (
              <>
                <p className="text-gray-600">
                  Êtes-vous sûr de vouloir bloquer l'utilisateur{' '}
                  <span className="font-semibold">{user.full_name || user.username}</span> (
                  {user.email})?
                </p>

                <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                  <p className="text-sm text-orange-800">
                    <strong>⚠️ Blocage :</strong> L'utilisateur ne pourra plus se connecter à la
                    plateforme jusqu'à ce que son compte soit débloqué.
                  </p>
                </div>
              </>
            )}

            {/* Error Message */}
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            {/* Success Message */}
            {success && (
              <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm text-green-600">
                  ✓ Statut mis à jour avec succès
                </p>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                disabled={isLoading || success}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Annuler
              </button>
              <button
                type="button"
                onClick={handleStatusChange}
                disabled={isLoading || success}
                className={`flex-1 px-4 py-2 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors ${
                  isSuspended
                    ? 'bg-green-600 hover:bg-green-700'
                    : 'bg-orange-600 hover:bg-orange-700'
                }`}
              >
                {isLoading
                  ? 'Traitement...'
                  : isSuspended
                  ? 'Débloquer'
                  : 'Bloquer'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
