import { useParams, Link, useNavigate } from 'react-router-dom'
import Layout from '@/components/Layout'
import StatusBadge from '@/components/StatusBadge'
import { useContractTypes } from '@/hooks/useReferences'
import {
  useGetMissionQuery,
  useGetMissionApplicationsQuery,
  useGetMissionStatsQuery,
  useUpdateMissionMutation,
  usePublishMissionMutation,
  type ApplicationStatus,
} from '../api/missionApi'
import {
  BriefcaseIcon,
  MapPinIcon,
  CalendarIcon,
  CurrencyDollarIcon,
  ClockIcon,
  AcademicCapIcon,
  ArrowLeftIcon,
  PencilIcon,
  CheckCircleIcon,
  UsersIcon,
} from '@heroicons/react/24/outline'
import { useAppSelector } from '@/store/hooks'
import toast from 'react-hot-toast'

const STATUS_LABELS: Record<string, string> = {
  draft: 'Brouillon',
  published: 'Publiée',
  accepting_applications: 'Accepte candidatures',
  in_review: 'En analyse',
  completed: 'Terminée',
  cancelled: 'Annulée',
}

const APPLICATION_STATUS_LABELS: Record<ApplicationStatus, string> = {
  submitted: 'Soumise',
  received: 'Reçue',
  under_review: 'En analyse',
  shortlisted: 'Présélectionnée',
  rejected_initial: 'Rejetée',
  interview_scheduled: 'Entretien programmé',
  interview_completed: 'Entretien passé',
  selected_for_client: 'Retenue pour client',
  rejected_after_interview: 'Rejetée après entretien',
  sent_to_client: 'Envoyée au client',
  selected_by_client: 'Retenue par client',
  rejected_by_client: 'Rejetée par client',
  standby: 'En attente',
  medical_check_pending: 'Visite médicale en attente',
  medical_approved: 'Apte',
  medical_rejected: 'Inapte',
  contract_pending: 'Contrat en attente',
  contract_signed: 'Contrat signé',
  hired: 'Embauché',
  rejected: 'Rejeté',
  withdrawn: 'Retirée',
}

export default function MissionDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAppSelector((state) => state.auth)

  const { data: mission, isLoading } = useGetMissionQuery(id!)
  const { data: applications = [] } = useGetMissionApplicationsQuery(
    { mission_id: id! },
    { skip: !id }
  )
  const { data: stats } = useGetMissionStatsQuery(id!, { skip: !id })
  
  const [publishMission] = usePublishMissionMutation()

  const isAdmin = user?.roles.includes('admin') || user?.roles.includes('super_admin')
  const isCommercial = user?.roles.includes('commercial')
  const canManage = isAdmin || isCommercial

  const handlePublish = async () => {
    if (!id) return
    try {
      await publishMission(id).unwrap()
      toast.success('Mission publiée avec succès')
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la publication')
    }
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

  if (!mission) {
    return (
      <Layout>
        <div className="text-center py-12">
          <p className="text-gray-600">Mission non trouvée</p>
          <Link to="/missions" className="text-jlc-purple-600 hover:text-jlc-purple-700 mt-4 inline-block">
            Retour aux missions
          </Link>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center text-gray-600 hover:text-gray-900"
          >
            <ArrowLeftIcon className="h-5 w-5 mr-2" />
            Retour
          </button>
          
          {canManage && (
            <div className="flex gap-2">
              {mission.status === 'draft' && (
                <button
                  onClick={handlePublish}
                  className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  <CheckCircleIcon className="h-5 w-5 mr-2" />
                  Publier
                </button>
              )}
              <Link
                to={`/missions/${id}/edit`}
                className="flex items-center px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700"
              >
                <PencilIcon className="h-5 w-5 mr-2" />
                Modifier
              </Link>
            </div>
          )}
        </div>

        {/* Mission Info Card */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="flex items-start justify-between mb-6">
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{mission.title}</h1>
              <span className={`px-3 py-1 text-sm font-medium rounded-full ${
                mission.status === 'published' ? 'bg-green-100 text-green-800' :
                mission.status === 'draft' ? 'bg-gray-100 text-gray-800' :
                'bg-blue-100 text-blue-800'
              }`}>
                {STATUS_LABELS[mission.status] || mission.status}
              </span>
            </div>
          </div>

          <div className="prose max-w-none mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Description</h3>
            <p className="text-gray-600 whitespace-pre-wrap">{mission.description}</p>
          </div>

          {/* Key Info Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <div className="flex items-start">
              <BriefcaseIcon className="h-6 w-6 text-gray-400 mr-3 mt-1" />
              <div>
                <p className="text-sm text-gray-600">Type de poste</p>
                <p className="font-semibold text-gray-900">{mission.job_type}</p>
              </div>
            </div>

            <div className="flex items-start">
              <MapPinIcon className="h-6 w-6 text-gray-400 mr-3 mt-1" />
              <div>
                <p className="text-sm text-gray-600">Localisation</p>
                <p className="font-semibold text-gray-900">{mission.location}</p>
              </div>
            </div>

            <div className="flex items-start">
              <CalendarIcon className="h-6 w-6 text-gray-400 mr-3 mt-1" />
              <div>
                <p className="text-sm text-gray-600">Type de contrat</p>
                <p className="font-semibold text-gray-900">{mission.contract_type}</p>
              </div>
            </div>

            {mission.duration && (
              <div className="flex items-start">
                <ClockIcon className="h-6 w-6 text-gray-400 mr-3 mt-1" />
                <div>
                  <p className="text-sm text-gray-600">Durée</p>
                  <p className="font-semibold text-gray-900">{mission.duration}</p>
                </div>
              </div>
            )}

            {mission.salary_range && (
              <div className="flex items-start">
                <CurrencyDollarIcon className="h-6 w-6 text-gray-400 mr-3 mt-1" />
                <div>
                  <p className="text-sm text-gray-600">Salaire</p>
                  <p className="font-semibold text-gray-900">{mission.salary_range}</p>
                </div>
              </div>
            )}

            <div className="flex items-start">
              <AcademicCapIcon className="h-6 w-6 text-gray-400 mr-3 mt-1" />
              <div>
                <p className="text-sm text-gray-600">Expérience requise</p>
                <p className="font-semibold text-gray-900">{mission.experience_required}</p>
              </div>
            </div>
          </div>

          {/* Skills Required */}
          {mission.required_skills.length > 0 && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Compétences requises</h3>
              <div className="flex flex-wrap gap-2">
                {mission.required_skills.map((skill, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-jlc-purple-100 text-jlc-purple-700 rounded-full text-sm"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Benefits */}
          {mission.benefits && mission.benefits.length > 0 && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Avantages</h3>
              <ul className="list-disc list-inside space-y-1">
                {mission.benefits.map((benefit, index) => (
                  <li key={index} className="text-gray-600">{benefit}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Working Hours */}
          {mission.working_hours && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Horaires de travail</h3>
              <p className="text-gray-600">{mission.working_hours}</p>
            </div>
          )}
        </div>

        {/* Statistics */}
        {stats && canManage && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Statistiques</h2>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">{stats.total_applications}</div>
                <div className="text-sm text-gray-600">Candidatures</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600">{stats.shortlisted}</div>
                <div className="text-sm text-gray-600">Présélectionnés</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-yellow-600">{stats.selected_by_client}</div>
                <div className="text-sm text-gray-600">Sélectionnés client</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">{stats.hired}</div>
                <div className="text-sm text-gray-600">Embauchés</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900">{stats.conversion_rate.toFixed(1)}%</div>
                <div className="text-sm text-gray-600">Taux conversion</div>
              </div>
            </div>
          </div>
        )}

        {/* Applications List */}
        {canManage && applications.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900 flex items-center">
                <UsersIcon className="h-6 w-6 mr-2" />
                Candidatures ({applications.length})
              </h2>
              <Link
                to={`/missions/${id}/candidatures`}
                className="text-jlc-purple-600 hover:text-jlc-purple-700 text-sm font-medium"
              >
                Voir toutes →
              </Link>
            </div>
            <div className="space-y-3">
              {applications.slice(0, 5).map((app) => (
                <div key={app.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">Candidat #{app.user_id.slice(0, 8)}</p>
                    <p className="text-sm text-gray-600">
                      {new Date(app.created_at).toLocaleDateString('fr-FR')}
                    </p>
                  </div>
                  <span className={`px-3 py-1 text-xs font-medium rounded-full ${
                    app.status === 'shortlisted' ? 'bg-purple-100 text-purple-800' :
                    app.status === 'hired' ? 'bg-green-100 text-green-800' :
                    app.status.includes('rejected') ? 'bg-red-100 text-red-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {APPLICATION_STATUS_LABELS[app.status]}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}
