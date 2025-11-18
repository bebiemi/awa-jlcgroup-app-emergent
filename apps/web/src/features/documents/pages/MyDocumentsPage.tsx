import { useState } from 'react'
import Layout from '@/components/Layout'
import {
  useListDocumentsQuery,
  useUploadDocumentMutation,
  useDeleteDocumentMutation,
} from '../api/documentsApi'
import {
  ArrowUpTrayIcon,
  DocumentIcon,
  TrashIcon,
  ArrowDownTrayIcon,
  EyeIcon,
} from '@heroicons/react/24/outline'
import { toast } from 'react-hot-toast'

const CATEGORY_LABELS: Record<string, string> = {
  cv: 'CV',
  cover_letter: 'Lettre de motivation',
  diploma: 'Diplôme',
  certificate: 'Certificat',
  id_card: 'Pièce d\'identité',
  contract: 'Contrat',
  payslip: 'Fiche de paie',
  rgpd: 'RGPD',
  other: 'Autre',
}

const STATUS_LABELS: Record<string, string> = {
  pending: 'En attente',
  verified: 'Vérifié',
  rejected: 'Rejeté',
  archived: 'Archivé',
}

const STATUS_COLORS: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  verified: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
  archived: 'bg-gray-100 text-gray-800',
}

const VISIBILITY_LABELS: Record<string, string> = {
  private: 'Privé',
  team: 'Équipe',
  public: 'Public',
}

export default function MyDocumentsPage() {
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [showUploadModal, setShowUploadModal] = useState(false)

  const { data: documents = [], isLoading } = useListDocumentsQuery({
    category: categoryFilter === 'all' ? undefined : categoryFilter,
    status: statusFilter === 'all' ? undefined : statusFilter,
  })

  const [deleteDocument] = useDeleteDocumentMutation()

  const handleDelete = async (id: string, filename: string) => {
    if (!confirm(`Supprimer le document "${filename}" ?`)) {
      return
    }

    try {
      await deleteDocument(id).unwrap()
      toast.success('Document supprimé')
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la suppression')
    }
  }

  const handleDownload = (id: string) => {
    window.open(`/api/documents/${id}/download`, '_blank')
  }

  // Statistics
  const stats = {
    total: documents.length,
    pending: documents.filter((d) => d.status === 'pending').length,
    verified: documents.filter((d) => d.status === 'verified').length,
    confidential: documents.filter((d) => d.is_confidential).length,
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Mes Documents</h1>
            <p className="text-gray-600 mt-1">Gérez vos documents en toute sécurité</p>
          </div>
          <button
            onClick={() => setShowUploadModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 transition-colors shadow-md hover:shadow-lg"
          >
            <ArrowUpTrayIcon className="h-5 w-5" />
            Importer un document
          </button>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              </div>
              <div className="p-3 bg-gray-100 rounded-full">
                <DocumentIcon className="h-6 w-6 text-gray-600" />
              </div>
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">En attente</p>
                <p className="text-2xl font-bold text-yellow-600">{stats.pending}</p>
              </div>
              <div className="p-3 bg-yellow-100 rounded-full">
                <DocumentIcon className="h-6 w-6 text-yellow-600" />
              </div>
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Vérifiés</p>
                <p className="text-2xl font-bold text-green-600">{stats.verified}</p>
              </div>
              <div className="p-3 bg-green-100 rounded-full">
                <DocumentIcon className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Confidentiels</p>
                <p className="text-2xl font-bold text-red-600">{stats.confidential}</p>
              </div>
              <div className="p-3 bg-red-100 rounded-full">
                <EyeIcon className="h-6 w-6 text-red-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">Catégorie</label>
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              >
                <option value="all">Toutes les catégories</option>
                <option value="cv">CV</option>
                <option value="cover_letter">Lettre de motivation</option>
                <option value="diploma">Diplôme</option>
                <option value="certificate">Certificat</option>
                <option value="id_card">Pièce d'identité</option>
                <option value="contract">Contrat</option>
                <option value="payslip">Fiche de paie</option>
                <option value="rgpd">RGPD</option>
                <option value="other">Autre</option>
              </select>
            </div>

            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">Statut</label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              >
                <option value="all">Tous les statuts</option>
                <option value="pending">En attente</option>
                <option value="verified">Vérifié</option>
                <option value="rejected">Rejeté</option>
                <option value="archived">Archivé</option>
              </select>
            </div>
          </div>
        </div>

        {/* Documents Grid */}
        <div className="bg-white rounded-lg shadow">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-jlc-purple-600"></div>
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center py-12">
              <DocumentIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">Aucun document</h3>
              <p className="mt-1 text-sm text-gray-500">Commencez par importer votre premier document.</p>
              <div className="mt-6">
                <button
                  onClick={() => setShowUploadModal(true)}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-jlc-purple-600 hover:bg-jlc-purple-700"
                >
                  <ArrowUpTrayIcon className="-ml-1 mr-2 h-5 w-5" />
                  Importer
                </button>
              </div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Document
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Catégorie
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Statut
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Visibilité
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Taille
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Créé le
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {documents.map((doc) => (
                    <tr key={doc.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <DocumentIcon className="h-8 w-8 text-gray-400 mr-3" />
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {doc.original_filename}
                            </div>
                            {doc.description && (
                              <div className="text-sm text-gray-500">{doc.description}</div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-600">
                          {CATEGORY_LABELS[doc.category] || doc.category}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${STATUS_COLORS[doc.status]}`}
                        >
                          {STATUS_LABELS[doc.status] || doc.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-600">
                          {VISIBILITY_LABELS[doc.visibility] || doc.visibility}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-600">
                          {(doc.file_size / 1024).toFixed(1)} KB
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-600">
                          {new Date(doc.created_at).toLocaleDateString('fr-FR')}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex gap-2 justify-end">
                          <button
                            onClick={() => handleDownload(doc.id)}
                            className="text-blue-600 hover:text-blue-900"
                            title="Télécharger"
                          >
                            <ArrowDownTrayIcon className="h-5 w-5" />
                          </button>
                          <button
                            onClick={() => handleDelete(doc.id, doc.original_filename)}
                            className="text-red-600 hover:text-red-900"
                            title="Supprimer"
                          >
                            <TrashIcon className="h-5 w-5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Upload Modal */}
        {showUploadModal && (
          <UploadDocumentModal
            isOpen={showUploadModal}
            onClose={() => setShowUploadModal(false)}
          />
        )}
      </div>
    </Layout>
  )
}

// Upload Modal Component
function UploadDocumentModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [uploadDocument, { isLoading }] = useUploadDocumentMutation()
  const [file, setFile] = useState<File | null>(null)
  const [formData, setFormData] = useState({
    category: 'other',
    visibility: 'private',
    description: '',
    tags: '',
    is_confidential: false,
    retention_period_days: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!file) {
      toast.error('Veuillez sélectionner un fichier')
      return
    }

    const data = new FormData()
    data.append('file', file)
    data.append('category', formData.category)
    data.append('visibility', formData.visibility)
    if (formData.description) data.append('description', formData.description)
    if (formData.tags) data.append('tags', formData.tags)
    data.append('is_confidential', formData.is_confidential.toString())
    if (formData.retention_period_days)
      data.append('retention_period_days', formData.retention_period_days)

    try {
      await uploadDocument(data).unwrap()
      toast.success('Document importé avec succès')
      onClose()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de l\'importation')
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        <div className="fixed inset-0 bg-black bg-opacity-50" onClick={onClose} />

        <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full p-6 z-10">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Importer un document</h3>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* File input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Fichier *</label>
              <input
                type="file"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.txt"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                Formats acceptés : PDF, DOC, DOCX, JPG, PNG, TXT (max 10MB)
              </p>
            </div>

            {/* Category */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Catégorie *</label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              >
                {Object.entries(CATEGORY_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </div>

            {/* Visibility */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Visibilité</label>
              <select
                value={formData.visibility}
                onChange={(e) => setFormData({ ...formData, visibility: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              >
                <option value="private">Privé</option>
                <option value="team">Équipe</option>
                <option value="public">Public</option>
              </select>
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                placeholder="Description du document..."
              />
            </div>

            {/* Confidential */}
            <div className="flex items-center">
              <input
                type="checkbox"
                checked={formData.is_confidential}
                onChange={(e) => setFormData({ ...formData, is_confidential: e.target.checked })}
                className="h-4 w-4 text-jlc-purple-600 focus:ring-jlc-purple-500 border-gray-300 rounded"
              />
              <label className="ml-2 text-sm text-gray-700">Document confidentiel</label>
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Annuler
              </button>
              <button
                type="submit"
                disabled={isLoading}
                className="flex-1 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 disabled:opacity-50"
              >
                {isLoading ? 'Import en cours...' : 'Importer'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
