import { useState } from 'react'
import { UserDetail, useGetUserDocumentsQuery, useVerifyDocumentMutation, useDeleteDocumentMutation } from '@/features/users/api/userDetailsApi'
import { DOCUMENT_TYPES, BADGE_VARIANTS, COLORS } from '@/constants/ui'
import { CheckCircleIcon, XCircleIcon, EyeIcon, TrashIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'
import { usePermissions } from '@/hooks/usePermission'

interface UserDocumentsTabProps {
  userId: string
  userDetail: UserDetail
}

export default function UserDocumentsTab({ userId }: UserDocumentsTabProps) {
  const { data: documents = [], isLoading } = useGetUserDocumentsQuery(userId)
  const [verifyDocument] = useVerifyDocumentMutation()
  const [deleteDocument] = useDeleteDocumentMutation()
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const { permissions } = usePermissions([
    'documents.read.all',
    'documents.verify.all',
    'documents.delete.all',
    'documents.download.all',
  ])
  const canRead = permissions['documents.read.all']
  const canVerify = permissions['documents.verify.all']
  const canDelete = permissions['documents.delete.all']
  const canPreview = permissions['documents.download.all'] || permissions['documents.read.all']

  const handleVerify = async (docId: string) => {
    try {
      await verifyDocument({ userId, docId }).unwrap()
      toast.success('Document vérifié avec succès')
    } catch (error: any) {
      toast.error(error?.data?.message || 'Erreur lors de la vérification')
    }
  }

  const handleDelete = async (docId: string) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce document ?')) return
    
    try {
      await deleteDocument({ userId, docId }).unwrap()
      toast.success('Document supprimé avec succès')
    } catch (error: any) {
      toast.error(error?.data?.message || 'Erreur lors de la suppression')
    }
  }

  const getDocumentTypeInfo = (type: string) => {
    const docType = Object.values(DOCUMENT_TYPES).find(dt => dt.code === type)
    return docType || DOCUMENT_TYPES.OTHER
  }

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-24 bg-gray-200 rounded-lg"></div>
        ))}
      </div>
    )
  }

  if (!canRead) return null

  return (
    <div className="space-y-4">
      {documents.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-gray-500">Aucun document uploadé</p>
        </div>
      ) : (
        documents.map((doc) => {
          const typeInfo = getDocumentTypeInfo(doc.type)
          return (
            <div key={doc.id} className="bg-white rounded-lg shadow p-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{typeInfo.icon}</span>
                    <div>
                      <h4 className="font-semibold text-gray-900">{typeInfo.label}</h4>
                      <p className="text-sm text-gray-500">{doc.file_name}</p>
                      <p className="text-xs text-gray-400">
                        Uploadé le {new Date(doc.uploaded_at).toLocaleString('fr-FR')}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {doc.verified ? (
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${BADGE_VARIANTS.success}`}>
                      <CheckCircleIcon className="h-4 w-4 inline mr-1" />
                      Vérifié
                    </span>
                  ) : (
                    canVerify && (
                      <button
                        onClick={() => handleVerify(doc.id)}
                        className="px-3 py-1 rounded-md text-xs font-semibold bg-blue-600 text-white hover:bg-blue-700"
                      >
                        Valider la conformité
                      </button>
                    )
                  )}
                  {canPreview && (
                    <button
                      onClick={() => setPreviewUrl(doc.url)}
                      className="p-2 rounded-md hover:bg-gray-100"
                      title="Prévisualiser"
                    >
                      <EyeIcon className="h-5 w-5 text-gray-600" />
                    </button>
                  )}
                  {canDelete && (
                    <button
                      onClick={() => handleDelete(doc.id)}
                      className="p-2 rounded-md hover:bg-red-50"
                      title="Supprimer"
                    >
                      <TrashIcon className="h-5 w-5 text-red-600" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          )
        })
      )}

      {/* Preview Modal */}
      {previewUrl && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-75" onClick={() => setPreviewUrl(null)}>
          <div className="max-w-4xl max-h-[90vh] bg-white rounded-lg p-4" onClick={(e) => e.stopPropagation()}>
            <iframe src={previewUrl} className="w-full h-[80vh]" />
            <button
              onClick={() => setPreviewUrl(null)}
              className="mt-4 w-full px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg"
            >
              Fermer
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
