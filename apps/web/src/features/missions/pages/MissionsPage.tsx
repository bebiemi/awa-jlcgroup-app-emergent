import { useState } from 'react'
import { Link } from 'react-router-dom'
import Layout from '@/components/Layout'
import StatusBadge from '@/components/StatusBadge'
import { useContractTypes } from '@/hooks/useReferences'
import {
  useGetMissionsQuery,
  usePublishMissionMutation,
  useDeleteMissionMutation,
  type Mission,
  type MissionStatus,
} from '../api/missionApi'
import {
  BriefcaseIcon,
  PlusIcon,
  EyeIcon,
  CheckCircleIcon,
  ClockIcon,
  XCircleIcon,
  UsersIcon,
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

const STATUS_LABELS: Record<MissionStatus, string> = {
  draft: 'Brouillon',
  pending_validation: 'En attente validation',
  published: 'Publiée',
  accepting_applications: 'Accepte candidatures',
  applications_closed: 'Candidatures fermées',
  in_review: 'En analyse',
  interviews_scheduled: 'Entretiens programmés',
  interviews_completed: 'Entretiens terminés',
  profiles_sent_to_client: 'Profils envoyés',
  client_selection_pending: 'Sélection client en attente',
  client_selection_completed: 'Client a sélectionné',
  medical_check_pending: 'Visite médicale en attente',
  medical_check_completed: 'Visite médicale faite',
  contract_pending: 'Contrat en attente',
  contract_signed: 'Contrat signé',
  completed: 'Terminée',
  cancelled: 'Annulée',
  on_hold: 'En pause',
}

const STATUS_COLORS: Record<MissionStatus, string> = {
  draft: 'bg-gray-100 text-gray-800',
  pending_validation: 'bg-yellow-100 text-yellow-800',
  published: 'bg-green-100 text-green-800',
  accepting_applications: 'bg-blue-100 text-blue-800',
  applications_closed: 'bg-orange-100 text-orange-800',
  in_review: 'bg-purple-100 text-purple-800',
  interviews_scheduled: 'bg-indigo-100 text-indigo-800',
  interviews_completed: 'bg-indigo-100 text-indigo-800',
  profiles_sent_to_client: 'bg-cyan-100 text-cyan-800',
  client_selection_pending: 'bg-yellow-100 text-yellow-800',
  client_selection_completed: 'bg-green-100 text-green-800',
  medical_check_pending: 'bg-orange-100 text-orange-800',
  medical_check_completed: 'bg-green-100 text-green-800',
  contract_pending: 'bg-yellow-100 text-yellow-800',
  contract_signed: 'bg-green-100 text-green-800',
  completed: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
  on_hold: 'bg-gray-100 text-gray-800',
}

export default function MissionsPage() {
  const [selectedStatus, setSelectedStatus] = useState<MissionStatus | 'all'>('all')
  const [searchQuery, setSearchQuery] = useState('')

  const { data: missions = [], isLoading, refetch } = useGetMissionsQuery({
    ...(selectedStatus !== 'all' && { status: selectedStatus }),
  })

  const { getLabel: getContractTypeLabel } = useContractTypes()
  const [publishMission] = usePublishMissionMutation()
  const [deleteMission] = useDeleteMissionMutation()

  const handlePublish = async (missionId: string) => {
    try {
      await publishMission(missionId).unwrap()
      toast.success('Mission publiée avec succès')
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la publication')
    }
  }

  const handleDelete = async (missionId: string) => {
    if (!confirm('Êtes-vous sûr de vouloir annuler cette mission ?')) return
    
    try {
      await deleteMission(missionId).unwrap()
      toast.success('Mission annulée')
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de l\'annulation')
    }
  }

  const filteredMissions = missions.filter(mission =>
    mission.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    mission.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    mission.job_type.toLowerCase().includes(searchQuery.toLowerCase())
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
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Gestion des Missions</h1>
            <p className="text-gray-600 mt-2">
              Créez, gérez et suivez vos missions d'intérim
            </p>
          </div>
          <Link
            to="/missions/create"
            className="flex items-center px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 transition"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Nouvelle Mission
          </Link>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-blue-100">
                <BriefcaseIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Total Missions</p>
                <p className="text-2xl font-bold text-gray-900">{missions.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-green-100">
                <CheckCircleIcon className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Publiées</p>
                <p className="text-2xl font-bold text-gray-900">
                  {missions.filter(m => m.status === 'published').length}
                </p>
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
                <p className="text-2xl font-bold text-gray-900">
                  {missions.filter(m => !['completed', 'cancelled'].includes(m.status)).length}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-purple-100">
                <UsersIcon className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Candidatures</p>
                <p className="text-2xl font-bold text-gray-900">
                  {missions.reduce((sum, m) => sum + m.applications_count, 0)}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Filters & Search */}
        <div className="bg-white p-4 rounded-lg shadow space-y-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Rechercher une mission..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              />
            </div>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value as MissionStatus | 'all')}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
            >
              <option value="all">Tous les statuts</option>
              <option value="draft">Brouillons</option>
              <option value="published">Publiées</option>
              <option value="in_review">En analyse</option>
              <option value="completed">Terminées</option>
            </select>
          </div>
        </div>

        {/* Missions List */}
        <div className="space-y-4">
          {filteredMissions.length === 0 ? (
            <div className="bg-white p-12 rounded-lg shadow text-center">
              <BriefcaseIcon className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-4 text-gray-600">Aucune mission trouvée</p>
              <Link
                to="/missions/create"
                className="mt-4 inline-flex items-center text-jlc-purple-600 hover:text-jlc-purple-700"
              >
                <PlusIcon className="h-5 w-5 mr-1" />
                Créer votre première mission
              </Link>
            </div>
          ) : (
            filteredMissions.map((mission) => (
              <div key={mission.id} className="bg-white p-6 rounded-lg shadow hover:shadow-md transition">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <h3 className="text-xl font-semibold text-gray-900">
                        {mission.title}
                      </h3>
                      <StatusBadge
                        category="mission_statuses"
                        status={mission.status}
                        showIcon
                      />
                    </div>
                    
                    <p className="text-gray-600 mt-2 line-clamp-2">
                      {mission.description}
                    </p>

                    <div className="flex flex-wrap gap-4 mt-4 text-sm text-gray-600">
                      <div className="flex items-center">
                        <BriefcaseIcon className="h-4 w-4 mr-1" />
                        {mission.job_type}
                      </div>
                      <div>📍 {mission.location}</div>
                      <div>💼 {mission.contract_type}</div>
                      {mission.salary_range && <div>💰 {mission.salary_range}</div>}
                    </div>

                    <div className="flex gap-6 mt-4 text-sm">
                      <div>
                        <span className="text-gray-600">Candidatures:</span>
                        <span className="ml-2 font-semibold text-blue-600">{mission.applications_count}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Présélectionnés:</span>
                        <span className="ml-2 font-semibold text-purple-600">{mission.shortlisted_count}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Embauchés:</span>
                        <span className="ml-2 font-semibold text-green-600">{mission.hired_count}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-col gap-2 ml-4">
                    <Link
                      to={`/missions/${mission.id}`}
                      className="flex items-center px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
                    >
                      <EyeIcon className="h-4 w-4 mr-2" />
                      Voir
                    </Link>
                    
                    {mission.status === 'draft' && (
                      <button
                        onClick={() => handlePublish(mission.id)}
                        className="flex items-center px-4 py-2 text-sm bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition"
                      >
                        <CheckCircleIcon className="h-4 w-4 mr-2" />
                        Publier
                      </button>
                    )}
                    
                    {!['completed', 'cancelled'].includes(mission.status) && (
                      <button
                        onClick={() => handleDelete(mission.id)}
                        className="flex items-center px-4 py-2 text-sm bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition"
                      >
                        <XCircleIcon className="h-4 w-4 mr-2" />
                        Annuler
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </Layout>
  )
}
