/**
 * InlineDocumentUpload - Composant réutilisable pour upload de documents inline
 * 
 * Features:
 * - Upload simple avec drag & drop
 * - Validation format et taille
 * - Preview du fichier
 * - Messages d'erreur clairs
 * - Intégration avec profileApi
 */
import { useState, useRef } from 'react'
import { useUploadDocumentMutation } from '@/features/profile/api/profileApi'
import Button from './Button'
import { DocumentTextIcon, CheckCircleIcon, XCircleIcon, ArrowUpTrayIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

interface InlineDocumentUploadProps {
  documentType: string
  onUploadSuccess?: (documentId: string, filename: string) => void
  onUploadError?: (error: string) => void
  maxSizeMB?: number
  allowedFormats?: string[]
  label?: string
  helperText?: string
  className?: string
}

export default function InlineDocumentUpload({
  documentType,
  onUploadSuccess,
  onUploadError,
  maxSizeMB = 5,
  allowedFormats = ['pdf', 'doc', 'docx'],
  label = 'Uploader un document',
  helperText,
  className = ''
}: InlineDocumentUploadProps) {
  const [uploadDocument, { isLoading }] = useUploadDocumentMutation()
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const validateFile = (file: File): string | null => {
    // Vérifier taille
    const fileSizeMB = file.size / (1024 * 1024)
    if (fileSizeMB > maxSizeMB) {
      return `Fichier trop volumineux. Taille maximale : ${maxSizeMB}MB`
    }

    // Vérifier format
    const fileExtension = file.name.split('.').pop()?.toLowerCase()
    if (fileExtension && !allowedFormats.includes(fileExtension)) {
      return `Format non supporté. Formats acceptés : ${allowedFormats.join(', ').toUpperCase()}`
    }

    return null
  }

  const handleFileSelect = (file: File) => {
    const error = validateFile(file)
    if (error) {
      toast.error(error)
      if (onUploadError) onUploadError(error)
      return
    }

    setSelectedFile(file)
  }

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const file = e.dataTransfer.files?.[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      formData.append('document_type', documentType)

      const result = await uploadDocument(formData).unwrap()

      toast.success('✅ Document uploadé avec succès')
      
      if (onUploadSuccess) {
        onUploadSuccess(result.id, result.filename || selectedFile.name)
      }

      // Reset
      setSelectedFile(null)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    } catch (error: any) {
      console.error('Erreur upload:', error)
      const errorMsg = error?.data?.detail || error?.message || 'Erreur lors de l\'upload'
      toast.error(`❌ ${errorMsg}`)
      
      if (onUploadError) onUploadError(errorMsg)
    }
  }

  const handleCancel = () => {
    setSelectedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className={`space-y-3 ${className}`}>
      <label className="block text-sm font-medium text-gray-700">{label}</label>
      
      {/* Drag & Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
          isDragging
            ? 'border-jlc-purple-500 bg-jlc-purple-50'
            : 'border-gray-300 hover:border-jlc-purple-400'
        }`}
      >
        {!selectedFile ? (
          <>
            <DocumentTextIcon className="h-12 w-12 text-gray-400 mx-auto mb-3" />
            <p className="text-sm text-gray-600 mb-2">
              Glissez-déposez votre fichier ici ou
            </p>
            <Button
              type="button"
              variant="secondary"
              onClick={() => fileInputRef.current?.click()}
              disabled={isLoading}
            >
              <ArrowUpTrayIcon className="h-5 w-5 mr-2" />
              Choisir un fichier
            </Button>
            <input
              ref={fileInputRef}
              type="file"
              onChange={handleFileInputChange}
              accept={allowedFormats.map(f => `.${f}`).join(',')}
              className="hidden"
            />
          </>
        ) : (
          <div className="space-y-3">
            <div className="flex items-center justify-center gap-2 text-sm">
              <CheckCircleIcon className="h-5 w-5 text-green-500" />
              <span className="font-medium text-gray-900">{selectedFile.name}</span>
              <span className="text-gray-500">
                ({(selectedFile.size / (1024 * 1024)).toFixed(2)} MB)
              </span>
            </div>
            
            <div className="flex gap-3 justify-center">
              <Button
                type="button"
                variant="primary"
                onClick={handleUpload}
                isLoading={isLoading}
                disabled={isLoading}
              >
                {isLoading ? 'Upload...' : 'Confirmer l\'upload'}
              </Button>
              <Button
                type="button"
                variant="secondary"
                onClick={handleCancel}
                disabled={isLoading}
              >
                <XCircleIcon className="h-5 w-5 mr-2" />
                Annuler
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Helper Text */}
      {helperText && (
        <p className="text-xs text-gray-500">{helperText}</p>
      )}
      {!helperText && (
        <p className="text-xs text-gray-500">
          Formats acceptés : {allowedFormats.join(', ').toUpperCase()} • Taille max : {maxSizeMB}MB
        </p>
      )}
    </div>
  )
}
