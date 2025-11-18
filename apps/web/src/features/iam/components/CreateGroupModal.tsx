import { useState, useEffect } from 'react'
import { XMarkIcon } from '@heroicons/react/24/outline'
import { useCreateGroupMutation, useListProfilesQuery } from '../api/iamApi'

interface CreateGroupModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function CreateGroupModal({ isOpen, onClose }: CreateGroupModalProps) {
  const [createGroup, { isLoading }] = useCreateGroupMutation()
  const { data: profiles = [] } = useListProfilesQuery()

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    profile_ids: [] as string[],
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    if (isOpen) {
      setFormData({
        name: '',
        description: '',
        profile_ids: [],
      })
      setError('')
      setSuccess(false)
    }
  }, [isOpen])

  // Générer le code automatiquement à partir du nom
  const generateCode = (name: string): string => {
    return name
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '') // Retirer les accents
      .replace(/[^a-z0-9]+/g, '_') // Remplacer les caractères spéciaux par _
      .replace(/^_+|_+$/g, '') // Retirer les _ au début et à la fin
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!formData.name.trim()) {
      setError('Le nom du groupe est requis')
      return
    }

    try {
      // Générer automatiquement le code
      const code = generateCode(formData.name)

      await createGroup({
        code,
        name: formData.name,
        description: formData.description || undefined,
        profile_ids: formData.profile_ids.length > 0 ? formData.profile_ids : undefined,
      }).unwrap()

      setSuccess(true)
      setTimeout(() => {
        onClose()
      }, 1500)
    } catch (err: any) {
      setError(err?.data?.detail || 'Erreur lors de la création du groupe')
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

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        <div className="fixed inset-0 bg-black bg-opacity-50 transition-opacity" onClick={onClose} />

        <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full p-6 z-10 max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-xl font-semibold text-gray-900">Créer un groupe IAM</h3>
              <p className="text-sm text-gray-500 mt-1">
                Le code sera généré automatiquement à partir du nom
              </p>
            </div>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-500">
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Nom */}
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
              {formData.name && (
                <p className="text-xs text-gray-500 mt-1">
                  Code généré : <span className="font-mono">{generateCode(formData.name)}</span>
                </p>
              )}
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
                placeholder="Description du groupe et de son rôle dans l'organisation..."
              />
            </div>

            {/* Profils IAM */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Profils IAM ({formData.profile_ids.length} sélectionné(s))
              </label>
              <p className="text-xs text-gray-500 mb-3">
                Les membres de ce groupe hériteront des permissions des profils sélectionnés
              </p>
              <div className="border border-gray-300 rounded-lg max-h-60 overflow-y-auto">
                {profiles && profiles.length > 0 ? (
                  <div className="divide-y divide-gray-200">
                    {profiles.map((profile) => (
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
                            {profile.is_system_role && (
                              <span className="px-2 py-0.5 bg-indigo-100 text-indigo-700 text-xs font-medium rounded">
                                Système
                              </span>
                            )}
                            {profile.is_protected && (
                              <span className="px-2 py-0.5 bg-purple-100 text-purple-700 text-xs font-medium rounded">
                                Protégé
                              </span>
                            )}
                          </div>
                          {profile.description && (
                            <p className="text-xs text-gray-500 mt-1">{profile.description}</p>
                          )}
                          <p className="text-xs text-gray-400 mt-1">
                            {profile.permission_ids.length} permission(s)
                          </p>
                        </div>
                      </label>
                    ))}
                  </div>
                ) : (
                  <p className="px-4 py-3 text-sm text-gray-500">Aucun profil disponible</p>
                )}
              </div>
            </div>

            {/* Info sur l'ajout de membres */}
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800">
                ℹ️ Les membres du groupe seront ajoutés après la création depuis la page de gestion
                des groupes ou depuis la page de gestion des utilisateurs.
              </p>
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
