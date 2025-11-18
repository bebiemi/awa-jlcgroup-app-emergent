import { useState, useEffect } from 'react'
import { XMarkIcon } from '@heroicons/react/24/outline'
import { 
  useListProfilesQuery, 
  useListGroupsQuery,
  useAssignProfilesToUserMutation,
  useAssignGroupsToUserMutation,
  type Profile, 
  type Group 
} from '@/features/iam/api/iamApi'
import { toast } from 'react-hot-toast'

interface AssignTeamMemberModalProps {
  user: any
  isOpen: boolean
  onClose: () => void
  canAssignProfiles: boolean
  canAssignGroups: boolean
}

export default function AssignTeamMemberModal({
  user,
  isOpen,
  onClose,
  canAssignProfiles,
  canAssignGroups,
}: AssignTeamMemberModalProps) {
  const { data: profiles = [] } = useListProfilesQuery()
  const { data: groups = [] } = useListGroupsQuery()
  const [assignProfiles] = useAssignProfilesToUserMutation()
  const [assignGroups] = useAssignGroupsToUserMutation()

  const [selectedProfiles, setSelectedProfiles] = useState<string[]>([])
  const [selectedGroups, setSelectedGroups] = useState<string[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    if (isOpen && user) {
      setSelectedProfiles(user.profile_ids || [])
      setSelectedGroups(user.group_ids || [])
    }
  }, [isOpen, user])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    try {
      const promises = []

      // Assigner les profils si la permission est disponible
      if (canAssignProfiles) {
        promises.push(
          assignProfiles({
            user_id: user.id,
            profile_ids: selectedProfiles,
          }).unwrap()
        )
      }

      // Assigner les groupes si la permission est disponible
      if (canAssignGroups) {
        promises.push(
          assignGroups({
            user_id: user.id,
            group_ids: selectedGroups,
          }).unwrap()
        )
      }

      // Attendre que toutes les opérations soient terminées
      await Promise.all(promises)
      
      toast.success('Affectations mises à jour avec succès')
      onClose()
    } catch (error: any) {
      console.error('Error updating assignments:', error)
      toast.error(error?.data?.detail || 'Erreur lors de la mise à jour')
    } finally {
      setIsSubmitting(false)
    }
  }

  const toggleProfile = (profileId: string) => {
    setSelectedProfiles((prev) =>
      prev.includes(profileId)
        ? prev.filter((id) => id !== profileId)
        : [...prev, profileId]
    )
  }

  const toggleGroup = (groupId: string) => {
    setSelectedGroups((prev) =>
      prev.includes(groupId)
        ? prev.filter((id) => id !== groupId)
        : [...prev, groupId]
    )
  }

  if (!isOpen) return null

  // Filtrer les profils pour exclure les profils système/admin sauf si l'utilisateur a déjà ces permissions
  const availableProfiles = profiles.filter((profile: Profile) => {
    // Les managers peuvent attribuer les profils métier (user category)
    // mais pas les profils admin ou système protégés
    if (profile.is_protected || profile.is_system_role) {
      return false
    }
    return profile.category === 'user' || profile.category === 'custom'
  })

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        <div className="fixed inset-0 bg-black bg-opacity-50 transition-opacity" onClick={onClose} />

        <div className="relative bg-white rounded-lg shadow-xl max-w-3xl w-full p-6 z-10 max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-xl font-semibold text-gray-900">
                Gérer les affectations
              </h3>
              <p className="text-sm text-gray-500 mt-1">
                {user.full_name || user.username} ({user.email})
              </p>
            </div>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-500">
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Profils */}
            {canAssignProfiles && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Profils métier ({selectedProfiles.length} sélectionné(s))
                </label>
                <div className="border border-gray-300 rounded-lg max-h-60 overflow-y-auto">
                  {availableProfiles.length === 0 ? (
                    <p className="px-4 py-3 text-sm text-gray-500">Aucun profil disponible</p>
                  ) : (
                    <div className="divide-y divide-gray-200">
                      {availableProfiles.map((profile: Profile) => (
                        <label
                          key={profile.id}
                          className="flex items-start px-4 py-3 hover:bg-gray-50 cursor-pointer transition-colors"
                        >
                          <input
                            type="checkbox"
                            checked={selectedProfiles.includes(profile.id)}
                            onChange={() => toggleProfile(profile.id)}
                            className="h-4 w-4 text-jlc-purple-600 focus:ring-jlc-purple-500 border-gray-300 rounded mt-0.5"
                          />
                          <div className="ml-3 flex-1">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-medium text-gray-700">
                                {profile.name}
                              </span>
                              <span className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded">
                                {profile.code}
                              </span>
                              {profile.category && (
                                <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded">
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
            )}

            {/* Groupes */}
            {canAssignGroups && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Groupes organisationnels ({selectedGroups.length} sélectionné(s))
                </label>
                <div className="border border-gray-300 rounded-lg max-h-60 overflow-y-auto">
                  {groups.length === 0 ? (
                    <p className="px-4 py-3 text-sm text-gray-500">Aucun groupe disponible</p>
                  ) : (
                    <div className="divide-y divide-gray-200">
                      {groups
                        .filter((group: Group) => !group.is_protected && !group.is_system_group)
                        .map((group: Group) => (
                          <label
                            key={group.id}
                            className="flex items-start px-4 py-3 hover:bg-gray-50 cursor-pointer transition-colors"
                          >
                            <input
                              type="checkbox"
                              checked={selectedGroups.includes(group.id)}
                              onChange={() => toggleGroup(group.id)}
                              className="h-4 w-4 text-jlc-purple-600 focus:ring-jlc-purple-500 border-gray-300 rounded mt-0.5"
                            />
                            <div className="ml-3 flex-1">
                              <div className="flex items-center gap-2">
                                <span className="text-sm font-medium text-gray-700">
                                  {group.name}
                                </span>
                                <span className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded">
                                  {group.code}
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
            )}

            {/* Info */}
            {!canAssignProfiles && !canAssignGroups && (
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-sm text-yellow-800">
                  Vous n'avez pas les permissions nécessaires pour modifier les affectations.
                </p>
              </div>
            )}

            {/* Summary */}
            {(canAssignProfiles || canAssignGroups) && (
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h4 className="text-sm font-medium text-blue-900 mb-2">Résumé des modifications</h4>
                <div className="text-sm text-blue-800 space-y-1">
                  {canAssignProfiles && (
                    <p>• Profils : {selectedProfiles.length} sélectionné(s)</p>
                  )}
                  {canAssignGroups && (
                    <p>• Groupes : {selectedGroups.length} sélectionné(s)</p>
                  )}
                </div>
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
              {(canAssignProfiles || canAssignGroups) && (
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="flex-1 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isSubmitting ? 'Enregistrement...' : 'Enregistrer'}
                </button>
              )}
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
