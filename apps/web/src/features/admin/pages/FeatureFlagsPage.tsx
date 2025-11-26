import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import Layout from '@/components/Layout'
import Card from '@/components/Card'
import { toast } from 'react-hot-toast'
import {
  PlusIcon,
  PencilIcon,
  TrashIcon,
  FlagIcon,
  ChartBarIcon,
  ClockIcon,
} from '@heroicons/react/24/outline'
import {
  useListFeatureFlagsQuery,
  useCreateFeatureFlagMutation,
  useUpdateFeatureFlagMutation,
  useDeleteFeatureFlagMutation,
  useApplyRolloutMutation,
  type FeatureFlag,
  type CreateFeatureFlagRequest,
} from '../api/featureFlagApi'
import { usePermissions } from '@/hooks/usePermission'

export default function FeatureFlagsPage() {
  const { t } = useTranslation()
  const [includeInactive, setIncludeInactive] = useState(true)
  const [typeFilter, setTypeFilter] = useState<string>('')
  const [showModal, setShowModal] = useState(false)
  const [showRolloutModal, setShowRolloutModal] = useState(false)
  const [showImportModal, setShowImportModal] = useState(false)
  const [editingFlag, setEditingFlag] = useState<FeatureFlag | null>(null)
  const [selectedFlag, setSelectedFlag] = useState<FeatureFlag | null>(null)
  const [importFile, setImportFile] = useState<File | null>(null)
  const [overwriteExisting, setOverwriteExisting] = useState(false)
  const { permissions } = usePermissions(['flags.read', 'flags.manage'])
  const canRead = permissions['flags.read'] || permissions['flags.manage']
  const canManage = permissions['flags.manage']

  // Form state
  const [formData, setFormData] = useState<CreateFeatureFlagRequest>({
    key: '',
    type: 'GLOBAL',
    value: false,
    target: null,
    metadata: {
      description: '',
      rollout_percentage: 0,
      tags: [],
      dependencies: [],
    },
  })
  const [rolloutPercentage, setRolloutPercentage] = useState(0)

  const { data, isLoading, refetch } = useListFeatureFlagsQuery({
    include_inactive: includeInactive,
    type_filter: typeFilter,
  })

  const [createFlag] = useCreateFeatureFlagMutation()
  const [updateFlag] = useUpdateFeatureFlagMutation()
  const [deleteFlag] = useDeleteFeatureFlagMutation()
  const [applyRollout] = useApplyRolloutMutation()

  const resetForm = () => {
    setFormData({
      key: '',
      type: 'GLOBAL',
      value: false,
      target: null,
      metadata: {
        description: '',
        rollout_percentage: 0,
        tags: [],
        dependencies: [],
      },
    })
    setEditingFlag(null)
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      await createFlag(formData).unwrap()
      toast.success('Feature flag créé avec succès')
      setShowModal(false)
      resetForm()
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la création')
    }
  }

  const handleEdit = (flag: FeatureFlag) => {
    setEditingFlag(flag)
    setFormData({
      key: flag.key,
      type: flag.type,
      value: flag.value,
      target: flag.target,
      metadata: flag.metadata,
    })
    setShowModal(true)
  }

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!editingFlag) return

    if (!canManage) return
    try {
      await updateFlag({
        id: editingFlag.id,
        data: {
          value: formData.value,
          target: formData.target,
          metadata: formData.metadata,
        },
      }).unwrap()
      toast.success('Feature flag mis à jour')
      setShowModal(false)
      resetForm()
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la mise à jour')
    }
  }

  const handleDelete = async (id: string, key: string) => {
    if (!confirm(`Supprimer le flag "${key}" ?`)) return

    if (!canManage) return
    try {
      await deleteFlag(id).unwrap()
      toast.success('Feature flag supprimé')
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la suppression')
    }
  }

  const handleToggle = async (flag: FeatureFlag) => {
    if (!canManage) return
    try {
      await updateFlag({
        id: flag.id,
        data: { value: !flag.value },
      }).unwrap()
      toast.success(`Flag ${!flag.value ? 'activé' : 'désactivé'}`)
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors du toggle')
    }
  }

  const handleOpenRollout = (flag: FeatureFlag) => {
    setSelectedFlag(flag)
    setRolloutPercentage(flag.metadata.rollout_percentage || 0)
    setShowRolloutModal(true)
  }

  const handleApplyRollout = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!selectedFlag) return

    if (!canManage) return
    try {
      await applyRollout({
        id: selectedFlag.id,
        data: {
          rollout_percentage: rolloutPercentage,
          description: `Rollout à ${rolloutPercentage}%`,
        },
      }).unwrap()
      toast.success(`Rollout appliqué: ${rolloutPercentage}%`)
      setShowRolloutModal(false)
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors du rollout')
    }
  }

  const handleExport = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/feature-flags/export', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      
      if (!response.ok) throw new Error('Export failed')
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `feature_flags_export_${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
      
      toast.success('Feature flags exportés avec succès')
    } catch (error) {
      toast.error('Erreur lors de l\'export')
    }
  }

  const handleImport = async () => {
    if (!importFile) {
      toast.error('Veuillez sélectionner un fichier')
      return
    }

    if (!canManage) return
    try {
      const fileContent = await importFile.text()
      const importData = JSON.parse(fileContent)
      
      const token = localStorage.getItem('access_token')
      const response = await fetch(`/api/feature-flags/import?overwrite=${overwriteExisting}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(importData),
      })
      
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Import failed')
      }
      
      const result = await response.json()
      toast.success(result.message)
      setShowImportModal(false)
      setImportFile(null)
      setOverwriteExisting(false)
      refetch()
    } catch (error: any) {
      toast.error(error.message || 'Erreur lors de l\'import')
    }
  }

  const getTypeBadgeColor = (type: string) => {
    switch (type) {
      case 'GLOBAL':
        return 'bg-blue-100 text-blue-800'
      case 'ROLE':
        return 'bg-purple-100 text-purple-800'
      case 'USER':
        return 'bg-green-100 text-green-800'
      case 'ENV':
        return 'bg-orange-100 text-orange-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (!canRead) return null

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Feature Flags</h1>
            <p className="mt-2 text-gray-600">
              Gérez les fonctionnalités de l'application par flag
            </p>
          </div>
          {canManage && (
            <div className="flex gap-2">
              <button
                onClick={handleExport}
                className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Export
              </button>
              <button
                onClick={() => setShowImportModal(true)}
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
                Import
              </button>
              <button
                onClick={() => {
                  resetForm()
                  setShowModal(true)
                }}
                className="inline-flex items-center gap-2 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700"
              >
                <PlusIcon className="h-5 w-5" />
                Nouveau Flag
              </button>
            </div>
          )}
        </div>

        {/* Statistiques */}
        {!isLoading && data && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total</p>
                  <p className="text-2xl font-bold text-gray-900">{data.total}</p>
                </div>
                <FlagIcon className="h-8 w-8 text-blue-500" />
              </div>
            </Card>
            <Card>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Actifs</p>
                  <p className="text-2xl font-bold text-green-600">
                    {data.flags.filter((f) => f.value).length}
                  </p>
                </div>
                <div className="text-3xl">✅</div>
              </div>
            </Card>
            <Card>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Inactifs</p>
                  <p className="text-2xl font-bold text-red-600">
                    {data.flags.filter((f) => !f.value).length}
                  </p>
                </div>
                <div className="text-3xl">❌</div>
              </div>
            </Card>
            <Card>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">En rollout</p>
                  <p className="text-2xl font-bold text-orange-600">
                    {data.flags.filter((f) => f.metadata.rollout_percentage > 0 && f.metadata.rollout_percentage < 100).length}
                  </p>
                </div>
                <ChartBarIcon className="h-8 w-8 text-orange-500" />
              </div>
            </Card>
          </div>
        )}

        {/* Filtres */}
        <Card>
          <div className="flex gap-4 items-center">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={includeInactive}
                onChange={(e) => setIncludeInactive(e.target.checked)}
                className="rounded border-gray-300"
              />
              <span className="text-sm text-gray-700">Afficher inactifs</span>
            </label>

            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="rounded-lg border-gray-300 text-sm"
            >
              <option value="">Tous les types</option>
              <option value="GLOBAL">GLOBAL</option>
              <option value="ROLE">ROLE</option>
              <option value="USER">USER</option>
              <option value="ENV">ENV</option>
            </select>
          </div>
        </Card>

        {/* Liste des flags */}
        <Card>
          {isLoading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
              <p className="mt-4 text-gray-600">Chargement...</p>
            </div>
          ) : data?.flags.length === 0 ? (
            <div className="text-center py-12">
              <FlagIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">Aucun flag</h3>
              <p className="mt-1 text-sm text-gray-500">
                Créez votre premier feature flag
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Clé
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Cible
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Description
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Rollout
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Statut
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {data?.flags.map((flag) => (
                    <tr key={flag.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <code className="text-sm font-mono font-medium text-gray-900 bg-gray-100 px-2 py-1 rounded">
                          {flag.key}
                        </code>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getTypeBadgeColor(flag.type)}`}>
                          {flag.type}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {flag.target || '-'}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                        {flag.metadata.description || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <div className="w-24 bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-jlc-purple-600 h-2 rounded-full"
                              style={{ width: `${flag.metadata.rollout_percentage}%` }}
                            ></div>
                          </div>
                          <span className="text-xs text-gray-600">
                            {flag.metadata.rollout_percentage}%
                          </span>
                          {data.can_create && (
                            <button
                              onClick={() => handleOpenRollout(flag)}
                              className="p-1 text-gray-400 hover:text-jlc-purple-600"
                              title="Modifier rollout"
                            >
                              <ChartBarIcon className="h-4 w-4" />
                            </button>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <button
                          onClick={() => handleToggle(flag)}
                          disabled={!data.can_create}
                          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                            flag.value ? 'bg-green-600' : 'bg-gray-300'
                          } ${!data.can_create && 'opacity-50 cursor-not-allowed'}`}
                        >
                          <span
                            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                              flag.value ? 'translate-x-6' : 'translate-x-1'
                            }`}
                          />
                        </button>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <div className="flex gap-2">
                          {data.can_create && (
                            <>
                              <button
                                onClick={() => handleEdit(flag)}
                                className="p-2 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg"
                                title="Modifier"
                              >
                                <PencilIcon className="h-5 w-5" />
                              </button>
                              <button
                                onClick={() => handleDelete(flag.id, flag.key)}
                                className="p-2 text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg"
                                title="Supprimer"
                              >
                                <TrashIcon className="h-5 w-5" />
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>

      {/* Modal Create/Edit */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">
              {editingFlag ? 'Modifier' : 'Créer'} un Feature Flag
            </h2>
            <form onSubmit={editingFlag ? handleUpdate : handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Clé *
                </label>
                <input
                  type="text"
                  value={formData.key}
                  onChange={(e) => setFormData({ ...formData, key: e.target.value })}
                  disabled={!!editingFlag}
                  className="w-full rounded-lg border-gray-300"
                  placeholder="feature.mission.bulk_assign"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Type *
                </label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value as any })}
                  disabled={!!editingFlag}
                  className="w-full rounded-lg border-gray-300"
                  required
                >
                  <option value="GLOBAL">GLOBAL - S'applique à tous</option>
                  <option value="ROLE">ROLE - Pour un rôle spécifique</option>
                  <option value="USER">USER - Pour un utilisateur</option>
                  <option value="ENV">ENV - Pour un environnement</option>
                </select>
              </div>

              {formData.type !== 'GLOBAL' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Cible *
                  </label>
                  <input
                    type="text"
                    value={formData.target || ''}
                    onChange={(e) => setFormData({ ...formData, target: e.target.value })}
                    className="w-full rounded-lg border-gray-300"
                    placeholder={
                      formData.type === 'ROLE'
                        ? 'admin'
                        : formData.type === 'USER'
                        ? 'user_uuid'
                        : 'production'
                    }
                    required
                  />
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={formData.metadata?.description || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      metadata: { ...formData.metadata!, description: e.target.value },
                    })
                  }
                  className="w-full rounded-lg border-gray-300"
                  rows={3}
                  placeholder="Description de la fonctionnalité"
                />
              </div>

              <div>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.value}
                    onChange={(e) => setFormData({ ...formData, value: e.target.checked })}
                    className="rounded border-gray-300"
                  />
                  <span className="text-sm font-medium text-gray-700">Activé</span>
                </label>
              </div>

              <div className="flex gap-2 justify-end pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false)
                    resetForm()
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700"
                >
                  {editingFlag ? 'Mettre à jour' : 'Créer'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal Rollout */}
      {showRolloutModal && selectedFlag && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-xl font-bold mb-4">Rollout Progressif</h2>
            <p className="text-sm text-gray-600 mb-4">
              Flag: <code className="font-mono bg-gray-100 px-1">{selectedFlag.key}</code>
            </p>
            <form onSubmit={handleApplyRollout} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Pourcentage: {rolloutPercentage}%
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="5"
                  value={rolloutPercentage}
                  onChange={(e) => setRolloutPercentage(Number(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>0%</span>
                  <span>50%</span>
                  <span>100%</span>
                </div>
              </div>

              <div className="bg-blue-50 p-3 rounded-lg">
                <p className="text-sm text-blue-800">
                  Le flag sera activé pour environ {rolloutPercentage}% des utilisateurs ciblés
                </p>
              </div>

              <div className="flex gap-2 justify-end pt-4">
                <button
                  type="button"
                  onClick={() => setShowRolloutModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700"
                >
                  Appliquer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal Import */}
      {showImportModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-xl font-bold mb-4">Importer Feature Flags</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Fichier JSON
                </label>
                <input
                  type="file"
                  accept=".json"
                  onChange={(e) => setImportFile(e.target.files?.[0] || null)}
                  className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-jlc-purple-50 file:text-jlc-purple-700 hover:file:bg-jlc-purple-100"
                />
              </div>

              <div>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={overwriteExisting}
                    onChange={(e) => setOverwriteExisting(e.target.checked)}
                    className="rounded border-gray-300"
                  />
                  <span className="text-sm text-gray-700">
                    Écraser les flags existants
                  </span>
                </label>
                <p className="mt-1 text-xs text-gray-500">
                  Si décoché, les flags existants seront ignorés
                </p>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                <p className="text-xs text-yellow-800">
                  ⚠️ Cette action va importer des feature flags. Assurez-vous que le fichier provient d'une source fiable.
                </p>
              </div>

              <div className="flex gap-2 justify-end pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowImportModal(false)
                    setImportFile(null)
                    setOverwriteExisting(false)
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  Annuler
                </button>
                <button
                  onClick={handleImport}
                  disabled={!importFile}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Importer
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </Layout>
  )
}
