import { Fragment, useState } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { XMarkIcon, CloudArrowUpIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

interface BulkImportUsersModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
}

interface ImportResult {
  success: boolean
  message: string
  total: number
  succeeded: number
  failed: number
  errors: Array<{
    line: number
    username: string
    email: string
    error: string
  }>
  created_users: Array<{
    username: string
    email: string
    password: string
    roles: string[]
  }>
}

export default function BulkImportUsersModal({ isOpen, onClose, onSuccess }: BulkImportUsersModalProps) {
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<any[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const [result, setResult] = useState<ImportResult | null>(null)

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (!selectedFile) return

    if (!selectedFile.name.endsWith('.csv')) {
      toast.error('Veuillez sélectionner un fichier CSV')
      return
    }

    setFile(selectedFile)
    setResult(null)

    // Parse CSV for preview
    const text = await selectedFile.text()
    const lines = text.split('\n').filter(l => l.trim())
    const headers = lines[0].split(',')
    const rows = lines.slice(1, 6).map(line => {
      const values = line.split(',')
      return headers.reduce((obj: any, header, index) => {
        obj[header.trim()] = values[index]?.trim() || ''
        return obj
      }, {})
    })
    setPreview(rows)
  }

  const handleUpload = async () => {
    if (!file) return

    setIsUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('/api/auth/admin/users/bulk-import', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: formData,
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Erreur lors de l\'import')
      }

      const data: ImportResult = await response.json()
      setResult(data)

      if (data.success) {
        toast.success(`${data.succeeded} utilisateur(s) importé(s) avec succès !`)
        onSuccess()
      } else {
        toast.error(`${data.succeeded} importé(s), ${data.failed} échec(s)`)
      }
    } catch (error: any) {
      toast.error(error.message || 'Erreur lors de l\'import')
    } finally {
      setIsUploading(false)
    }
  }

  const handleClose = () => {
    setFile(null)
    setPreview([])
    setResult(null)
    onClose()
  }

  const downloadTemplate = () => {
    const csvContent = `username,email,full_name,roles,phone
john_doe,john@entreprise.com,John Doe,interim,+241061234567
jane_smith,jane@jlcgroup.com,Jane Smith,collaborator,+241062345678`
    
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'template_import_users.csv'
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
    toast.success('Template téléchargé')
  }

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={handleClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-25" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-4xl transform overflow-hidden rounded-2xl bg-white p-6 shadow-xl transition-all">
                <div className="flex items-center justify-between mb-6">
                  <Dialog.Title as="h3" className="text-2xl font-bold text-gray-900">
                    Importer des utilisateurs en masse
                  </Dialog.Title>
                  <button
                    onClick={handleClose}
                    className="text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <XMarkIcon className="h-6 w-6" />
                  </button>
                </div>

                {!result ? (
                  <>
                    {/* Instructions */}
                    <div className="mb-6 p-4 bg-blue-50 rounded-lg">
                      <h4 className="font-semibold text-blue-900 mb-2">📋 Format CSV attendu :</h4>
                      <p className="text-sm text-blue-800 mb-2">
                        <code className="bg-blue-100 px-2 py-1 rounded">username,email,full_name,roles,phone</code>
                      </p>
                      <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
                        <li>Les rôles disponibles : <code>interim, collaborator, candidat, postulant, admin</code></li>
                        <li>Les domaines email autorisés seront vérifiés automatiquement</li>
                        <li>Les mots de passe sont générés automatiquement (16 caractères sécurisés)</li>
                        <li>Les emails d'invitation seront envoyés aux utilisateurs créés</li>
                      </ul>
                      <button
                        onClick={downloadTemplate}
                        className="mt-3 text-sm text-blue-600 hover:text-blue-800 font-medium"
                      >
                        📥 Télécharger un template CSV
                      </button>
                    </div>

                    {/* File upload */}
                    <div className="mb-6">
                      <label className="block">
                        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-jlc-purple-400 transition-colors cursor-pointer">
                          <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
                          <p className="mt-2 text-sm text-gray-600">
                            {file ? file.name : 'Cliquez pour sélectionner un fichier CSV'}
                          </p>
                          <input
                            type="file"
                            accept=".csv"
                            onChange={handleFileChange}
                            className="hidden"
                          />
                        </div>
                      </label>
                    </div>

                    {/* Preview */}
                    {preview.length > 0 && (
                      <div className="mb-6">
                        <h4 className="font-semibold text-gray-900 mb-3">Aperçu (5 premières lignes) :</h4>
                        <div className="overflow-x-auto border rounded-lg">
                          <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                              <tr>
                                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Username</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Email</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Nom complet</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Rôles</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Téléphone</th>
                              </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                              {preview.map((row, idx) => (
                                <tr key={idx}>
                                  <td className="px-4 py-2 text-sm text-gray-900">{row.username}</td>
                                  <td className="px-4 py-2 text-sm text-gray-900">{row.email}</td>
                                  <td className="px-4 py-2 text-sm text-gray-900">{row.full_name}</td>
                                  <td className="px-4 py-2 text-sm text-gray-900">{row.roles}</td>
                                  <td className="px-4 py-2 text-sm text-gray-900">{row.phone}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    )}

                    {/* Actions */}
                    <div className="flex justify-end gap-3">
                      <button
                        onClick={handleClose}
                        className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                      >
                        Annuler
                      </button>
                      <button
                        onClick={handleUpload}
                        disabled={!file || isUploading}
                        className="px-6 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                      >
                        {isUploading ? 'Import en cours...' : 'Importer'}
                      </button>
                    </div>
                  </>
                ) : (
                  <>
                    {/* Results */}
                    <div className="space-y-4">
                      {/* Summary */}
                      <div className={`p-4 rounded-lg ${result.success ? 'bg-green-50' : 'bg-yellow-50'}`}>
                        <div className="flex items-center gap-3">
                          {result.success ? (
                            <CheckCircleIcon className="h-6 w-6 text-green-600" />
                          ) : (
                            <XCircleIcon className="h-6 w-6 text-yellow-600" />
                          )}
                          <div>
                            <p className="font-semibold text-gray-900">{result.message}</p>
                            <p className="text-sm text-gray-600">
                              Total: {result.total} | Réussi: {result.succeeded} | Échec: {result.failed}
                            </p>
                          </div>
                        </div>
                      </div>

                      {/* Created users with passwords */}
                      {result.created_users && result.created_users.length > 0 && (
                        <div>
                          <h4 className="font-semibold text-gray-900 mb-3">✅ Utilisateurs créés :</h4>
                          <div className="bg-gray-50 rounded-lg p-4 max-h-60 overflow-y-auto">
                            <div className="space-y-2">
                              {result.created_users.map((user, idx) => (
                                <div key={idx} className="text-sm bg-white p-3 rounded border">
                                  <p className="font-medium text-gray-900">{user.username} ({user.email})</p>
                                  <p className="text-gray-600">Rôles: {user.roles.join(', ')}</p>
                                  <p className="text-red-600 font-mono text-xs mt-1">
                                    🔑 Mot de passe: <span className="select-all">{user.password}</span>
                                  </p>
                                  <p className="text-xs text-gray-500 mt-1">⚠️ Copiez ce mot de passe maintenant, il ne sera plus affiché</p>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Errors */}
                      {result.errors && result.errors.length > 0 && (
                        <div>
                          <h4 className="font-semibold text-red-900 mb-3">❌ Erreurs :</h4>
                          <div className="bg-red-50 rounded-lg p-4 max-h-60 overflow-y-auto">
                            <div className="space-y-2">
                              {result.errors.map((error, idx) => (
                                <div key={idx} className="text-sm text-red-800">
                                  <span className="font-medium">Ligne {error.line}:</span> {error.username} ({error.email}) - {error.error}
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex justify-end gap-3 mt-6">
                      <button
                        onClick={handleClose}
                        className="px-6 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 transition-colors"
                      >
                        Fermer
                      </button>
                    </div>
                  </>
                )}
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  )
}
