import { useState, useEffect } from 'react'
import { XMarkIcon } from '@heroicons/react/24/outline'
import { useCreateProfileMutation, useListPermissionsQuery } from '../api/iamApi'
import PermissionSelector from './PermissionSelector'

interface CreateProfileModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function CreateProfileModal({ isOpen, onClose }: CreateProfileModalProps) {
  const [createProfile, { isLoading }] = useCreateProfileMutation()
  const { data: permissions = [] } = useListPermissionsQuery()

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    permission_ids: [] as string[],
    category: 'custom',
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    if (isOpen) {
      setFormData({
        name: '',
        description: '',
        permission_ids: [],
        category: 'custom',
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
      setError('Le nom du profil est requis')
      return
    }

    if (formData.permission_ids.length === 0) {
      setError('Sélectionnez au moins une permission')
      return
    }

    try {
      // Générer automatiquement le code
      const code = generateCode(formData.name)

      await createProfile({
        code,
        name: formData.name,
        description: formData.description || undefined,
        permission_ids: formData.permission_ids,
        category: formData.category,
      }).unwrap()

      setSuccess(true)
      setTimeout(() => {
        onClose()
      }, 1500)
    } catch (err: any) {
      setError(err?.data?.detail || 'Erreur lors de la création du profil')
    }
  }

  const togglePermission = (permissionId: string) => {
    setFormData((prev) => ({
      ...prev,
      permission_ids: prev.permission_ids.includes(permissionId)
        ? prev.permission_ids.filter((id) => id !== permissionId)
        : [...prev.permission_ids, permissionId],
    }))
  }

  const toggleCategory = (category: string) => {
    const categoryPermissions =
      permissions?.filter((p) => p.category === category).map((p) => p.id) || []
    const allSelected = categoryPermissions.every((id) => formData.permission_ids.includes(id))

    if (allSelected) {
      // Désélectionner toutes les permissions de cette catégorie
      setFormData((prev) => ({
        ...prev,
        permission_ids: prev.permission_ids.filter((id) => !categoryPermissions.includes(id)),
      }))
    } else {
      // Sélectionner toutes les permissions de cette catégorie
      setFormData((prev) => ({
        ...prev,
        permission_ids: [...new Set([...prev.permission_ids, ...categoryPermissions])],
      }))
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        <div className="fixed inset-0 bg-black bg-opacity-50 transition-opacity" onClick={onClose} />

        <div className="relative bg-white rounded-lg shadow-xl max-w-5xl w-full p-6 z-10 max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-xl font-semibold text-gray-900">Créer un profil IAM</h3>
              <p className="text-sm text-gray-500 mt-1">
                Le code sera généré automatiquement à partir du nom
              </p>
            </div>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-500">
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Nom */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nom du profil *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
                placeholder="Ex: Gestionnaire Marketing"
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
                placeholder="Description du profil et de son rôle dans l'organisation..."
              />
            </div>

            {/* Catégorie */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Catégorie</label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              >
                <option value="custom">Personnalisé</option>
                <option value="business">Métier</option>
                <option value="technical">Technique</option>
                <option value="management">Gestion</option>
              </select>
            </div>

            {/* Sélecteur de permissions avec recherche/filtrage */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Permissions *
              </label>
              <PermissionSelector
                permissions={permissions}
                selectedPermissionIds={formData.permission_ids}
                onToggle={togglePermission}
                onToggleCategory={toggleCategory}
              />
            </div>

            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            {success && (
              <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm text-green-600">✓ Profil créé avec succès</p>
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
                {isLoading ? 'Création...' : 'Créer le profil'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
