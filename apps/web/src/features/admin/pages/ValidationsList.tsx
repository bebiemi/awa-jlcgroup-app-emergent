import Layout from '@/components/Layout'
import Card from '@/components/Card'
import Button from '@/components/Button'
import { useGetValidationsQuery, useApproveValidationMutation, useRejectValidationMutation } from '../api/validationApi'
import { useReferences } from '@/hooks/useReferences'
import { useMemo, useState } from 'react'
import { CheckIcon, XMarkIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'
import clsx from 'clsx'
import { useAppConfig } from '@/hooks/useAppConfig'

export default function ValidationsList() {
  const { validationStatuses } = useAppConfig()
  const { data: validationStatusesRefs = [] } = useReferences('validation_statuses')

  const validationStatusesConfig = useMemo(() => {
    const resolveStatus = (target: string) =>
      validationStatusesRefs.find(vs => vs.code === target)?.code ||
      validationStatuses.find(status => status.toLowerCase() === target.toLowerCase()) ||
      target

    const fallback = validationStatuses[0] || validationStatusesRefs[0]?.code || 'pending'

    return {
      pending: resolveStatus('pending') || fallback,
      approved: resolveStatus('approved') || fallback,
      rejected: resolveStatus('rejected') || fallback,
    }
  }, [validationStatuses, validationStatusesRefs])

  const { pending: pendingStatus, approved: approvedStatus, rejected: rejectedStatus } = validationStatusesConfig

  const [statusFilter, setStatusFilter] = useState<string>(pendingStatus)
  const [selectedValidation, setSelectedValidation] = useState<string | null>(null)
  const [showApproveModal, setShowApproveModal] = useState(false)
  const [showRejectModal, setShowRejectModal] = useState(false)
  const [comment, setComment] = useState('')

  const { data, isLoading, refetch } = useGetValidationsQuery({
    status: statusFilter || undefined,
    page: 1,
    page_size: 50,
  })

  const [approveValidation, { isLoading: isApproving }] = useApproveValidationMutation()
  const [rejectValidation, { isLoading: isRejecting }] = useRejectValidationMutation()

  const handleApprove = async () => {
    if (!selectedValidation) return

    try {
      await approveValidation({
        id: selectedValidation,
        comment: comment || undefined,
      }).unwrap()
      toast.success('Compte approuvé avec succès')
      setShowApproveModal(false)
      setComment('')
      setSelectedValidation(null)
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Échec de l’approbation')
    }
  }

  const handleReject = async () => {
    if (!selectedValidation || !comment) {
      toast.error('Veuillez fournir un motif de refus')
      return
    }

    try {
      await rejectValidation({
        id: selectedValidation,
        comment,
      }).unwrap()
      toast.success('Compte refusé')
      setShowRejectModal(false)
      setComment('')
      setSelectedValidation(null)
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Échec du refus')
    }
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Gestion des Validations
            </h1>
            <p className="mt-2 text-gray-600">
              Approuver ou refuser les demandes de compte
            </p>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex space-x-4">
            <button
              onClick={() => setStatusFilter(pendingStatus)}
              className={clsx(
                'px-4 py-2 rounded-lg font-medium transition-colors',
                statusFilter === pendingStatus
                  ? 'bg-jlc-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              )}
            >
              En attente ({data?.items.filter(v => v.status === pendingStatus).length || 0})
            </button>
            <button
              onClick={() => setStatusFilter(approvedStatus)}
              className={clsx(
                'px-4 py-2 rounded-lg font-medium transition-colors',
                statusFilter === approvedStatus
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              )}
            >
              Approuvées
            </button>
            <button
              onClick={() => setStatusFilter(rejectedStatus)}
              className={clsx(
                'px-4 py-2 rounded-lg font-medium transition-colors',
                statusFilter === rejectedStatus
                  ? 'bg-red-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              )}
            >
              Refusées
            </button>
            <button
              onClick={() => setStatusFilter('')}
              className={clsx(
                'px-4 py-2 rounded-lg font-medium transition-colors',
                !statusFilter
                  ? 'bg-gray-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              )}
            >
              Toutes
            </button>
          </div>
        </div>

        {/* Validations Table */}
        <Card>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
            </div>
          ) : data && data.items.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Utilisateur
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Statut
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {data.items.map((validation) => (
                    <tr key={validation.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {validation.user_name || 'N/A'}
                          </div>
                          <div className="text-sm text-gray-500">
                            {validation.user_email}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={clsx(
                          'px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full',
                          validation.validation_type === 'interim'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-purple-100 text-purple-800'
                        )}>
                          {validation.validation_type === 'interim' ? 'Intérimaire' : 'Entreprise'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={clsx(
                          'px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full',
                          validation.status === pendingStatus && 'bg-yellow-100 text-yellow-800',
                          validation.status === approvedStatus && 'bg-green-100 text-green-800',
                          validation.status === rejectedStatus && 'bg-red-100 text-red-800'
                        )}>
                          {validation.status === pendingStatus && 'En attente'}
                          {validation.status === approvedStatus && 'Approuvé'}
                          {validation.status === rejectedStatus && 'Refusé'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(validation.created_at).toLocaleDateString('fr-FR')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        {validation.status === pendingStatus && (
                          <div className="flex space-x-2">
                            <button
                              onClick={() => {
                                setSelectedValidation(validation.id)
                                setShowApproveModal(true)
                              }}
                              className="text-green-600 hover:text-green-900 flex items-center"
                            >
                              <CheckIcon className="h-5 w-5 mr-1" />
                              Approuver
                            </button>
                            <button
                              onClick={() => {
                                setSelectedValidation(validation.id)
                                setShowRejectModal(true)
                              }}
                              className="text-red-600 hover:text-red-900 flex items-center"
                            >
                              <XMarkIcon className="h-5 w-5 mr-1" />
                              Refuser
                            </button>
                          </div>
                        )}
                          {validation.status !== pendingStatus && (
                          <span className="text-gray-400">Traité</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-center text-gray-500 py-12">
              Aucune validation trouvée
            </p>
          )}
        </Card>
      </div>

      {/* Approve Modal */}
      {showApproveModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-semibold mb-4">Approuver le compte</h3>
            <p className="text-gray-600 mb-4">
              Êtes-vous sûr de vouloir approuver ce compte?
            </p>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Commentaire (optionnel)
              </label>
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                rows={3}
                placeholder="Ajouter un commentaire..."
              />
            </div>
            <div className="flex justify-end space-x-3">
              <Button
                variant="secondary"
                onClick={() => {
                  setShowApproveModal(false)
                  setComment('')
                }}
              >
                Annuler
              </Button>
              <Button
                variant="success"
                onClick={handleApprove}
                isLoading={isApproving}
              >
                Approuver
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Reject Modal */}
      {showRejectModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-semibold mb-4">Refuser le compte</h3>
            <p className="text-gray-600 mb-4">
              Veuillez indiquer le motif du refus:
            </p>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Motif du refus *
              </label>
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                rows={3}
                placeholder="Expliquez pourquoi ce compte est refusé..."
                required
              />
            </div>
            <div className="flex justify-end space-x-3">
              <Button
                variant="secondary"
                onClick={() => {
                  setShowRejectModal(false)
                  setComment('')
                }}
              >
                Annuler
              </Button>
              <Button
                variant="danger"
                onClick={handleReject}
                isLoading={isRejecting}
                disabled={!comment}
              >
                Refuser
              </Button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  )
}
