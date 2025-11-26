import { useState } from 'react'
import { XMarkIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline'
import { useDeleteUserMutation, type User } from '@/features/users/api/usersApi'
import { usePermissions } from '@/hooks/usePermission'

interface DeleteUserModalProps {
  user: User
  isOpen: boolean
  onClose: () => void
}

export default function DeleteUserModal({ user, isOpen, onClose }: DeleteUserModalProps) {
  const [deleteUser, { isLoading }] = useDeleteUserMutation()
  const { permissions } = usePermissions(['users.delete', 'users.manage'])
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [reason, setReason] = useState('Suppression initiée par un administrateur')

  const handleDelete = async () => {
    setError('')

    try {
      await deleteUser({ user_id: user.id, reason }).unwrap()
      setSuccess(true)
      setTimeout(() => {
        onClose()
      }, 1500)
    } catch (err: any) {
      setError(err?.data?.detail || 'Erreur lors de la suppression')
    }
  }

  if (!isOpen) return null

  if (!permissions['users.delete'] && !permissions['users.manage']) {
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
              <div className="flex-shrink-0 w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                <ExclamationTriangleIcon className="h-6 w-6 text-red-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900">Supprimer l'utilisateur</h3>
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
            <p className="text-gray-600">
              Cette action programme l'archivage puis la suppression définitive de l'utilisateur{' '}
              <span className="font-semibold">{user.full_name || user.username}</span> (
              {user.email})?
            </p>

            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-sm text-red-800">
                <strong>⚠️ Attention :</strong> L'utilisateur est archivé immédiatement puis supprimé définitivement
                après la période de rétention définie (déjà stockée pour les comptes en cours). Les nouvelles valeurs
                de rétention n'affectent pas les programmations déjà enregistrées.
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Motif</label>
              <input
                type="text"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                placeholder="Ex: compte inactif, demande de suppression..."
              />
            </div>

            {/* Error Message */}
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            {/* Success Message */}
            {success && (
              <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm text-green-600">✓ Utilisateur supprimé avec succès</p>
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
                onClick={handleDelete}
                disabled={isLoading || success}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? 'Suppression...' : 'Supprimer définitivement'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
