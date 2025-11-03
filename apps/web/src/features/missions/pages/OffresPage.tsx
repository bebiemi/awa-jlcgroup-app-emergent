import { useState } from 'react'
import { Link } from 'react-router-dom'
import Layout from '@/components/Layout'
import {
  useGetMissionsQuery,
  useApplyToMissionMutation,
  useGetMyApplicationsQuery,
  type Mission,
} from '../api/missionApi'
import {
  BriefcaseIcon,
  MapPinIcon,
  CalendarIcon,
  ClockIcon,
  CurrencyDollarIcon,
  AcademicCapIcon,
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

export default function OffresPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedJobType, setSelectedJobType] = useState<string>('all')

  const { data: missions = [], isLoading } = useGetMissionsQuery({
    published_only: true,
  })

  const { data: myApplications = [] } = useGetMyApplicationsQuery()
  
  const [applyToMission] = useApplyToMissionMutation()

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
                <p className="text-sm text-gray-600">Types de poste</p>
                <p className="text-2xl font-bold text-gray-900">{jobTypes.length}</p>
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
                placeholder="Rechercher par titre, description, localisation..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              />
            </div>
            <select
              value={selectedJobType}
              onChange={(e) => setSelectedJobType(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
            >
              <option value="all">Tous les types de poste</option>
              {jobTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Missions List */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredMissions.length === 0 ? (
            <div className="col-span-2 bg-white p-12 rounded-lg shadow text-center">
              <BriefcaseIcon className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-4 text-gray-600">Aucune mission disponible pour le moment</p>
              <p className="mt-2 text-sm text-gray-500">Revenez plus tard ou modifiez vos filtres</p>
            </div>
          ) : (
            filteredMissions.map((mission) => (
              <div key={mission.id} className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      {mission.title}
                    </h3>
                    <div className="flex items-center text-sm text-gray-600 mb-2">
                      <BriefcaseIcon className="h-4 w-4 mr-1" />
                      {mission.job_type}
                    </div>
                  </div>
                  {hasApplied(mission.id) && (
                    <span className="px-3 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                      ✓ Candidature envoyée
                    </span>
                  )}
                </div>

                <p className="text-gray-600 mb-4 line-clamp-3">
                  {mission.description}
                </p>

                <div className="space-y-2 mb-4 text-sm text-gray-600">
                  <div className="flex items-center">
                    <MapPinIcon className="h-4 w-4 mr-2 text-gray-400" />
                    {mission.location}
                  </div>
                  
                  <div className="flex items-center">
                    <CalendarIcon className="h-4 w-4 mr-2 text-gray-400" />
                    {mission.contract_type} {mission.duration && `• ${mission.duration}`}
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
                    <Link
                      to={`/offres/${mission.id}/postuler`}
                      className="flex-1 text-center px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 transition"
                    >
                      Postuler
                    </Link>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </Layout>
  )
}
