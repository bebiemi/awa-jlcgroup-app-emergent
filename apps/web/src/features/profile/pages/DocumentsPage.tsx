/**
 * DocumentsPage - Page dédiée à la gestion complète des documents
 * 
 * Features:
 * - Catégorisation des documents (Administratifs, Personnels, Professionnels)
 * - Recherche et filtrage
 * - Upload multi-fichiers
 * - Prévisualisation
 * - Préparation pour intégrations tierces (API/webhooks)
 */
import { useState } from 'react'
import Layout from '@/components/Layout'
import Card from '@/components/Card'
import Button from '@/components/Button'
import { useListDocumentsQuery, useUploadDocumentMutation, useDeleteDocumentMutation } from '@/features/documents/api/documentsApi'
import { useGetDocumentTypesQuery } from '../api/referencesApi'
import {
  DocumentTextIcon,
  FolderIcon,
  MagnifyingGlassIcon,
  ArrowUpTrayIcon,
  TrashIcon,
  EyeIcon,
  FunnelIcon,
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

// Catégories de documents
const DOCUMENT_CATEGORIES = {
  administrative: {
    label: 'Documents Administratifs',
    icon: '📋',
    color: 'bg-blue-100 text-blue-800 border-blue-300',
    types: ['carte_identite', 'passeport', 'permis_conduire', 'carte_sejour', 'carte_vitale'],
  },
  professional: {
    label: 'Documents Professionnels',
    icon: '💼',
    color: 'bg-purple-100 text-purple-800 border-purple-300',
    types: ['cv', 'lettre_motivation', 'diplome', 'certificat', 'attestation_travail'],
  },
  personal: {
    label: 'Documents Personnels',
    icon: '📄',
    color: 'bg-green-100 text-green-800 border-green-300',
    types: ['justificatif_domicile', 'rib', 'attestation_assurance', 'autre'],
  },
}

export default function DocumentsPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [selectedType, setSelectedType] = useState<string>('all')
  const [uploadingFile, setUploadingFile] = useState<File | null>(null)
  const [selectedDocType, setSelectedDocType] = useState<string>('cv')

  const { data: documentsData, isLoading } = useListDocumentsQuery({})
  const { data: documentTypesData } = useGetDocumentTypesQuery({ requiredOnly: false })
  const [uploadDocument, { isLoading: isUploading }] = useUploadDocumentMutation()
  const [deleteDocument, { isLoading: isDeleting }] = useDeleteDocumentMutation()

  const userDocuments = documentsData || []
  const allDocumentTypes = documentTypesData?.data || []

  // Fonction pour catégoriser un document
  const getCategoryForType = (docType: string): string => {
    for (const [categoryKey, categoryConfig] of Object.entries(DOCUMENT_CATEGORIES)) {
      if (categoryConfig.types.includes(docType)) {
        return categoryKey
      }
    }
    return 'personal'
  }

  // Filtrer les documents
  const filteredDocuments = userDocuments.filter((doc: any) => {
    const matchesSearch = 
      (doc.filename?.toLowerCase() || '').includes(searchQuery.toLowerCase()) ||
      (doc.type?.toLowerCase() || '').includes(searchQuery.toLowerCase())
    
    const docCategory = getCategoryForType(doc.type || doc.document_type)
    const matchesCategory = selectedCategory === 'all' || docCategory === selectedCategory
    
    const matchesType = selectedType === 'all' || doc.type === selectedType || doc.document_type === selectedType

    return matchesSearch && matchesCategory && matchesType
  })

  // Grouper par catégorie
  const documentsByCategory = {
    administrative: filteredDocuments.filter((doc: any) => getCategoryForType(doc.type || doc.document_type) === 'administrative'),
    professional: filteredDocuments.filter((doc: any) => getCategoryForType(doc.type || doc.document_type) === 'professional'),
    personal: filteredDocuments.filter((doc: any) => getCategoryForType(doc.type || doc.document_type) === 'personal'),
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      // Valider taille (5MB max)
      if (file.size > 5 * 1024 * 1024) {
        toast.error('❌ Fichier trop volumineux (max 5MB)')
        return
      }
      setUploadingFile(file)
    }
  }

  const handleUpload = async () => {
    if (!uploadingFile) return

    try {
      await uploadDocument({
        file: uploadingFile,
        document_type: selectedDocType
      }).unwrap()
      
      toast.success('✅ Document uploadé avec succès')
      setUploadingFile(null)
      refetch()
    } catch (error: any) {
      toast.error(`❌ ${error?.data?.detail || 'Erreur lors de l\'upload'}`)
    }
  }

  const handleDelete = async (documentId: string) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer ce document ?')) {
      return
    }

    try {
      await deleteDocument(documentId).unwrap()
      toast.success('✅ Document supprimé')
      refetch()
    } catch (error: any) {
      toast.error(`❌ ${error?.data?.detail || 'Erreur lors de la suppression'}`)
    }
  }

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestion des Documents</h1>
          <p className="text-gray-600 mt-1">
            Centralisez tous vos documents professionnels et administratifs
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total</p>
                <p className="text-2xl font-bold text-gray-900">{userDocuments.length}</p>
              </div>
              <DocumentTextIcon className="h-10 w-10 text-gray-400" />
            </div>
          </Card>
          {Object.entries(DOCUMENT_CATEGORIES).map(([key, config]) => (
            <Card key={key}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{config.label.split(' ')[1]}</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {documentsByCategory[key as keyof typeof documentsByCategory].length}
                  </p>
                </div>
                <div className="text-3xl">{config.icon}</div>
              </div>
            </Card>
          ))}
        </div>

        {/* Upload Section */}
        <Card>
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <ArrowUpTrayIcon className="h-5 w-5" />
              Uploader un document
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Type de document
                </label>
                <select
                  value={selectedDocType}
                  onChange={(e) => setSelectedDocType(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
                >
                  {allDocumentTypes.map((docType: any) => (
                    <option key={docType.code} value={docType.code}>
                      {docType.label_fr}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Fichier
                </label>
                <input
                  type="file"
                  onChange={handleFileSelect}
                  accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
                />
              </div>
              <div className="flex items-end">
                <Button
                  variant="primary"
                  onClick={handleUpload}
                  disabled={!uploadingFile || isUploading}
                  isLoading={isUploading}
                  className="w-full"
                >
                  <ArrowUpTrayIcon className="h-5 w-5 mr-2" />
                  Uploader
                </Button>
              </div>
            </div>
            {uploadingFile && (
              <div className="flex items-center gap-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <DocumentTextIcon className="h-5 w-5 text-blue-600" />
                <span className="text-sm text-blue-900">
                  {uploadingFile.name} ({(uploadingFile.size / 1024).toFixed(2)} KB)
                </span>
              </div>
            )}
          </div>
        </Card>

        {/* Search and Filters */}
        <Card>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-1">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Rechercher un document..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
                />
              </div>
            </div>
            <div>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              >
                <option value="all">Toutes les catégories</option>
                {Object.entries(DOCUMENT_CATEGORIES).map(([key, config]) => (
                  <option key={key} value={key}>
                    {config.icon} {config.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              >
                <option value="all">Tous les types</option>
                {allDocumentTypes.map((docType: any) => (
                  <option key={docType.code} value={docType.code}>
                    {docType.label_fr}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </Card>

        {/* Documents Grid by Category */}
        {Object.entries(DOCUMENT_CATEGORIES).map(([categoryKey, categoryConfig]) => {
          const categoryDocs = documentsByCategory[categoryKey as keyof typeof documentsByCategory]
          
          if (categoryDocs.length === 0 && selectedCategory !== 'all' && selectedCategory !== categoryKey) {
            return null
          }

          return (
            <div key={categoryKey}>
              <div className="flex items-center gap-2 mb-4">
                <div className="text-2xl">{categoryConfig.icon}</div>
                <h2 className="text-xl font-bold text-gray-900">{categoryConfig.label}</h2>
                <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full">
                  {categoryDocs.length}
                </span>
              </div>

              {categoryDocs.length === 0 ? (
                <Card>
                  <div className="text-center py-8 text-gray-500">
                    <FolderIcon className="h-12 w-12 mx-auto mb-3 text-gray-400" />
                    <p className="text-sm">Aucun document dans cette catégorie</p>
                  </div>
                </Card>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {categoryDocs.map((doc: any) => (
                    <Card key={doc.id} className="hover:shadow-md transition-shadow">
                      <div className="space-y-3">
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-2">
                            <DocumentTextIcon className="h-5 w-5 text-gray-400" />
                            <div>
                              <p className="font-medium text-gray-900 text-sm truncate">
                                {doc.filename || doc.original_filename || 'Document sans nom'}
                              </p>
                              <p className="text-xs text-gray-500">
                                {doc.type || doc.document_type}
                              </p>
                            </div>
                          </div>
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            doc.validation_status === 'validated'
                              ? 'bg-green-100 text-green-700'
                              : doc.validation_status === 'rejected'
                              ? 'bg-red-100 text-red-700'
                              : 'bg-yellow-100 text-yellow-700'
                          }`}>
                            {doc.validation_status === 'validated' ? '✓' : doc.validation_status === 'rejected' ? '✗' : '⏳'}
                          </span>
                        </div>

                        <div className="text-xs text-gray-500">
                          Uploadé le {new Date(doc.uploaded_at).toLocaleDateString('fr-FR')}
                        </div>

                        <div className="flex gap-2">
                          <Button
                            variant="secondary"
                            onClick={() => window.open(doc.file_url, '_blank')}
                            className="flex-1 text-sm py-1.5"
                          >
                            <EyeIcon className="h-4 w-4 mr-1" />
                            Voir
                          </Button>
                          <Button
                            variant="danger"
                            onClick={() => handleDelete(doc.id)}
                            disabled={isDeleting}
                            className="text-sm py-1.5 px-3"
                          >
                            <TrashIcon className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          )
        })}

        {/* Placeholder pour interconnexions futures */}
        <Card className="border-2 border-dashed border-gray-300 bg-gray-50">
          <div className="text-center py-8">
            <div className="text-4xl mb-3">🔗</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Interconnexions (À venir)
            </h3>
            <p className="text-sm text-gray-600">
              Bientôt : Synchronisation automatique avec applications tierces via API/webhooks
            </p>
            <p className="text-xs text-gray-500 mt-2">
              (Google Drive, Dropbox, Services RH externes, etc.)
            </p>
          </div>
        </Card>
      </div>
    </Layout>
  )
}
