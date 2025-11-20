/**
 * Hooks factorisés pour la gestion des documents
 * Architecture IAM unifiée - Zéro valeur en dur
 */
import { useMemo } from 'react'
import { 
  useListDocumentsQuery, 
  useUploadDocumentMutation,
  useDeleteDocumentMutation,
  useUpdateDocumentMutation,
  Document 
} from '@/features/documents/api/documentsApi'
import { useGetReferenceValuesQuery } from '@/features/config/api/referencesApi'
import { usePermissions } from './usePermission'

/**
 * Hook pour récupérer les types de documents depuis le référentiel dynamique
 * @returns Types de documents configurés en admin
 */
export const useDocumentTypes = () => {
  const { data, isLoading, error } = useGetReferenceValuesQuery('documents_types')
  
  return {
    documentTypes: data || [],
    isLoading,
    error,
  }
}

/**
 * Hook pour gérer les permissions de visibilité des documents
 * Basé sur IAM dynamique, pas de valeurs en dur
 */
export const useDocumentVisibilityPermissions = () => {
  const { permissions } = usePermissions([
    'documents.read.own',
    'documents.read.all',
    'documents.view.all',
    'documents.manage.all',
    'documents.view_cv.all', // Permission spécifique RRH/Recrutement
  ])

  return {
    canViewOwnDocuments: permissions['documents.read.own'],
    canViewAllDocuments: permissions['documents.read.all'] || permissions['documents.view.all'],
    canManageAllDocuments: permissions['documents.manage.all'],
    canViewAllCV: permissions['documents.view_cv.all'], // RRH/Recrutement
  }
}

/**
 * Hook pour filtrer les documents selon les permissions IAM
 * @param documents Liste brute des documents
 * @param currentUserId ID de l'utilisateur connecté
 * @returns Documents filtrés selon les permissions
 */
export const useFilteredDocuments = (
  documents: Document[] | undefined,
  currentUserId: string | undefined
): Document[] => {
  const { 
    canViewAllDocuments, 
    canManageAllDocuments,
    canViewAllCV 
  } = useDocumentVisibilityPermissions()

  return useMemo(() => {
    if (!documents || !currentUserId) return []

    // SuperAdmin/Admin : voir tous les documents
    if (canManageAllDocuments || canViewAllDocuments) {
      return documents
    }

    // RRH/Recrutement : voir ses documents + tous les CV
    if (canViewAllCV) {
      return documents.filter(
        (doc) => 
          doc.user_id === currentUserId || // Ses propres documents
          doc.category === 'cv' || // Tous les CV
          doc.tags?.includes('cv') // Documents tagués CV
      )
    }

    // Utilisateur normal : seulement ses documents
    return documents.filter((doc) => doc.user_id === currentUserId)
  }, [documents, currentUserId, canViewAllDocuments, canManageAllDocuments, canViewAllCV])
}

/**
 * Hook principal pour gérer les documents avec toute la logique métier
 * @returns Fonctions et état pour la gestion des documents
 */
export const useDocuments = () => {
  const { data: documents, isLoading, error, refetch } = useListDocumentsQuery({})
  const [uploadDocument, { isLoading: isUploading }] = useUploadDocumentMutation()
  const [deleteDocument, { isLoading: isDeleting }] = useDeleteDocumentMutation()
  const [updateDocument, { isLoading: isUpdating }] = useUpdateDocumentMutation()
  
  const { documentTypes } = useDocumentTypes()

  /**
   * Upload avec tag automatique selon le type
   * @param file Fichier à uploader
   * @param category Type de document (depuis référentiel)
   * @param description Description optionnelle
   */
  const handleUpload = async (
    file: File, 
    category: string,
    description?: string
  ) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('category', category)
    
    if (description) {
      formData.append('description', description)
    }

    // L'upload invalide automatiquement le cache RTK Query
    // → Rafraîchissement automatique de la liste
    await uploadDocument(formData).unwrap()
    
    // Le badge "Documents manquants" se mettra à jour automatiquement
    // grâce à l'invalidation du tag 'Documents'
  }

  /**
   * Suppression avec rafraîchissement automatique
   */
  const handleDelete = async (documentId: string) => {
    await deleteDocument(documentId).unwrap()
    // Invalidation automatique du cache RTK Query
  }

  /**
   * Mise à jour avec rafraîchissement automatique
   */
  const handleUpdate = async (documentId: string, updates: any) => {
    await updateDocument({ id: documentId, data: updates }).unwrap()
    // Invalidation automatique du cache RTK Query
  }

  return {
    documents: documents || [],
    documentTypes,
    isLoading,
    isUploading,
    isDeleting,
    isUpdating,
    error,
    refetch,
    handleUpload,
    handleDelete,
    handleUpdate,
  }
}

/**
 * Hook pour compter les documents manquants selon le profil
 * Utilise le référentiel pour déterminer les documents requis
 */
export const useMissingDocuments = (userDocuments: Document[]) => {
  const { documentTypes } = useDocumentTypes()

  return useMemo(() => {
    // Filtrer les types requis (configurés en admin)
    const requiredTypes = documentTypes.filter((type: any) => type.required === true)
    
    // Vérifier quels types manquent
    const missingTypes = requiredTypes.filter((type: any) => {
      return !userDocuments.some(
        (doc) => doc.category === type.code || doc.tags?.includes(type.code)
      )
    })

    return {
      missingCount: missingTypes.length,
      missingTypes,
      requiredTypes,
    }
  }, [userDocuments, documentTypes])
}
