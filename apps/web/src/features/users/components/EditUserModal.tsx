import { useState, useEffect } from 'react'
import { XMarkIcon, ShieldCheckIcon } from '@heroicons/react/24/outline'
import { useUpdateUserMutation, usersApi, type User } from '../api/usersApi'
import { 
  useListProfilesQuery, 
  useListGroupsQuery,
  useAssignProfilesToUserMutation,
  useAssignGroupsToUserMutation,
  useGetUserPermissionsQuery
} from '@/features/iam/api/iamApi'
import { useAppDispatch } from '@/store/hooks'
import { toast } from 'react-hot-toast'

interface EditUserModalProps {
  user: User
  isOpen: boolean
  onClose: () => void
}

export default function EditUserModal({ user, isOpen, onClose }: EditUserModalProps) {
  const dispatch = useAppDispatch()
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

      // Invalider le cache des utilisateurs pour rafraîchir la liste
      dispatch(usersApi.util.invalidateTags(['Users']))
      
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

            {/* Info IAM Model */}
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800">
                ℹ️ <strong>Modèle IAM Hybride</strong> : Les permissions sont héritées via Profils → Groupes → Rôles IAM
              </p>
            </div>

            {/* Profils Métiers */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Profils Métiers ({formData.profile_ids.length} sélectionné(s))
              </label>
              <div className="border border-gray-300 rounded-lg max-h-48 overflow-y-auto">
                {profiles.length === 0 ? (
                  <p className="px-4 py-3 text-sm text-gray-500">Aucun profil disponible</p>
                ) : (
                  <div className="divide-y divide-gray-200">
                    {profiles
                      .filter((p) => !p.is_protected && !p.is_system_role)
                      .map((profile) => (
                        <label
                          key={profile.id}
                          className="flex items-start px-4 py-3 hover:bg-gray-50 cursor-pointer transition-colors"
                        >
                          <input
                            type="checkbox"
                            checked={formData.profile_ids.includes(profile.id)}
                            onChange={() => toggleProfile(profile.id)}
                            className="h-4 w-4 text-jlc-purple-600 focus:ring-jlc-purple-500 border-gray-300 rounded mt-0.5"
                          />
                          <div className="ml-3 flex-1">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-medium text-gray-700">
                                {profile.name}
                              </span>
                              {profile.category && (
                                <span className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded">
                                  {profile.category}
                                </span>
                              )}
                            </div>
                            {profile.description && (
                              <p className="text-xs text-gray-500 mt-1">{profile.description}</p>
                            )}
                            <p className="text-xs text-gray-400 mt-1">
                              {profile.permission_ids?.length || 0} permission(s)
                            </p>
                          </div>
                        </label>
                      ))}
                  </div>
                )}
              </div>
            </div>

            {/* Groupes */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Groupes Organisationnels ({formData.group_ids.length} sélectionné(s))
              </label>
              <div className="border border-gray-300 rounded-lg max-h-48 overflow-y-auto">
                {groups.length === 0 ? (
                  <p className="px-4 py-3 text-sm text-gray-500">Aucun groupe disponible</p>
                ) : (
                  <div className="divide-y divide-gray-200">
                    {groups
                      .filter((g) => !g.is_protected && !g.is_system_group)
                      .map((group) => (
                        <label
                          key={group.id}
                          className="flex items-start px-4 py-3 hover:bg-gray-50 cursor-pointer transition-colors"
                        >
                          <input
                            type="checkbox"
                            checked={formData.group_ids.includes(group.id)}
                            onChange={() => toggleGroup(group.id)}
                            className="h-4 w-4 text-jlc-purple-600 focus:ring-jlc-purple-500 border-gray-300 rounded mt-0.5"
                          />
                          <div className="ml-3 flex-1">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-medium text-gray-700">
                                {group.name}
                              </span>
                            </div>
                            {group.description && (
                              <p className="text-xs text-gray-500 mt-1">{group.description}</p>
                            )}
                            <div className="flex gap-3 text-xs text-gray-400 mt-1">
                              <span>{group.profile_ids?.length || 0} profil(s)</span>
                              <span>•</span>
                              <span>{group.user_ids?.length || 0} membre(s)</span>
                            </div>
                          </div>
                        </label>
                      ))}
                  </div>
                )}
              </div>
            </div>

            {/* Rôles IAM Hérités (Lecture seule) */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-gray-700">
                  Rôles IAM Hérités (lecture seule)
                </label>
                <button
                  type="button"
                  onClick={() => setShowInheritedRoles(!showInheritedRoles)}
                  className="text-sm text-jlc-purple-600 hover:text-jlc-purple-700"
                >
                  {showInheritedRoles ? 'Masquer' : 'Afficher'}
                </button>
              </div>
              
              {showInheritedRoles && (
                <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg">
                  {userPermissions ? (
                    <div className="space-y-2">
                      <p className="text-xs text-gray-600 mb-2">
                        <ShieldCheckIcon className="h-4 w-4 inline mr-1" />
                        Ces rôles sont calculés automatiquement via vos profils et groupes
                      </p>
                      {userPermissions.computed_roles && userPermissions.computed_roles.length > 0 ? (
                        <div className="flex flex-wrap gap-2">
                          {userPermissions.computed_roles.map((role: string) => (
                            <span
                              key={role}
                              className="inline-flex items-center px-2 py-1 bg-purple-100 text-purple-800 text-xs font-medium rounded"
                            >
                              {role}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <p className="text-xs text-gray-500">Aucun rôle IAM hérité</p>
                      )}
                      <p className="text-xs text-gray-500 mt-2">
                        Total permissions : {userPermissions.permissions?.length || 0}
                      </p>
                    </div>
                  ) : (
                    <p className="text-xs text-gray-500">Chargement des droits hérités...</p>
                  )}
                </div>
              )}
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
