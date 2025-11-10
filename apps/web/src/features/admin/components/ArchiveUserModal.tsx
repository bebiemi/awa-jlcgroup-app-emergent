import { Fragment, useState } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { ExclamationTriangleIcon, XMarkIcon } from '@heroicons/react/24/outline'
import { useArchiveUserMutation, useGetRetentionConfigQuery } from '../api/userDetailsApi'
import { toast } from 'react-hot-toast'

interface ArchiveUserModalProps {
  isOpen: boolean
  onClose: () => void
  user: {
    id: string
    username: string
    full_name?: string
    email: string
  } | null
  onSuccess?: () => void
}

export default function ArchiveUserModal({
  isOpen,
  onClose,
  user,
  onSuccess,
}: ArchiveUserModalProps) {
  const [reason, setReason] = useState('')
  const [archiveUser, { isLoading }] = useArchiveUserMutation()
  const { data: retentionConfig } = useGetRetentionConfigQuery()

  const handleArchive = async () => {
    if (!user) return

    try {
      await archiveUser({
        userId: user.id,
        reason: reason.trim() || undefined,
      }).unwrap()

      toast.success(
        `Utilisateur archivé. Suppression définitive prévue dans ${retentionConfig?.retention_days || 90} jours.`
      )
      onSuccess?.()
      onClose()
      setReason('')
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de l\'archivage de l\'utilisateur')
    }
  }

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
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
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                <div className="absolute right-4 top-4">
                  <button
                    onClick={onClose}
                    className="text-gray-400 hover:text-gray-500 transition-colors"
                  >
                    <XMarkIcon className="h-6 w-6" />
                  </button>
                </div>

                <div className="flex items-center gap-4 mb-4">
                  <div className="flex-shrink-0 flex items-center justify-center w-12 h-12 rounded-full bg-yellow-100">
                    <ExclamationTriangleIcon className="h-6 w-6 text-yellow-600" />
                  </div>
                  <Dialog.Title as="h3" className="text-lg font-semibold text-gray-900">
                    Archiver l'utilisateur
                  </Dialog.Title>
                </div>

                {user && (
                  <div className="mt-4 space-y-4">
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <p className="text-sm text-yellow-800">
                        <strong>Attention :</strong> L'utilisateur{' '}
                        <span className="font-semibold">{user.full_name || user.username}</span> (
                        {user.email}) sera archivé.
                      </p>
                      <p className="text-sm text-yellow-700 mt-2">
                        Le compte sera conservé pendant{' '}
                        <strong>{retentionConfig?.retention_days || 90} jours</strong> avant
                        suppression définitive.
                      </p>
                      <p className="text-sm text-yellow-700 mt-1">
                        Durant cette période, vous pourrez restaurer le compte depuis la section
                        "Archives".
                      </p>
                    </div>

                    <div>
                      <label
                        htmlFor="reason"
                        className="block text-sm font-medium text-gray-700 mb-2"
                      >
                        Raison (optionnel)
                      </label>
                      <textarea
                        id="reason"
                        rows={3}
                        value={reason}
                        onChange={(e) => setReason(e.target.value)}
                        placeholder="Indiquez la raison de l'archivage..."
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent resize-none"
                      />
                    </div>

                    <div className="flex gap-3 mt-6">
                      <button
                        type="button"
                        onClick={onClose}
                        disabled={isLoading}
                        className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Annuler
                      </button>
                      <button
                        type="button"
                        onClick={handleArchive}
                        disabled={isLoading}
                        className="flex-1 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {isLoading ? 'Archivage...' : 'Archiver'}
                      </button>
                    </div>
                  </div>
                )}
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  )
}
