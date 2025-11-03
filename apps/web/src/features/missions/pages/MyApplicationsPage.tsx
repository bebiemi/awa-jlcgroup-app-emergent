import { Link } from 'react-router-dom'
import Layout from '@/components/Layout'
import { useGetMyApplicationsQuery, type ApplicationStatus } from '../api/missionApi'
import {
  BriefcaseIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  EyeIcon,
} from '@heroicons/react/24/outline'

const STATUS_LABELS: Record<ApplicationStatus, string> = {
  submitted: 'En attente',
  received: 'Reçue',
  under_review: 'En cours d\'analyse',
  shortlisted: '✨ Présélectionnée',
  rejected_initial: 'Non retenue',
  interview_scheduled: '📅 Entretien programmé',
  interview_completed: 'Entretien passé',
  selected_for_client: '🎯 Envoyée au client',
  rejected_after_interview: 'Non retenue',
  sent_to_client: 'Envoyée au client',
  selected_by_client: '🎉 Retenue par le client',
  rejected_by_client: 'Non retenue par le client',
  standby: 'Liste d\'attente',
  medical_check_pending: '🏥 Visite médicale à faire',
  medical_approved: '✅ Apte',
  medical_rejected: 'Inapte',
  contract_pending: '📝 Contrat en attente',
  contract_signed: '✅ Contrat signé',
  hired: '🎉 Embauché(e)',
  rejected: 'Non retenue',
  withdrawn: 'Retirée',
}

const STATUS_COLORS: Record<string, string> = {
  submitted: 'bg-blue-100 text-blue-800 border-blue-200',
  shortlisted: 'bg-purple-100 text-purple-800 border-purple-200',
  interview_scheduled: 'bg-indigo-100 text-indigo-800 border-indigo-200',
  selected_for_client: 'bg-cyan-100 text-cyan-800 border-cyan-200',
  selected_by_client: 'bg-green-100 text-green-800 border-green-200',
  medical_check_pending: 'bg-orange-100 text-orange-800 border-orange-200',
  medical_approved: 'bg-green-100 text-green-800 border-green-200',
  contract_pending: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  contract_signed: 'bg-green-100 text-green-800 border-green-200',
  hired: 'bg-green-100 text-green-800 border-green-200',
  rejected: 'bg-red-100 text-red-800 border-red-200',
}

const getStatusInfo = (status: ApplicationStatus) => {
  const messages: Record<string, { title: string; desc: string }> = {
    submitted: {
      title: 'En attente',
      desc: 'Votre candidature a été reçue et est en cours de traitement'
    },
    shortlisted: {
      title: 'Présélectionné !',
      desc: 'Félicitations ! Votre profil a été présélectionné'
    },
    interview_scheduled: {
      title: 'Entretien programmé',
      desc: 'Un entretien a été planifié. Vous serez contacté prochainement'
    },
    selected_for_client: {
      title: 'Envoyé au client',
      desc: 'Votre profil a été transmis au client pour validation finale'
    },
    selected_by_client: {
      title: 'Félicitations !',
      desc: 'Le client vous a sélectionné ! Prochaine étape: visite médicale'
    },
    medical_check_pending: {
      title: 'Visite médicale',
      desc: 'Veuillez effectuer votre visite médicale et uploader le certificat'
    },
    medical_approved: {
      title: 'Apte au poste',
      desc: 'Votre visite médicale est validée. En attente du contrat'
    },
    contract_pending: {
      title: 'Contrat en préparation',
      desc: 'Le contrat est en cours de préparation'
    },
    contract_signed: {
      title: 'Contrat signé',
      desc: 'Toutes les formalités sont terminées !'
    },
    hired: {
      title: 'Embauché !',
      desc: 'Félicitations ! Vous êtes officiellement embauché'
    },
    rejected: {
      title: 'Non retenue',
      desc: 'Votre candidature n\'a pas été retenue cette fois'
    },
  }

  return messages[status] || { title: 'En cours', desc: 'Statut en cours de mise à jour' }
}

export default function MyApplicationsPage() {
  const { data: applications = [], isLoading } = useGetMyApplicationsQuery()

  // Group by status
  const activeApplications = applications.filter(app => 
    !['rejected', 'withdrawn', 'hired'].includes(app.status)
  )
  const completedApplications = applications.filter(app =>
    app.status === 'hired'
  )
  const rejectedApplications = applications.filter(app =>
    ['rejected', 'withdrawn'].includes(app.status) ||
    app.status.includes('rejected')
  )

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
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Mes Candidatures</h1>
          <p className="text-gray-600 mt-2">
            Suivez l'évolution de vos candidatures en temps réel
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-blue-100">
                <BriefcaseIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Total</p>
                <p className="text-2xl font-bold text-gray-900">{applications.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-yellow-100">
                <ClockIcon className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">En cours</p>
                <p className="text-2xl font-bold text-gray-900">{activeApplications.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-green-100">
                <CheckCircleIcon className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Embauchés</p>
                <p className="text-2xl font-bold text-gray-900">{completedApplications.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-red-100">
                <XCircleIcon className="h-6 w-6 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Non retenues</p>
                <p className="text-2xl font-bold text-gray-900">{rejectedApplications.length}</p>
              </div>
            </div>
          </div>
        </div>

        {applications.length === 0 ? (
          <div className="bg-white p-12 rounded-lg shadow text-center">
            <BriefcaseIcon className="mx-auto h-12 w-12 text-gray-400" />
            <p className="mt-4 text-gray-600">Vous n'avez pas encore de candidatures</p>
            <Link
              to="/offres"
              className="mt-4 inline-block text-jlc-purple-600 hover:text-jlc-purple-700 font-medium"
            >
              Découvrir les offres disponibles →
            </Link>
          </div>
        ) : (
          <>
            {/* Active Applications */}
            {activeApplications.length > 0 && (
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-4">
                  Candidatures en cours ({activeApplications.length})
                </h2>
                <div className="space-y-4">
                  {activeApplications.map((app) => {
                    const statusInfo = getStatusInfo(app.status)
                    return (
                      <div key={app.id} className="bg-white p-6 rounded-lg shadow hover:shadow-md transition">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <h3 className="text-lg font-semibold text-gray-900">
                                Mission #{app.mission_id.slice(0, 8)}
                              </h3>
                              <span className={`px-3 py-1 text-xs font-medium rounded-full border ${
                                STATUS_COLORS[app.status] || 'bg-gray-100 text-gray-800 border-gray-200'
                              }`}>
                                {STATUS_LABELS[app.status]}
                              </span>
                            </div>

                            <div className="mb-3 p-4 bg-blue-50 border-l-4 border-blue-400 rounded">
                              <p className="font-medium text-blue-900">{statusInfo.title}</p>
                              <p className="text-sm text-blue-700 mt-1">{statusInfo.desc}</p>
                            </div>

                            {app.interview_scheduled_at && (
                              <div className="text-sm text-gray-600 mb-2">
                                📅 Entretien prévu le {new Date(app.interview_scheduled_at).toLocaleString('fr-FR')}
                              </div>
                            )}

                            {app.matching_skills.length > 0 && (
                              <div className="flex flex-wrap gap-2 mt-2">
                                {app.matching_skills.slice(0, 4).map((skill, idx) => (
                                  <span key={idx} className="px-2 py-1 text-xs bg-jlc-purple-100 text-jlc-purple-700 rounded-full">
                                    {skill}
                                  </span>
                                ))}
                              </div>
                            )}

                            <p className="text-sm text-gray-500 mt-3">
                              Candidature envoyée le {new Date(app.created_at).toLocaleDateString('fr-FR')}
                            </p>
                          </div>

                          <Link
                            to={`/offres/${app.mission_id}`}
                            className="ml-4 flex items-center px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
                          >
                            <EyeIcon className="h-4 w-4 mr-2" />
                            Voir l'offre
                          </Link>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            {/* Completed Applications */}
            {completedApplications.length > 0 && (
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-4">
                  Missions réussies ({completedApplications.length})
                </h2>
                <div className="space-y-4">
                  {completedApplications.map((app) => (
                    <div key={app.id} className="bg-gradient-to-r from-green-50 to-emerald-50 p-6 rounded-lg shadow border border-green-200">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <CheckCircleIcon className="h-6 w-6 text-green-600" />
                            <h3 className="text-lg font-semibold text-gray-900">
                              Mission #{app.mission_id.slice(0, 8)}
                            </h3>
                            <span className="px-3 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800 border border-green-200">
                              🎉 Embauché
                            </span>
                          </div>
                          <p className="text-sm text-gray-600">
                            Contrat signé le {app.contract_signed_at ? new Date(app.contract_signed_at).toLocaleDateString('fr-FR') : 'N/A'}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Rejected Applications */}
            {rejectedApplications.length > 0 && (
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-4">
                  Candidatures non retenues ({rejectedApplications.length})
                </h2>
                <div className="space-y-4">
                  {rejectedApplications.map((app) => (
                    <div key={app.id} className="bg-white p-6 rounded-lg shadow opacity-75">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="text-lg font-semibold text-gray-900">
                              Mission #{app.mission_id.slice(0, 8)}
                            </h3>
                            <span className="px-3 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800">
                              Non retenue
                            </span>
                          </div>
                          <p className="text-sm text-gray-600">
                            Ne vous découragez pas ! Continuez à postuler.
                          </p>
                        </div>
                        <Link
                          to="/offres"
                          className="ml-4 px-4 py-2 text-sm bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 transition"
                        >
                          Voir d'autres offres
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </Layout>
  )
}
