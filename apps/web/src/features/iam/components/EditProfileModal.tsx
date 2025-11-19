import { useState, useEffect } from 'react'
import { XMarkIcon, ShieldCheckIcon } from '@heroicons/react/24/outline'
import { useUpdateProfileMutation, useListPermissionsQuery, type Profile } from '../api/iamApi'
import DualColumnPermissionSelector from './DualColumnPermissionSelector'

interface EditProfileModalProps {
  profile: Profile
  isOpen: boolean
  onClose: () => void
}

export default function EditProfileModal({ profile, isOpen, onClose }: EditProfileModalProps) {
  const [updateProfile, { isLoading }] = useUpdateProfileMutation()
  const { data: permissions = [] } = useListPermissionsQuery()

  const [formData, setFormData] = useState({
    name: profile.name,
    description: profile.description || '',
    permission_ids: profile.permission_ids,
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    if (isOpen) {
      setFormData({
        name: profile.name,
        description: profile.description || '',
        permission_ids: profile.permission_ids,
      })
      setError('')
      setSuccess(false)
    }
  }, [isOpen, profile])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (profile.is_protected) {
      setError('Ce profil est protégé et ne peut pas être modifié')
      return
    }

    try {
      await updateProfile({
        id: profile.id,
        data: {
          name: formData.name,
          description: formData.description || undefined,
          permission_ids: formData.permission_ids,
        },
      }).unwrap()

      setSuccess(true)
      setTimeout(() => {
        onClose()
      }, 1500)
    } catch (err: any) {
      setError(err?.data?.detail || 'Erreur lors de la mise à jour')
    }
  }

  if (!isOpen) return null

  const isReadOnly = profile.is_protected || profile.is_system_role

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        <div className="fixed inset-0 bg-black bg-opacity-50 transition-opacity" onClick={onClose} />

        <div className="relative bg-white rounded-lg shadow-xl max-w-5xl w-full p-6 z-10 max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-xl font-semibold text-gray-900">
                  {isReadOnly ? 'Voir le profil IAM' : 'Modifier le profil IAM'}
                </h3>
                {profile.is_protected && (
                  <span className="inline-flex items-center gap-1 px-2 py-1 bg-purple-100 text-purple-700 text-xs font-medium rounded">
                    <ShieldCheckIcon className="h-4 w-4" />
                    Protégé
                  </span>
                )}
                {profile.is_system_role && (
                  <span className="px-2 py-1 bg-indigo-100 text-indigo-700 text-xs font-medium rounded">
                    Système
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-500 mt-1">
                Code : <span className="font-mono">{profile.code}</span>
              </p>
            </div>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-500">
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          {isReadOnly && (
            <div className="mb-4 p-3 bg-indigo-50 border border-indigo-200 rounded-lg">
              <p className="text-sm text-indigo-800">
                ℹ️ Ce profil {profile.is_protected ? 'protégé' : 'système'} ne peut pas être
                modifié. Vous pouvez uniquement consulter ses permissions.
              </p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Nom */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nom du profil</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
                disabled={isReadOnly}
                required
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
                disabled={isReadOnly}
              />
            </div>

            {/* Catégorie (lecture seule) */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Catégorie</label>
              <input
                type="text"
                value={profile.category}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-100 cursor-not-allowed"
                disabled
              />
            </div>

            {/* Sélecteur de permissions à deux colonnes */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">Permissions</label>
              <DualColumnPermissionSelector
                allPermissions={permissions}
                selectedPermissionIds={formData.permission_ids}
                onAdd={(permId) => {
                  setFormData((prev) => ({
                    ...prev,
                    permission_ids: [...prev.permission_ids, permId],
                  }))
                }}
                onRemove={(permId) => {
                  setFormData((prev) => ({
                    ...prev,
                    permission_ids: prev.permission_ids.filter((id) => id !== permId),
                  }))
                }}
                disabled={isReadOnly}
              />
            </div>

            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            {success && (
              <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm text-green-600">✓ Profil mis à jour avec succès</p>
              </div>
            )}

            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                {isReadOnly ? 'Fermer' : 'Annuler'}
              </button>
              {!isReadOnly && (
                <button
                  type="submit"
                  disabled={isLoading || success}
                  className="flex-1 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isLoading ? 'Enregistrement...' : 'Enregistrer'}
                </button>
              )}
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
