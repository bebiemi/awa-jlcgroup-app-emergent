import { useState, useEffect } from 'react'
import { XMarkIcon } from '@heroicons/react/24/outline'
import {
  useCreateGroupMutation,
  useGetProfilesQuery,
  useGetUsersQuery,
} from '../api/securityApi'
import { useGetUsersQuery as useGetAllUsers } from '../api/usersApi'

interface CreateGroupModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function CreateGroupModal({ isOpen, onClose }: CreateGroupModalProps) {
  const [createGroup, { isLoading }] = useCreateGroupMutation()
  const { data: profiles } = useGetProfilesQuery()
  const { data: usersData } = useGetAllUsers({ page: 1, page_size: 1000 })

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    profile_id: '',
    member_ids: [] as string[],
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    if (isOpen) {
      setFormData({ name: '', description: '', profile_id: '', member_ids: [] })
      setError('')
      setSuccess(false)
    }
  }, [isOpen])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!formData.name.trim()) {
      setError('Le nom du groupe est requis')
      return
    }

    try {
      await createGroup({
        name: formData.name,
        description: formData.description || undefined,
        profile_id: formData.profile_id || undefined,
        member_ids: formData.member_ids,
      }).unwrap()

      setSuccess(true)
      setTimeout(() => {
        onClose()
      }, 1500)
    } catch (err: any) {
      setError(err?.data?.detail || 'Erreur lors de la création du groupe')
    }
  }

  const toggleMember = (userId: string) => {
    setFormData((prev) => ({
      ...prev,
      member_ids: prev.member_ids.includes(userId)
        ? prev.member_ids.filter((id) => id !== userId)
        : [...prev.member_ids, userId],
    }))
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        <div className="fixed inset-0 bg-black bg-opacity-50 transition-opacity" onClick={onClose} />

        <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full p-6 z-10 max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-gray-900">Créer un groupe</h3>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-500">
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nom du groupe *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
                placeholder="Ex: Équipe RH"
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
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
                placeholder="Description du groupe..."
              />
            </div>

            {/* Profile */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Profil de permissions
              </label>
              <select
                value={formData.profile_id}
                onChange={(e) => setFormData({ ...formData, profile_id: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              >
                <option value="">Aucun profil</option>
                {profiles?.map((profile) => (
                  <option key={profile.id} value={profile.id}>
                    {profile.name} {profile.is_system ? '(Système)' : ''}
                  </option>
                ))}
              </select>
            </div>

            {/* Members */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Membres ({formData.member_ids.length})
              </label>
              <div className="border border-gray-300 rounded-lg max-h-48 overflow-y-auto">
                {usersData?.users && usersData.users.length > 0 ? (
                  <div className="divide-y divide-gray-200">
                    {usersData.users.map((user) => (
                      <label
                        key={user.id}
                        className="flex items-center px-4 py-2 hover:bg-gray-50 cursor-pointer"
                      >
                        <input
                          type="checkbox"
                          checked={formData.member_ids.includes(user.id)}
                          onChange={() => toggleMember(user.id)}
                          className="h-4 w-4 text-jlc-purple-600 focus:ring-jlc-purple-500 border-gray-300 rounded"
                        />
                        <span className="ml-3 text-sm text-gray-700">
                          {user.full_name || user.username} ({user.email})
                        </span>
                      </label>
                    ))}
                  </div>
                ) : (
                  <p className="px-4 py-3 text-sm text-gray-500">Aucun utilisateur disponible</p>
                )}
              </div>
            </div>

            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            {success && (
              <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm text-green-600">✓ Groupe créé avec succès</p>
              </div>
            )}

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
                {isLoading ? 'Création...' : 'Créer le groupe'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
