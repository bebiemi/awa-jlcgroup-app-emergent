import { useState, useEffect } from 'react'
import { XMarkIcon, ShieldCheckIcon } from '@heroicons/react/24/outline'
import { useUpdateUserMutation, type User } from '../api/usersApi'
import { 
  useListProfilesQuery, 
  useListGroupsQuery,
  useAssignProfilesToUserMutation,
  useAssignGroupsToUserMutation,
  useGetUserPermissionsQuery
} from '@/features/iam/api/iamApi'
import { toast } from 'react-hot-toast'

interface EditUserModalProps {
  user: User
  isOpen: boolean
  onClose: () => void
}

export default function EditUserModal({ user, isOpen, onClose }: EditUserModalProps) {
  const [updateUser, { isLoading: isUpdating }] = useUpdateUserMutation()
  const [assignProfiles, { isLoading: isAssigningProfiles }] = useAssignProfilesToUserMutation()
  const [assignGroups, { isLoading: isAssigningGroups }] = useAssignGroupsToUserMutation()
  
  // Fetch available profiles and groups
  const { data: profiles = [] } = useListProfilesQuery()
  const { data: groups = [] } = useListGroupsQuery()
  
  // Fetch user's current permissions (for display only)
  const { data: userPermissions } = useGetUserPermissionsQuery(user.id, { skip: !isOpen })
  
  const [formData, setFormData] = useState({
    full_name: user.full_name || '',
    email: user.email,
    profile_ids: user.profile_ids || [],
    group_ids: user.group_ids || [],
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [showInheritedRoles, setShowInheritedRoles] = useState(false)

  useEffect(() => {
    if (isOpen) {
      setFormData({
        full_name: user.full_name || '',
        email: user.email,
        profile_ids: user.profile_ids || [],
        group_ids: user.group_ids || [],
      })
      setError('')
      setSuccess(false)
      setShowInheritedRoles(false)
    }
  }, [isOpen, user])
  
  const isLoading = isUpdating || isAssigningProfiles || isAssigningGroups

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    try {
      // 1. Update basic user info (name, email)
      await updateUser({
        user_id: user.id,
        data: {
          full_name: formData.full_name,
          email: formData.email,
        },
      }).unwrap()

      // 2. Assign profiles (respects IAM model)
      if (JSON.stringify(formData.profile_ids) !== JSON.stringify(user.profile_ids || [])) {
        await assignProfiles({
          user_id: user.id,
          profile_ids: formData.profile_ids,
        }).unwrap()
      }

      // 3. Assign groups (respects IAM model)
      if (JSON.stringify(formData.group_ids) !== JSON.stringify(user.group_ids || [])) {
        await assignGroups({
          user_id: user.id,
          group_ids: formData.group_ids,
        }).unwrap()
      }

      toast.success('Utilisateur mis à jour avec succès')
      setSuccess(true)
      setTimeout(() => {
        onClose()
      }, 1500)
    } catch (err: any) {
      const errorMsg = err?.data?.detail || 'Erreur lors de la mise à jour'
      setError(errorMsg)
      toast.error(errorMsg)
    }
  }

  const toggleProfile = (profileId: string) => {
    setFormData((prev) => ({
      ...prev,
      profile_ids: prev.profile_ids.includes(profileId)
        ? prev.profile_ids.filter((id) => id !== profileId)
        : [...prev.profile_ids, profileId],
    }))
  }

  const toggleGroup = (groupId: string) => {
    setFormData((prev) => ({
      ...prev,
      group_ids: prev.group_ids.includes(groupId)
        ? prev.group_ids.filter((id) => id !== groupId)
        : [...prev.group_ids, groupId],
    }))
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        {/* Backdrop */}
        <div className="fixed inset-0 bg-black bg-opacity-50 transition-opacity" onClick={onClose} />

        {/* Modal */}
        <div className="relative bg-white rounded-lg shadow-xl max-w-4xl w-full p-6 z-10 max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-gray-900">Modifier l'utilisateur</h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500 transition-colors"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Full Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nom complet
              </label>
              <input
                type="text"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
                placeholder="Nom complet"
              />
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
                placeholder="email@example.com"
                required
              />
            </div>

            {/* Roles */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Rôles</label>
              <div className="space-y-2">
                {['admin', 'super_admin', 'interim', 'company', 'agency'].map((role) => (
                  <label key={role} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.roles.includes(role)}
                      onChange={() => toggleRole(role)}
                      className="h-4 w-4 text-jlc-purple-600 focus:ring-jlc-purple-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700 capitalize">{role}</span>
                  </label>
                ))}
              </div>
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
                <p className="text-sm text-green-600">✓ Utilisateur mis à jour avec succès</p>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Annuler
              </button>
              <button
                type="submit"
                disabled={isLoading || success}
                className="flex-1 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? 'Enregistrement...' : 'Enregistrer'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
