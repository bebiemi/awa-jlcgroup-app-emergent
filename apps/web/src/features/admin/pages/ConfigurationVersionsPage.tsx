import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import Layout from '@/components/Layout'
import Card from '@/components/Card'
import Button from '@/components/Button'
import Modal from '@/components/Modal'
import { 
  ClockIcon, 
  ArrowPathIcon, 
  DocumentDuplicateIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

interface Version {
  id: string
  version: string
  description: string
  created_at: string
  created_by_name: string
  snapshot_type: string
  tags: string[]
}

export default function ConfigurationVersionsPage() {
  const { t } = useTranslation()
  const [versions, setVersions] = useState<Version[]>([])
  const [loading, setLoading] = useState(false)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showRollbackModal, setShowRollbackModal] = useState(false)
  const [selectedVersion, setSelectedVersion] = useState<Version | null>(null)
  const [description, setDescription] = useState('')
  const [rollbackReason, setRollbackReason] = useState('')

  const loadVersions = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${import.meta.env.REACT_APP_BACKEND_URL}/api/versions/list`)
      const data = await response.json()
      setVersions(data.versions)
    } catch (error) {
      toast.error('Erreur lors du chargement des versions')
    } finally {
      setLoading(false)
    }
  }

  const createSnapshot = async () => {
    if (!description.trim()) {
      toast.error('Description requise')
      return
    }

    try {
      const response = await fetch(
        `${import.meta.env.REACT_APP_BACKEND_URL}/api/versions/snapshot?description=${encodeURIComponent(description)}`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          }
        }
      )

      if (response.ok) {
        toast.success('Snapshot créé avec succès')
        setShowCreateModal(false)
        setDescription('')
        loadVersions()
      } else {
        toast.error('Erreur lors de la création du snapshot')
      }
    } catch (error) {
      toast.error('Erreur réseau')
    }
  }

  const rollbackToVersion = async () => {
    if (!selectedVersion || !rollbackReason.trim()) {
      toast.error('Raison requise')
      return
    }

    try {
      const response = await fetch(
        `${import.meta.env.REACT_APP_BACKEND_URL}/api/versions/rollback`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
          body: JSON.stringify({
            version_id: selectedVersion.id,
            reason: rollbackReason
          })
        }
      )

      if (response.ok) {
        toast.success('Rollback effectué avec succès')
        setShowRollbackModal(false)
        setRollbackReason('')
        setSelectedVersion(null)
        loadVersions()
      } else {
        toast.error('Erreur lors du rollback')
      }
    } catch (error) {
      toast.error('Erreur réseau')
    }
  }

  useEffect(() => {
    loadVersions()
  }, [])

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Versions de Configuration
            </h1>
            <p className="mt-2 text-gray-600">
              Gérez l'historique et les versions de votre configuration
            </p>
          </div>
          <Button
            onClick={() => setShowCreateModal(true)}
            icon={DocumentDuplicateIcon}
          >
            Créer Snapshot
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-purple-100 rounded-lg p-3">
                <ClockIcon className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Versions</p>
                <p className="text-2xl font-bold text-gray-900">{versions.length}</p>
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-green-100 rounded-lg p-3">
                <CheckCircleIcon className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Snapshots Manuels</p>
                <p className="text-2xl font-bold text-gray-900">
                  {versions.filter(v => v.snapshot_type === 'manual').length}
                </p>
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-blue-100 rounded-lg p-3">
                <ArrowPathIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Rollbacks</p>
                <p className="text-2xl font-bold text-gray-900">
                  {versions.filter(v => v.snapshot_type === 'rollback').length}
                </p>
              </div>
            </div>
          </Card>
        </div>

        {/* Versions List */}
        <Card>
          <h2 className="text-xl font-semibold mb-4">Historique des Versions</h2>
          <div className="space-y-4">
            {loading ? (
              <p className="text-center text-gray-500 py-8">Chargement...</p>
            ) : versions.length === 0 ? (
              <p className="text-center text-gray-500 py-8">Aucune version disponible</p>
            ) : (
              versions.map((version) => (
                <div
                  key={version.id}
                  className="border border-gray-200 rounded-lg p-4 hover:border-purple-300 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {version.version}
                        </h3>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          version.snapshot_type === 'manual' 
                            ? 'bg-green-100 text-green-800'
                            : version.snapshot_type === 'rollback'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {version.snapshot_type}
                        </span>
                        {version.tags.map(tag => (
                          <span key={tag} className="px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded-full">
                            {tag}
                          </span>
                        ))}
                      </div>
                      <p className="mt-1 text-gray-600">{version.description}</p>
                      <p className="mt-2 text-sm text-gray-500">
                        Par {version.created_by_name} • {new Date(version.created_at).toLocaleString('fr-FR')}
                      </p>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setSelectedVersion(version)
                        setShowRollbackModal(true)
                      }}
                      icon={ArrowPathIcon}
                    >
                      Rollback
                    </Button>
                  </div>
                </div>
              ))
            )}
          </div>
        </Card>

        {/* Create Snapshot Modal */}
        <Modal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          title="Créer un Snapshot"
        >
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description *
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                rows={3}
                placeholder="Décrivez les changements ou la raison de ce snapshot..."
              />
            </div>
            <div className="flex justify-end gap-3">
              <Button
                variant="outline"
                onClick={() => setShowCreateModal(false)}
              >
                Annuler
              </Button>
              <Button onClick={createSnapshot}>
                Créer Snapshot
              </Button>
            </div>
          </div>
        </Modal>

        {/* Rollback Modal */}
        <Modal
          isOpen={showRollbackModal}
          onClose={() => {
            setShowRollbackModal(false)
            setSelectedVersion(null)
            setRollbackReason('')
          }}
          title="Confirmer le Rollback"
        >
          <div className="space-y-4">
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex">
                <XCircleIcon className="h-5 w-5 text-yellow-600 mr-2" />
                <div>
                  <h4 className="text-sm font-medium text-yellow-800">Attention</h4>
                  <p className="mt-1 text-sm text-yellow-700">
                    Cette action va restaurer la configuration à la version{' '}
                    <strong>{selectedVersion?.version}</strong>. Un snapshot automatique
                    sera créé avant le rollback.
                  </p>
                </div>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Raison du rollback *
              </label>
              <textarea
                value={rollbackReason}
                onChange={(e) => setRollbackReason(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                rows={3}
                placeholder="Expliquez pourquoi vous effectuez ce rollback..."
              />
            </div>
            <div className="flex justify-end gap-3">
              <Button
                variant="outline"
                onClick={() => {
                  setShowRollbackModal(false)
                  setSelectedVersion(null)
                  setRollbackReason('')
                }}
              >
                Annuler
              </Button>
              <Button onClick={rollbackToVersion} variant="danger">
                Confirmer Rollback
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </Layout>
  )
}
