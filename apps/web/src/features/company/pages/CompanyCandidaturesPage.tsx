import { useState } from 'react'
import Layout from '@/components/Layout'
import Card from '@/components/Card'
import {
  UserGroupIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
} from '@heroicons/react/24/outline'
import { Link } from 'react-router-dom'

export default function CompanyCandidaturesPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')

  // Mock data - À remplacer par de vraies données de l'API
  const candidatures = [
    {
      id: '1',
      candidat_name: 'Jean Dupont',
      mission_title: 'Développeur Full Stack',
      status: 'under_review',
      date_candidature: '2025-01-15',
      score: 85,
    },
    {
      id: '2',
      candidat_name: 'Marie Martin',
      mission_title: 'Chef de Projet IT',
      status: 'shortlisted',
      date_candidature: '2025-01-14',
      score: 92,
    },
    {
      id: '3',
      candidat_name: 'Pierre Bernard',
      mission_title: 'Développeur Full Stack',
      status: 'rejected',
      date_candidature: '2025-01-12',
      score: 45,
    },
  ]

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      submitted: { label: 'Soumise', color: 'bg-gray-100 text-gray-700' },
      under_review: { label: 'En revue', color: 'bg-blue-100 text-blue-700' },
      shortlisted: { label: 'Présélectionné', color: 'bg-green-100 text-green-700' },
      interview_scheduled: { label: 'Entretien prévu', color: 'bg-purple-100 text-purple-700' },
      selected: { label: 'Sélectionné', color: 'bg-green-200 text-green-800' },
      rejected: { label: 'Rejeté', color: 'bg-red-100 text-red-700' },
    }

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.submitted
    return (
      <span className={`px-3 py-1 rounded-full text-xs font-medium ${config.color}`}>
        {config.label}
      </span>
    )
  }

  const getStatusIcon = (status: string) => {
    if (status === 'selected' || status === 'shortlisted') {
      return <CheckCircleIcon className="h-5 w-5 text-green-500" />
    }
    if (status === 'rejected') {
      return <XCircleIcon className="h-5 w-5 text-red-500" />
    }
    return <ClockIcon className="h-5 w-5 text-blue-500" />
  }

  const filteredCandidatures = candidatures.filter((c) => {
    const matchSearch =
      searchTerm === '' ||
      c.candidat_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.mission_title.toLowerCase().includes(searchTerm.toLowerCase())
    const matchStatus = filterStatus === 'all' || c.status === filterStatus
    return matchSearch && matchStatus
  })

  const stats = {
    total: candidatures.length,
    enRevue: candidatures.filter((c) => c.status === 'under_review').length,
    preselectionnes: candidatures.filter((c) => c.status === 'shortlisted').length,
    rejetes: candidatures.filter((c) => c.status === 'rejected').length,
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Suivi des Candidatures</h1>
          <p className="mt-2 text-gray-600">
            Gérez et suivez toutes les candidatures reçues pour vos missions
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="bg-gradient-to-br from-blue-50 to-blue-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-blue-600">Total</p>
                <p className="text-2xl font-bold text-blue-900 mt-1">{stats.total}</p>
              </div>
              <UserGroupIcon className="h-8 w-8 text-blue-600" />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-yellow-50 to-yellow-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-yellow-600">En revue</p>
                <p className="text-2xl font-bold text-yellow-900 mt-1">{stats.enRevue}</p>
              </div>
              <ClockIcon className="h-8 w-8 text-yellow-600" />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-green-50 to-green-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-green-600">Présélectionnés</p>
                <p className="text-2xl font-bold text-green-900 mt-1">{stats.preselectionnes}</p>
              </div>
              <CheckCircleIcon className="h-8 w-8 text-green-600" />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-red-50 to-red-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-red-600">Rejetés</p>
                <p className="text-2xl font-bold text-red-900 mt-1">{stats.rejetes}</p>
              </div>
              <XCircleIcon className="h-8 w-8 text-red-600" />
            </div>
          </Card>
        </div>

        {/* Filters */}
        <Card>
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Rechercher par candidat ou mission..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              />
            </div>

            {/* Status Filter */}
            <div className="flex items-center gap-2">
              <FunnelIcon className="h-5 w-5 text-gray-400" />
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              >
                <option value="all">Tous les statuts</option>
                <option value="under_review">En revue</option>
                <option value="shortlisted">Présélectionnés</option>
                <option value="rejected">Rejetés</option>
              </select>
            </div>
          </div>
        </Card>

        {/* Candidatures List */}
        <Card>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Candidat
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Mission
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Score
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
                {filteredCandidatures.map((candidature) => (
                  <tr key={candidature.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {getStatusIcon(candidature.status)}
                        <span className="ml-3 text-sm font-medium text-gray-900">
                          {candidature.candidat_name}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-900">{candidature.mission_title}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <span className="text-sm font-medium text-gray-900">
                          {candidature.score}%
                        </span>
                        <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              candidature.score >= 70
                                ? 'bg-green-500'
                                : candidature.score >= 50
                                ? 'bg-yellow-500'
                                : 'bg-red-500'
                            }`}
                            style={{ width: `${candidature.score}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(candidature.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(candidature.date_candidature).toLocaleDateString('fr-FR')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <Link
                        to={`/missions/applications/${candidature.id}`}
                        className="text-jlc-purple-600 hover:text-jlc-purple-700 font-medium"
                      >
                        Voir détails →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {filteredCandidatures.length === 0 && (
              <div className="text-center py-12">
                <UserGroupIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">Aucune candidature</h3>
                <p className="mt-1 text-sm text-gray-500">
                  {searchTerm || filterStatus !== 'all'
                    ? 'Aucun résultat pour ces filtres'
                    : 'Vous n\'avez pas encore reçu de candidatures'}
                </p>
              </div>
            )}
          </div>
        </Card>
      </div>
    </Layout>
  )
}
