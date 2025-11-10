import { Fragment, useState } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { ArrowPathIcon, XMarkIcon } from '@heroicons/react/24/outline'
import { useRestoreUserMutation } from '../api/userDetailsApi'
import { toast } from 'react-hot-toast'

interface RestoreUserModalProps {
  isOpen: boolean
  onClose: () => void
  user: {
    id: string
    username: string
    full_name?: string
    email: string
    deletion_scheduled_at?: string
  } | null
  onSuccess?: () => void
}

export default function RestoreUserModal({
  isOpen,
  onClose,
  user,
  onSuccess,
}: RestoreUserModalProps) {
  const [reason, setReason] = useState('')
  const [restoreUser, { isLoading }] = useRestoreUserMutation()

  const handleRestore = async () => {
    if (!user) return

    try {
      await restoreUser({
        userId: user.id,
        reason: reason.trim() || undefined,
      }).unwrap()

      toast.success('Utilisateur restauré avec succès')
      onSuccess?.()
      onClose()
      setReason('')
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la restauration de l\'utilisateur')
    }
  }

  const getDaysRemaining = () => {
    if (!user?.deletion_scheduled_at) return null
    const deletionDate = new Date(user.deletion_scheduled_at)
    const now = new Date()
    const diffTime = deletionDate.getTime() - now.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays > 0 ? diffDays : 0
  }

  const daysRemaining = getDaysRemaining()

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
                  <div className="flex-shrink-0 flex items-center justify-center w-12 h-12 rounded-full bg-green-100">
                    <ArrowPathIcon className="h-6 w-6 text-green-600" />
                  </div>
                  <Dialog.Title as="h3" className="text-lg font-semibold text-gray-900">
                    Restaurer l'utilisateur
                  </Dialog.Title>
                </div>

                {user && (
                  <div className="mt-4 space-y-4">
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <p className="text-sm text-green-800">
                        Restaurer le compte de{' '}
                        <span className="font-semibold">{user.full_name || user.username}</span> (
                        {user.email}) ?
                      </p>
                      {daysRemaining !== null && (
                        <p className="text-sm text-green-700 mt-2">
                          <strong>Suppression définitive prévue dans {daysRemaining} jour(s)</strong>
                        </p>
                      )}
                      <p className="text-sm text-green-700 mt-1">
                        Le compte sera réactivé et l'utilisateur pourra à nouveau se connecter.
                      </p>
                    </div>

                    <div>
                      <label
                        htmlFor="restore-reason"
                        className="block text-sm font-medium text-gray-700 mb-2"
                      >
                        Raison (optionnel)
                      </label>
                      <textarea
                        id="restore-reason"
                        rows={3}
                        value={reason}
                        onChange={(e) => setReason(e.target.value)}
                        placeholder="Indiquez la raison de la restauration..."
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
                        onClick={handleRestore}
                        disabled={isLoading}
                        className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {isLoading ? 'Restauration...' : 'Restaurer'}
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
