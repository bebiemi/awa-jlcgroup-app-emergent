import { useState } from 'react'
import { Link } from 'react-router-dom'
import Layout from '@/components/Layout'
import {
  useGetMissionsQuery,
  useApplyToMissionMutation,
  useGetMyApplicationsQuery,
  type Mission,
} from '../api/missionApi'
import { useGetActiveContractQuery } from '@/features/contracts/api/contractApi'
import MissionDetailModal from '../components/MissionDetailModal'
import {
  BriefcaseIcon,
  MapPinIcon,
  CalendarIcon,
  ClockIcon,
  CurrencyDollarIcon,
  AcademicCapIcon,
  ExclamationCircleIcon,
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'
import { useAppSelector } from '@/store/hooks'

export default function OffresPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedJobType, setSelectedJobType] = useState<string>('all')
  
  // État pour la modale de détail de mission
  const [selectedMission, setSelectedMission] = useState<Mission | null>(null)
  const [isMissionModalOpen, setIsMissionModalOpen] = useState(false)

  const currentUser = useAppSelector((state) => state.auth.user)
  const isInterimaire = currentUser?.roles?.includes('intérimaire') ?? false

  const { data: missions = [], isLoading } = useGetMissionsQuery({
    published_only: true,
  })

  const { data: myApplications = [] } = useGetMyApplicationsQuery()
  // Only fetch active contract for intérimaires
  const { data: contractData } = useGetActiveContractQuery(undefined, {
    skip: !isInterimaire,
  })
  
  const [applyToMission] = useApplyToMissionMutation()

  // Check if user can apply (no active mission or within J-5 of end)
  const canApply = contractData?.can_apply ?? true
  const activeContract = contractData?.active_contract

  // Extract unique job types
  const jobTypes = Array.from(new Set(missions.map(m => m.job_type)))

  const filteredMissions = missions.filter(mission => {
    const matchesSearch = 
      mission.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      mission.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      mission.job_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
      mission.location.toLowerCase().includes(searchQuery.toLowerCase())
    
    const matchesJobType = selectedJobType === 'all' || mission.job_type === selectedJobType

    return matchesSearch && matchesJobType
  })

  const hasApplied = (missionId: string) => {
    return myApplications.some(app => app.mission_id === missionId)
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
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Offres de Mission</h1>
          <p className="text-gray-600 mt-2">
            Découvrez les missions disponibles et postulez en quelques clics
          </p>
        </div>

        {/* Alert if user cannot apply */}
        {!canApply && activeContract && (
          <div className="bg-orange-50 border-l-4 border-orange-500 p-4 rounded">
            <div className="flex">
              <div className="flex-shrink-0">
                <ExclamationCircleIcon className="h-5 w-5 text-orange-400" />
              </div>
              <div className="ml-3">
                <p className="text-sm text-orange-700">
                  <span className="font-medium">Mission en cours : </span>
                  Vous êtes actuellement en mission <strong>{activeContract.mission_title}</strong>.
                  Les candidatures seront possibles 5 jours avant la fin de votre mission actuelle.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-blue-100">
                <BriefcaseIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Missions disponibles</p>
                <p className="text-2xl font-bold text-gray-900">{missions.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-green-100">
                <ClockIcon className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Mes candidatures</p>
                <p className="text-2xl font-bold text-gray-900">{myApplications.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-purple-100">
                <AcademicCapIcon className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Nouveautés</p>
                <p className="text-2xl font-bold text-gray-900">
                  {missions.filter(m => {
                    const created = new Date(m.created_at)
                    const weekAgo = new Date()
                    weekAgo.setDate(weekAgo.getDate() - 7)
                    return created > weekAgo
                  }).length}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Rechercher une mission..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              />
            </div>
            <div>
              <select
                value={selectedJobType}
                onChange={(e) => setSelectedJobType(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              >
                <option value="all">Tous les types de mission</option>
                {jobTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Results */}
        {filteredMissions.length === 0 ? (
          <div className="text-center py-12">
            <BriefcaseIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">Aucune mission disponible</p>
          </div>
        ) : (
          <div className="text-sm text-gray-600 mb-4">
            {filteredMissions.length} mission{filteredMissions.length > 1 ? 's' : ''} trouvée{filteredMissions.length > 1 ? 's' : ''}
          </div>
        )}

        {/* Mission Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredMissions.map((mission: Mission) => (
            <div key={mission.id} className="bg-white rounded-lg shadow hover:shadow-lg transition p-6">
              <div className="flex items-start justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  {mission.title}
                </h3>
                <span className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded-full">
                  {mission.status}
                </span>
              </div>

              <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                {mission.description}
              </p>

              <div className="space-y-2 text-sm text-gray-600 mb-4">
                <div className="flex items-center">
                  <MapPinIcon className="h-4 w-4 mr-2 text-gray-400" />
                  {mission.location}
                </div>
                <div className="flex items-center">
                  <CalendarIcon className="h-4 w-4 mr-2 text-gray-400" />
                  {new Date(mission.start_date).toLocaleDateString('fr-FR')} - {new Date(mission.end_date).toLocaleDateString('fr-FR')}
                </div>
                <div className="flex items-center">
                  <BriefcaseIcon className="h-4 w-4 mr-2 text-gray-400" />
                  {mission.job_type}
                </div>
                {mission.salary_range && (
                  <div className="flex items-center">
                    <CurrencyDollarIcon className="h-4 w-4 mr-2 text-gray-400" />
                    {mission.salary_range}
                  </div>
                )}
              </div>

              {/* Skills */}
              {mission.required_skills.length > 0 && (
                <div className="mb-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">Compétences requises:</p>
                  <div className="flex flex-wrap gap-2">
                    {mission.required_skills.slice(0, 5).map((skill, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 text-xs bg-jlc-purple-100 text-jlc-purple-700 rounded-full"
                      >
                        {skill}
                      </span>
                    ))}
                    {mission.required_skills.length > 5 && (
                      <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full">
                        +{mission.required_skills.length - 5}
                      </span>
                    )}
                  </div>
                </div>
              )}

              <div className="flex gap-3">
                <Link
                  to={`/offres/${mission.id}`}
                  className="flex-1 text-center px-4 py-2 border border-jlc-purple-600 text-jlc-purple-600 rounded-lg hover:bg-jlc-purple-50 transition"
                >
                  Voir les détails
                </Link>
                
                {!hasApplied(mission.id) && (
                  canApply ? (
                    <Link
                      to={`/offres/${mission.id}/postuler`}
                      className="flex-1 text-center px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 transition"
                    >
                      Postuler
                    </Link>
                  ) : (
                    <button
                      disabled
                      title="Vous avez une mission en cours"
                      className="flex-1 text-center px-4 py-2 bg-gray-300 text-gray-500 rounded-lg cursor-not-allowed"
                    >
                      Postuler
                    </button>
                  )
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </Layout>
  )
}
