/**
 * Grouping Requests Page
 * Phase 4: Gestion des demandes de regroupement d'entreprises
 */
import { useState, useEffect } from 'react'
import Layout from '@/components/Layout'
import Card from '@/components/Card'
import Button from '@/components/Button'
import {
  BuildingOfficeIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  PlusIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

interface GroupingRequest {
  id: string
  entreprise_1_id: string
  entreprise_1_nom: string
  entreprise_2_id: string
  entreprise_2_nom: string
  requested_by: string
  requested_by_name: string
  requested_at: string
  status: 'pending' | 'approved' | 'rejected'
  reason?: string
  approvals: {
    entreprise_1: {
      approved: boolean
      approved_by?: string
      approved_by_name?: string
      approved_at?: string
    }
    entreprise_2: {
      approved: boolean
      approved_by?: string
      approved_by_name?: string
      approved_at?: string
    }
  }
  rejection_reason?: string
  rejected_by?: string
  rejected_at?: string
}

export default function GroupingRequestsPage() {
  const [requests, setRequests] = useState<GroupingRequest[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState<string>('pending')
  const [selectedRequest, setSelectedRequest] = useState<GroupingRequest | null>(null)
  const [showApproveModal, setShowApproveModal] = useState(false)
  const [showRejectModal, setShowRejectModal] = useState(false)
  const [rejectionReason, setRejectionReason] = useState('')
  const [notes, setNotes] = useState('')

  useEffect(() => {
    loadRequests()
  }, [statusFilter])

  const loadRequests = async () => {
    setIsLoading(true)
    try {
      const params = new URLSearchParams()
      if (statusFilter && statusFilter !== 'all') {
        params.append('status', statusFilter)
      }

      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/entreprises/grouping/my-requests?${params.toString()}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      )

      if (response.ok) {
        const data = await response.json()
        setRequests(data.requests || [])
      } else {
        toast.error('Erreur lors du chargement des demandes')
      }
    } catch (error) {
      console.error('Error loading requests:', error)
      toast.error('Erreur de connexion')
    } finally {
      setIsLoading(false)
    }
  }

  const handleApprove = async (request: GroupingRequest) => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/entreprises/grouping/${request.id}/approve`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          },
          body: JSON.stringify({ notes })
        }
      )

      if (response.ok) {
        const result = await response.json()
        toast.success(result.message || 'Demande approuvée avec succès')
        loadRequests()
        setShowApproveModal(false)
        setNotes('')
      } else {
        const error = await response.json()
        toast.error(error.detail || 'Erreur lors de l\'approbation')
      }
    } catch (error) {
      console.error('Error approving request:', error)
      toast.error('Erreur de connexion')
    }
  }

  const handleReject = async (request: GroupingRequest) => {
    if (!rejectionReason.trim()) {
      toast.error('Veuillez indiquer une raison de rejet')
      return
    }

    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/entreprises/grouping/${request.id}/reject`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          },
          body: JSON.stringify({ rejection_reason: rejectionReason })
        }
      )

      if (response.ok) {
        toast.success('Demande rejetée')
        loadRequests()
        setShowRejectModal(false)
        setRejectionReason('')
      } else {
        const error = await response.json()
        toast.error(error.detail || 'Erreur lors du rejet')
      }
    } catch (error) {
      console.error('Error rejecting request:', error)
      toast.error('Erreur de connexion')
    }
  }

  const getStatusBadge = (status: string) => {
    const badges = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
    }
    const labels = {
      pending: 'En attente',
      approved: 'Approuvé',
      rejected: 'Rejeté',
    }
    return (
      <span className={`px-3 py-1 text-xs font-medium rounded-full ${badges[status as keyof typeof badges]}`}>
        {labels[status as keyof typeof labels]}
      </span>
    )
  }

  if (isLoading) {
    return (
      <Layout>
        <div className="flex justify-center items-center py-12">
          <ArrowPathIcon className="h-8 w-8 animate-spin text-jlc-purple-600" />
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Demandes de Regroupement</h1>
          <p className="text-gray-600 mt-2">
            Gérez les demandes de regroupement entre vos entreprises liées
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">En attente</p>
                <p className="text-2xl font-bold text-gray-900">
                  {requests.filter(r => r.status === 'pending').length}
                </p>
              </div>
              <ClockIcon className="h-8 w-8 text-yellow-500" />
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Approuvées</p>
                <p className="text-2xl font-bold text-gray-900">
                  {requests.filter(r => r.status === 'approved').length}
                </p>
              </div>
              <CheckCircleIcon className="h-8 w-8 text-green-500" />
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Rejetées</p>
                <p className="text-2xl font-bold text-gray-900">
                  {requests.filter(r => r.status === 'rejected').length}
                </p>
              </div>
              <XCircleIcon className="h-8 w-8 text-red-500" />
            </div>
          </Card>
        </div>

        {/* Filter */}
        <Card>
          <div className="flex items-center justify-between">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
            >
              <option value="all">Toutes les demandes</option>
              <option value="pending">En attente</option>
              <option value="approved">Approuvées</option>
              <option value="rejected">Rejetées</option>
            </select>

            <Button onClick={loadRequests} variant="secondary">
              <ArrowPathIcon className="h-5 w-5 mr-2" />
              Actualiser
            </Button>
          </div>
        </Card>

        {/* Requests List */}
        <div className="space-y-4">
          {requests.length === 0 ? (
            <Card>
              <p className="text-center text-gray-600 py-8">
                Aucune demande de regroupement
              </p>
            </Card>
          ) : (
            requests.map((request) => (
              <Card key={request.id}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <BuildingOfficeIcon className="h-5 w-5 text-gray-500" />
                      <h3 className="text-lg font-semibold text-gray-900">
                        {request.entreprise_1_nom} ↔ {request.entreprise_2_nom}
                      </h3>
                      {getStatusBadge(request.status)}
                    </div>

                    <p className="text-sm text-gray-600 mb-2">
                      Demandé par <strong>{request.requested_by_name}</strong> le{' '}
                      {new Date(request.requested_at).toLocaleDateString('fr-FR')}
                    </p>

                    {request.reason && (
                      <p className="text-sm text-gray-700 mb-3 italic">"{request.reason}"</p>
                    )}

                    {/* Approval Status */}
                    <div className="grid grid-cols-2 gap-4 mt-4">
                      <div
                        className={`p-3 rounded-lg border ${
                          request.approvals.entreprise_1.approved
                            ? 'bg-green-50 border-green-200'
                            : 'bg-gray-50 border-gray-200'
                        }`}
                      >
                        <p className="text-xs font-semibold text-gray-700 mb-1">
                          {request.entreprise_1_nom}
                        </p>
                        {request.approvals.entreprise_1.approved ? (
                          <div className="flex items-center text-green-700">
                            <CheckCircleIcon className="h-4 w-4 mr-1" />
                            <span className="text-xs">Approuvé</span>
                          </div>
                        ) : (
                          <div className="flex items-center text-gray-600">
                            <ClockIcon className="h-4 w-4 mr-1" />
                            <span className="text-xs">En attente</span>
                          </div>
                        )}
                      </div>

                      <div
                        className={`p-3 rounded-lg border ${
                          request.approvals.entreprise_2.approved
                            ? 'bg-green-50 border-green-200'
                            : 'bg-gray-50 border-gray-200'
                        }`}
                      >
                        <p className="text-xs font-semibold text-gray-700 mb-1">
                          {request.entreprise_2_nom}
                        </p>
                        {request.approvals.entreprise_2.approved ? (
                          <div className="flex items-center text-green-700">
                            <CheckCircleIcon className="h-4 w-4 mr-1" />
                            <span className="text-xs">Approuvé</span>
                          </div>
                        ) : (
                          <div className="flex items-center text-gray-600">
                            <ClockIcon className="h-4 w-4 mr-1" />
                            <span className="text-xs">En attente</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {request.status === 'rejected' && request.rejection_reason && (
                      <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                        <p className="text-xs font-semibold text-red-900">Raison du rejet:</p>
                        <p className="text-sm text-red-700">{request.rejection_reason}</p>
                      </div>
                    )}
                  </div>

                  {request.status === 'pending' && (
                    <div className="flex space-x-2 ml-4">
                      <Button
                        onClick={() => {
                          setSelectedRequest(request)
                          setShowApproveModal(true)
                        }}
                        variant="primary"
                        className="bg-green-600 hover:bg-green-700"
                      >
                        <CheckCircleIcon className="h-5 w-5 mr-1" />
                        Approuver
                      </Button>
                      <Button
                        onClick={() => {
                          setSelectedRequest(request)
                          setShowRejectModal(true)
                        }}
                        variant="secondary"
                        className="border-red-300 text-red-600 hover:bg-red-50"
                      >
                        <XCircleIcon className="h-5 w-5 mr-1" />
                        Rejeter
                      </Button>
                    </div>
                  )}
                </div>
              </Card>
            ))
          )}
        </div>
      </div>

      {/* Approve Modal - Simplifié pour l'instant */}
      {showApproveModal && selectedRequest && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Approuver le regroupement</h3>
            <p className="text-sm text-gray-600 mb-4">
              Vous allez approuver le regroupement entre <strong>{selectedRequest.entreprise_1_nom}</strong> et{' '}
              <strong>{selectedRequest.entreprise_2_nom}</strong>.
            </p>
            <div className="flex space-x-3">
              <Button
                onClick={() => {
                  setShowApproveModal(false)
                  setSelectedRequest(null)
                }}
                variant="secondary"
              >
                Annuler
              </Button>
              <Button
                onClick={() => handleApprove(selectedRequest)}
                variant="primary"
                className="bg-green-600 hover:bg-green-700"
              >
                Confirmer
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Reject Modal */}
      {showRejectModal && selectedRequest && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Rejeter le regroupement</h3>
            <textarea
              value={rejectionReason}
              onChange={(e) => setRejectionReason(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 mb-4"
              rows={4}
              placeholder="Raison du rejet (obligatoire)"
              required
            />
            <div className="flex space-x-3">
              <Button
                onClick={() => {
                  setShowRejectModal(false)
                  setSelectedRequest(null)
                  setRejectionReason('')
                }}
                variant="secondary"
              >
                Annuler
              </Button>
              <Button
                onClick={() => handleReject(selectedRequest)}
                variant="primary"
                className="bg-red-600 hover:bg-red-700"
                disabled={!rejectionReason.trim()}
              >
                Rejeter
              </Button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  )
}
