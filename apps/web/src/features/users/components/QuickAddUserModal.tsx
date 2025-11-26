import { useState, useEffect } from 'react'
import { XMarkIcon, EnvelopeIcon } from '@heroicons/react/24/outline'
import {
  useCreateUserMutation,
  useGetGroupsQuery,
} from '@/features/admin/api/securityApi'
import { usePermissions } from '@/hooks/usePermission'

interface QuickAddUserModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function QuickAddUserModal({ isOpen, onClose }: QuickAddUserModalProps) {
  const [createUser, { isLoading }] = useCreateUserMutation()
  const { data: groups } = useGetGroupsQuery()
  const { permissions } = usePermissions(['users.create'])

  const [formData, setFormData] = useState({
    email: '',
    full_name: '',
    group_ids: [] as string[],
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    if (isOpen) {
      setFormData({ email: '', full_name: '', group_ids: [] })
      setError('')
      setSuccess(false)
    }
  }, [isOpen])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!formData.email.trim()) {
      setError('L\'email est requis')
      return
    }

    try {
      await createUser({
        email: formData.email,
        full_name: formData.full_name || undefined,
        password: undefined, // Auto-generate
        roles: [],
        group_ids: formData.group_ids,
        profile_id: undefined,
        send_invitation: true,
      }).unwrap()

      setSuccess(true)
      setTimeout(() => {
        onClose()
      }, 2000)
    } catch (err: any) {
      setError(err?.data?.detail || 'Erreur lors de la création de l\'utilisateur')
    }
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

  if (!permissions['users.create']) {
    return null
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        <div className="fixed inset-0 bg-black bg-opacity-50 transition-opacity" onClick={onClose} />

        <div className="relative bg-white rounded-lg shadow-xl max-w-lg w-full p-6 z-10">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-gray-900">Ajout rapide d'utilisateur</h3>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-500">
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg flex items-start gap-2">
            <EnvelopeIcon className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <p className="text-sm text-blue-800">
              Un email d'invitation sera automatiquement envoyé à l'utilisateur avec un mot de passe temporaire.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email *
              </label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
                placeholder="utilisateur@example.com"
                required
              />
            </div>

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
                placeholder="Prénom Nom"
              />
            </div>

            {/* Groups */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Groupes (optionnel)
              </label>
              {groups && groups.length > 0 ? (
                <div className="border border-gray-300 rounded-lg max-h-40 overflow-y-auto">
                  {groups.map((group) => (
                    <label
                      key={group.id}
                      className="flex items-center px-4 py-2 hover:bg-gray-50 cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={formData.group_ids.includes(group.id)}
                        onChange={() => toggleGroup(group.id)}
                        className="h-4 w-4 text-jlc-purple-600 focus:ring-jlc-purple-500 border-gray-300 rounded"
                      />
                      <span className="ml-3 text-sm text-gray-700">{group.name}</span>
                    </label>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500">Aucun groupe disponible</p>
              )}
            </div>

            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            {success && (
              <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm text-green-600">
                  ✓ Utilisateur créé avec succès ! Un email d'invitation a été envoyé.
                </p>
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
                {isLoading ? 'Création...' : 'Créer et inviter'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
