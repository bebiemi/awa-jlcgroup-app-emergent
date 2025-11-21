import { useState, useRef } from 'react'
import { useListDocumentsQuery, useUploadDocumentMutation, useDeleteDocumentMutation } from '@/features/documents/api/documentsApi'
import { DocumentTextIcon, TrashIcon, ArrowUpTrayIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

export default function DocumentsSection() {
  const { data, isLoading } = useGetMyDocumentsQuery()
  const [uploadDocument] = useUploadDocumentMutation()
  const [deleteDocument] = useDeleteDocumentMutation()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [selectedDocType, setSelectedDocType] = useState('cv')
  const [uploading, setUploading] = useState(false)

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (file.size > 5 * 1024 * 1024) {
      toast.error('Fichier trop volumineux (max 5MB)')
      return
    }

    setUploading(true)
    try {
      await uploadDocument({ file, document_type: selectedDocType }).unwrap()
      toast.success('Document uploadé avec succès')
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de l\'upload')
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (docId: string, filename: string) => {
    if (!confirm(`Supprimer ${filename} ?`)) return

    try {
      await deleteDocument(docId).unwrap()
      toast.success('Document supprimé')
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la suppression')
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  const getDocumentTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      cv: 'CV',
      diploma: 'Diplôme',
      certificate: 'Certificat',
      id_card: 'Carte d\'identité',
      passport: 'Passeport',
      driving_license: 'Permis de conduire',
      other: 'Autre'
    }
    return labels[type] || type
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-jlc-purple-600"></div>
      </div>
    )
  }

  const documents = data?.documents || []

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 hover:border-jlc-purple-400 transition">
        <div className="text-center">
          <ArrowUpTrayIcon className="mx-auto h-12 w-12 text-gray-400" />
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Type de document
            </label>
            <select
              value={selectedDocType}
              onChange={(e) => setSelectedDocType(e.target.value)}
              className="mb-4 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
            >
              <option value="cv">CV</option>
              <option value="diploma">Diplôme</option>
              <option value="certificate">Certificat</option>
              <option value="id_card">Carte d'identité</option>
              <option value="passport">Passeport</option>
              <option value="driving_license">Permis de conduire</option>
              <option value="other">Autre</option>
            </select>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleFileSelect}
            accept=".pdf,.jpg,.jpeg,.png,.doc,.docx,.xls,.xlsx"
            className="hidden"
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="px-6 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 disabled:opacity-50 transition"
          >
            {uploading ? 'Upload en cours...' : 'Choisir un fichier'}
          </button>
          <p className="mt-2 text-xs text-gray-500">
            PDF, images, Word, Excel - Maximum 5MB
          </p>
        </div>
      </div>

      {/* Documents List */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Mes Documents ({documents.length})
        </h3>
        {documents.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <p>Aucun document uploadé</p>
          </div>
        ) : (
          <div className="space-y-3">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
              >
                <div className="flex items-center space-x-3 flex-1">
                  <DocumentTextIcon className="h-8 w-8 text-jlc-purple-600 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {doc.original_filename}
                    </p>
                    <p className="text-xs text-gray-500">
                      {getDocumentTypeLabel(doc.type)} • {formatFileSize(doc.file_size)} • {new Date(doc.uploaded_at).toLocaleDateString('fr-FR')}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(doc.id, doc.original_filename)}
                  className="ml-4 p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                  title="Supprimer"
                >
                  <TrashIcon className="h-5 w-5" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
