import { useState, useEffect } from 'react'
import { XMarkIcon } from '@heroicons/react/24/outline'
import {
  useCreateProfileMutation,
  useGetPermissionsQuery,
} from '../api/securityApi'

interface CreateProfileModalProps {
  isOpen: boolean
  onClose: () => void
}

const MODULE_LABELS: Record<string, string> = {
  admin: 'Administration',
  validations: 'Validations',
  interimaires: 'Intérimaires',
  entreprises: 'Entreprises',
  rapports: 'Rapports',
  dashboard: 'Tableau de bord',
}

export default function CreateProfileModal({ isOpen, onClose }: CreateProfileModalProps) {
  const [createProfile, { isLoading }] = useCreateProfileMutation()
  const { data: permissions } = useGetPermissionsQuery({})

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    permissions: [] as string[],
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    if (isOpen) {
      setFormData({ name: '', description: '', permissions: [] })
      setError('')
      setSuccess(false)
    }
  }, [isOpen])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!formData.name.trim()) {
      setError('Le nom du profil est requis')
      return
    }

    if (formData.permissions.length === 0) {
      setError('Sélectionnez au moins une permission')
      return
    }

    try {
      await createProfile({
        name: formData.name,
        description: formData.description || undefined,
        permissions: formData.permissions,
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
      permissions: prev.permissions.includes(permissionId)
        ? prev.permissions.filter((id) => id !== permissionId)
        : [...prev.permissions, permissionId],
    }))
  }

  const toggleModule = (module: string) => {
    const modulePermissions = permissions?.filter((p) => p.module === module).map((p) => p.id) || []
    const allSelected = modulePermissions.every((id) => formData.permissions.includes(id))

    if (allSelected) {
      // Deselect all in module
      setFormData((prev) => ({
        ...prev,
        permissions: prev.permissions.filter((id) => !modulePermissions.includes(id)),
      }))
    } else {
      // Select all in module
      setFormData((prev) => ({
        ...prev,
        permissions: [...new Set([...prev.permissions, ...modulePermissions])],
      }))
    }
  }

  // Group permissions by module
  const permissionsByModule = permissions?.reduce((acc, perm) => {
    if (!acc[perm.module]) {
      acc[perm.module] = []
    }
    acc[perm.module].push(perm)
    return acc
  }, {} as Record<string, typeof permissions>)

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        <div className="fixed inset-0 bg-black bg-opacity-50 transition-opacity" onClick={onClose} />

        <div className="relative bg-white rounded-lg shadow-xl max-w-4xl w-full p-6 z-10 max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-gray-900">Créer un profil</h3>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-500">
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Name */}
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
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
                placeholder="Description du profil..."
              />
            </div>

            {/* Permissions */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Permissions ({formData.permissions.length} sélectionnée(s))
              </label>
              <div className="space-y-4 border border-gray-300 rounded-lg p-4 max-h-96 overflow-y-auto">
                {permissionsByModule &&
                  Object.entries(permissionsByModule).map(([module, modulePerms]) => {
                    const modulePermIds = modulePerms.map((p) => p.id)
                    const allSelected = modulePermIds.every((id) =>
                      formData.permissions.includes(id)
                    )
                    const someSelected = modulePermIds.some((id) =>
                      formData.permissions.includes(id)
                    )

                    return (
                      <div key={module} className="border border-gray-200 rounded-lg p-4">
                        {/* Module Header */}
                        <label className="flex items-center cursor-pointer mb-3">
                          <input
                            type="checkbox"
                            checked={allSelected}
                            ref={(input) => {
                              if (input) input.indeterminate = someSelected && !allSelected
                            }}
                            onChange={() => toggleModule(module)}
                            className="h-5 w-5 text-jlc-purple-600 focus:ring-jlc-purple-500 border-gray-300 rounded"
                          />
                          <span className="ml-3 text-sm font-semibold text-gray-900">
                            {MODULE_LABELS[module] || module}
                          </span>
                        </label>

                        {/* Module Permissions */}
                        <div className="ml-8 space-y-2">
                          {modulePerms.map((perm) => (
                            <label
                              key={perm.id}
                              className="flex items-start cursor-pointer hover:bg-gray-50 p-2 rounded"
                            >
                              <input
                                type="checkbox"
                                checked={formData.permissions.includes(perm.id)}
                                onChange={() => togglePermission(perm.id)}
                                className="h-4 w-4 text-jlc-purple-600 focus:ring-jlc-purple-500 border-gray-300 rounded mt-0.5"
                              />
                              <div className="ml-3">
                                <span className="text-sm text-gray-700">{perm.label}</span>
                                {perm.description && (
                                  <p className="text-xs text-gray-500 mt-0.5">
                                    {perm.description}
                                  </p>
                                )}
                              </div>
                            </label>
                          ))}
                        </div>
                      </div>
                    )
                  })}
              </div>
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
