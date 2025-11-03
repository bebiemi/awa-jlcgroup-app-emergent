import { useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import Layout from '@/components/Layout'
import Modal from '@/components/Modal'
import {
  useGetMissionQuery,
  useGetMissionApplicationsQuery,
  useUpdateApplicationMutation,
  useShortlistApplicationMutation,
  type Application,
  type ApplicationStatus,
} from '../api/missionApi'
import {
  ArrowLeftIcon,
  UserIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  EyeIcon,
  StarIcon,
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

const STATUS_FILTERS = [
  { value: 'all', label: 'Toutes', count: 0 },
  { value: 'submitted', label: 'Nouvelles', count: 0 },
  { value: 'shortlisted', label: 'Présélectionnées', count: 0 },
  { value: 'interview_scheduled', label: 'Entretiens', count: 0 },
  { value: 'selected_for_client', label: 'Pour client', count: 0 },
  { value: 'selected_by_client', label: 'Retenues', count: 0 },
  { value: 'rejected', label: 'Rejetées', count: 0 },
]

const STATUS_LABELS: Record<ApplicationStatus, string> = {
  submitted: 'Nouvelle',
  received: 'Reçue',
  under_review: 'En analyse',
  shortlisted: 'Présélectionnée',
  rejected_initial: 'Rejetée',
  interview_scheduled: 'Entretien programmé',
  interview_completed: 'Entretien passé',
  selected_for_client: 'Pour client',
  rejected_after_interview: 'Rejetée',
  sent_to_client: 'Envoyée au client',
  selected_by_client: 'Retenue par client',
  rejected_by_client: 'Rejetée par client',
  standby: 'En attente',
  medical_check_pending: 'Visite médicale',
  medical_approved: 'Apte',
  medical_rejected: 'Inapte',
  contract_pending: 'Contrat en attente',
  contract_signed: 'Contrat signé',
  hired: 'Embauché',
  rejected: 'Rejetée',
  withdrawn: 'Retirée',
}

const STATUS_COLORS: Record<string, string> = {
  submitted: 'bg-blue-100 text-blue-800',
  received: 'bg-blue-100 text-blue-800',
  under_review: 'bg-yellow-100 text-yellow-800',
  shortlisted: 'bg-purple-100 text-purple-800',
  rejected_initial: 'bg-red-100 text-red-800',
  interview_scheduled: 'bg-indigo-100 text-indigo-800',
  interview_completed: 'bg-indigo-100 text-indigo-800',
  selected_for_client: 'bg-green-100 text-green-800',
  rejected_after_interview: 'bg-red-100 text-red-800',
  sent_to_client: 'bg-cyan-100 text-cyan-800',
  selected_by_client: 'bg-green-100 text-green-800',
  rejected_by_client: 'bg-red-100 text-red-800',
  hired: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
}

export default function ApplicationsManagementPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const { data: mission } = useGetMissionQuery(id!)
  const { data: applications = [], isLoading, refetch } = useGetMissionApplicationsQuery(
    { mission_id: id! },
    { skip: !id }
  )

  const [updateApplication] = useUpdateApplicationMutation()
  const [shortlistApplication] = useShortlistApplicationMutation()

  const [selectedFilter, setSelectedFilter] = useState<string>('all')
  const [selectedApp, setSelectedApp] = useState<Application | null>(null)
  const [showDetailModal, setShowDetailModal] = useState(false)
  const [showRejectModal, setShowRejectModal] = useState(false)
  const [rejectReason, setRejectReason] = useState('')
  const [showInterviewModal, setShowInterviewModal] = useState(false)
  const [interviewDate, setInterviewDate] = useState('')
  const [interviewNotes, setInterviewNotes] = useState('')

  // Filter applications
  const filteredApplications = applications.filter(app => {
    if (selectedFilter === 'all') return true
    if (selectedFilter === 'rejected') {
      return app.status.includes('rejected') || app.status === 'rejected'
    }
    return app.status === selectedFilter
  })

  // Count by status
  const statusCounts = STATUS_FILTERS.map(filter => ({
    ...filter,
    count: filter.value === 'all' 
      ? applications.length
      : filter.value === 'rejected'
      ? applications.filter(a => a.status.includes('rejected') || a.status === 'rejected').length
      : applications.filter(a => a.status === filter.value).length
  }))

  const handleShortlist = async (appId: string) => {
    try {
      await shortlistApplication(appId).unwrap()
      toast.success('Candidature présélectionnée')
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur')
    }
  }

  const handleReject = async () => {
    if (!selectedApp || !rejectReason.trim()) {
      toast.error('Veuillez indiquer la raison du rejet')
      return
    }

    try {
      await updateApplication({
        id: selectedApp.id,
        data: {
          status: 'rejected_initial',
          internal_notes: rejectReason,
        }
      }).unwrap()
      toast.success('Candidature rejetée')
      setShowRejectModal(false)
      setRejectReason('')
      setSelectedApp(null)
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur')
    }
  }

  const handleScheduleInterview = async () => {
    if (!selectedApp || !interviewDate) {
      toast.error('Veuillez sélectionner une date')
      return
    }

    try {
      await updateApplication({
        id: selectedApp.id,
        data: {
          status: 'interview_scheduled',
          interview_scheduled_at: new Date(interviewDate).toISOString(),
          interview_notes: interviewNotes,
        }
      }).unwrap()
      toast.success('Entretien programmé')
      setShowInterviewModal(false)
      setInterviewDate('')
      setInterviewNotes('')
      setSelectedApp(null)
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur')
    }
  }

  const handleSendToClient = async (appId: string) => {
    try {
      await updateApplication({
        id: appId,
        data: { status: 'sent_to_client' }
      }).unwrap()
      toast.success('Profil envoyé au client')
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur')
    }
  }

  const openDetailModal = (app: Application) => {
    setSelectedApp(app)
    setShowDetailModal(true)
  }

  const openRejectModal = (app: Application) => {
    setSelectedApp(app)
    setShowRejectModal(true)
  }

  const openInterviewModal = (app: Application) => {
    setSelectedApp(app)
    setShowInterviewModal(true)
  }

  if (isLoading) {
    return (
      <Layout>
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate(`/missions/${id}`)}
              className="flex items-center text-gray-600 hover:text-gray-900"
            >
              <ArrowLeftIcon className="h-5 w-5 mr-2" />
              Retour
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Gestion des Candidatures</h1>
              {mission && (
                <p className="text-gray-600 text-sm mt-1">{mission.title}</p>
              )}
            </div>
          </div>
        </div>

        {/* Status Filter Tabs */}
        <div className="bg-white rounded-lg shadow overflow-x-auto">
          <div className="flex border-b">
            {statusCounts.map((filter) => (
              <button
                key={filter.value}
                onClick={() => setSelectedFilter(filter.value)}
                className={`flex-1 min-w-[120px] px-4 py-3 text-sm font-medium transition ${
                  selectedFilter === filter.value
                    ? 'border-b-2 border-jlc-purple-600 text-jlc-purple-600 bg-jlc-purple-50'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center justify-center gap-2">
                  <span>{filter.label}</span>
                  <span className={`px-2 py-0.5 rounded-full text-xs ${
                    selectedFilter === filter.value
                      ? 'bg-jlc-purple-600 text-white'
                      : 'bg-gray-200 text-gray-700'
                  }`}>
                    {filter.count}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Applications List */}
        <div className="space-y-4">
          {filteredApplications.length === 0 ? (
            <div className="bg-white p-12 rounded-lg shadow text-center">
              <UserIcon className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-4 text-gray-600">Aucune candidature dans cette catégorie</p>
            </div>
          ) : (
            filteredApplications.map((app) => (
              <div key={app.id} className="bg-white p-6 rounded-lg shadow hover:shadow-md transition">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="p-3 bg-gray-100 rounded-full">
                        <UserIcon className="h-6 w-6 text-gray-600" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">
                          Candidat #{app.user_id.slice(0, 8)}
                        </h3>
                        <p className="text-sm text-gray-600">
                          Postulé le {new Date(app.created_at).toLocaleDateString('fr-FR')}
                        </p>
                      </div>
                      <span className={`px-3 py-1 text-xs font-medium rounded-full ${
                        STATUS_COLORS[app.status] || 'bg-gray-100 text-gray-800'
                      }`}>
                        {STATUS_LABELS[app.status]}
                      </span>
                    </div>

                    {/* Cover Letter Preview */}
                    {app.cover_letter && (
                      <div className="mb-3 p-3 bg-gray-50 rounded">
                        <p className="text-sm text-gray-700 line-clamp-2">
                          {app.cover_letter}
                        </p>
                      </div>
                    )}

                    {/* Matching Skills */}
                    {app.matching_skills.length > 0 && (
                      <div className="flex flex-wrap gap-2 mb-3">
                        {app.matching_skills.slice(0, 5).map((skill, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-1 text-xs bg-jlc-purple-100 text-jlc-purple-700 rounded-full"
                          >
                            {skill}
                          </span>
                        ))}
                        {app.matching_skills.length > 5 && (
                          <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full">
                            +{app.matching_skills.length - 5}
                          </span>
                        )}
                      </div>
                    )}

                    {/* Score */}
                    {app.score !== null && app.score !== undefined && (
                      <div className="flex items-center gap-2">
                        <StarIcon className="h-5 w-5 text-yellow-500" />
                        <span className="text-sm font-medium text-gray-900">
                          Score: {app.score}/100
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex flex-col gap-2 ml-4">
                    <button
                      onClick={() => openDetailModal(app)}
                      className="flex items-center px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
                    >
                      <EyeIcon className="h-4 w-4 mr-2" />
                      Détails
                    </button>

                    {app.status === 'submitted' && (
                      <>
                        <button
                          onClick={() => handleShortlist(app.id)}
                          className="flex items-center px-4 py-2 text-sm bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition"
                        >
                          <StarIcon className="h-4 w-4 mr-2" />
                          Présélectionner
                        </button>
                        <button
                          onClick={() => openRejectModal(app)}
                          className="flex items-center px-4 py-2 text-sm bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition"
                        >
                          <XCircleIcon className="h-4 w-4 mr-2" />
                          Rejeter
                        </button>
                      </>
                    )}

                    {app.status === 'shortlisted' && (
                      <>
                        <button
                          onClick={() => openInterviewModal(app)}
                          className="flex items-center px-4 py-2 text-sm bg-indigo-100 text-indigo-700 rounded-lg hover:bg-indigo-200 transition"
                        >
                          <ClockIcon className="h-4 w-4 mr-2" />
                          Planifier entretien
                        </button>
                        <button
                          onClick={() => openRejectModal(app)}
                          className="flex items-center px-4 py-2 text-sm bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition"
                        >
                          <XCircleIcon className="h-4 w-4 mr-2" />
                          Rejeter
                        </button>
                      </>
                    )}

                    {app.status === 'interview_completed' && (
                      <button
                        onClick={() => handleSendToClient(app.id)}
                        className="flex items-center px-4 py-2 text-sm bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition"
                      >
                        <CheckCircleIcon className="h-4 w-4 mr-2" />
                        Envoyer au client
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Detail Modal */}
      <Modal isOpen={showDetailModal} onClose={() => setShowDetailModal(false)}>
        {selectedApp && (
          <div className="p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">
              Détails de la candidature
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700">Candidat</label>
                <p className="text-gray-900">#{selectedApp.user_id}</p>
              </div>

              {selectedApp.cover_letter && (
                <div>
                  <label className="text-sm font-medium text-gray-700">Lettre de motivation</label>
                  <p className="text-gray-900 whitespace-pre-wrap mt-1">{selectedApp.cover_letter}</p>
                </div>
              )}

              {selectedApp.matching_skills.length > 0 && (
                <div>
                  <label className="text-sm font-medium text-gray-700">Compétences</label>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {selectedApp.matching_skills.map((skill, idx) => (
                      <span key={idx} className="px-2 py-1 text-xs bg-jlc-purple-100 text-jlc-purple-700 rounded-full">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {selectedApp.additional_info && (
                <div>
                  <label className="text-sm font-medium text-gray-700">Informations complémentaires</label>
                  <p className="text-gray-900 mt-1">{selectedApp.additional_info}</p>
                </div>
              )}

              <div>
                <label className="text-sm font-medium text-gray-700">Date de candidature</label>
                <p className="text-gray-900">{new Date(selectedApp.created_at).toLocaleString('fr-FR')}</p>
              </div>
            </div>

            <div className="mt-6">
              <button
                onClick={() => setShowDetailModal(false)}
                className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
              >
                Fermer
              </button>
            </div>
          </div>
        )}
      </Modal>

      {/* Reject Modal */}
      <Modal isOpen={showRejectModal} onClose={() => setShowRejectModal(false)}>
        <div className="p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">
            Rejeter la candidature
          </h3>
          
          <p className="text-gray-600 mb-4">
            Veuillez indiquer la raison du rejet (optionnel mais recommandé)
          </p>

          <textarea
            value={rejectReason}
            onChange={(e) => setRejectReason(e.target.value)}
            rows={4}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
            placeholder="Raison du rejet..."
          />

          <div className="flex gap-3 mt-6">
            <button
              onClick={() => setShowRejectModal(false)}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Annuler
            </button>
            <button
              onClick={handleReject}
              className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              Rejeter
            </button>
          </div>
        </div>
      </Modal>

      {/* Interview Modal */}
      <Modal isOpen={showInterviewModal} onClose={() => setShowInterviewModal(false)}>
        <div className="p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">
            Planifier un entretien
          </h3>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Date et heure *
              </label>
              <input
                type="datetime-local"
                value={interviewDate}
                onChange={(e) => setInterviewDate(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Notes (optionnel)
              </label>
              <textarea
                value={interviewNotes}
                onChange={(e) => setInterviewNotes(e.target.value)}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                placeholder="Instructions pour l'entretien..."
              />
            </div>
          </div>

          <div className="flex gap-3 mt-6">
            <button
              onClick={() => setShowInterviewModal(false)}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Annuler
            </button>
            <button
              onClick={handleScheduleInterview}
              className="flex-1 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700"
            >
              Planifier
            </button>
          </div>
        </div>
      </Modal>
    </Layout>
  )
}
