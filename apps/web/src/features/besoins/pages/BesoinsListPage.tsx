import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout from '@/components/Layout'
import {
  PlusIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  ClockIcon,
  CheckCircleIcon,
  PaperAirplaneIcon,
} from '@heroicons/react/24/outline'
import { useGetBesoinsQuery } from '../api/besoinApi'
import { useGetWorkflowConfigQuery } from '../api/configApi'
import { toast } from 'react-hot-toast'

const STATUS_ICONS: Record<string, any> = {
  brouillon: ClockIcon,
  soumis: PaperAirplaneIcon,
  analyse: MagnifyingGlassIcon,
  mission_creee: CheckCircleIcon,
  publication: CheckCircleIcon,
  pourvu: CheckCircleIcon,
}

const STATUS_COLORS: Record<string, string> = {
  brouillon: 'bg-gray-100 text-gray-700',
  soumis: 'bg-blue-100 text-blue-700',
  analyse: 'bg-yellow-100 text-yellow-700',
  mission_creee: 'bg-purple-100 text-purple-700',
  publication: 'bg-green-100 text-green-700',
  pourvu: 'bg-emerald-100 text-emerald-700',
}

export default function BesoinsListPage() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [page, setPage] = useState(1)

  const { data: besoinsData, isLoading, error } = useGetBesoinsQuery({
    status: statusFilter || undefined,
    search: search || undefined,
    page,
    page_size: 12,
  })

  const { data: workflowConfig } = useGetWorkflowConfigQuery('besoin')

  const getStatusLabel = (statusKey: string) => {
    const status = workflowConfig?.statuses.find((s) => s.key === statusKey)
    return status?.label?.fr || statusKey
  }

  const getStatusColor = (statusKey: string) => {
    const status = workflowConfig?.statuses.find((s) => s.key === statusKey)
    return status?.color || '#6B7280'
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return null
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Demandes clientes</h1>
            <p className="text-gray-600 mt-1">Gérez les demandes de recrutement des entreprises</p>
          </div>
          <button
            onClick={() => navigate('/entreprise/besoins/create')}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-jlc-purple-600 to-indigo-600 text-white rounded-lg hover:from-jlc-purple-700 hover:to-indigo-700 shadow-md transition-all"
          >
            <PlusIcon className="h-5 w-5" />
            Créer une demande
          </button>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Search */}
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Rechercher un besoin..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              />
            </div>

            {/* Status filter */}
            <div className="relative">
              <FunnelIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent appearance-none"
              >
                <option value="">Tous les statuts</option>
                {workflowConfig?.statuses.map((status) => (
                  <option key={status.key} value={status.key}>
                    {status.label.fr}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Besoins Grid */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="animate-pulse">
                <div className="bg-gray-200 rounded-2xl h-64" />
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
            Erreur lors du chargement des besoins
          </div>
        ) : besoinsData && besoinsData.items.length > 0 ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {besoinsData.items.map((besoin) => {
                const StatusIcon = STATUS_ICONS[besoin.status] || ClockIcon
                const statusColorClass = STATUS_COLORS[besoin.status] || 'bg-gray-100 text-gray-700'

                return (
                  <div
                    key={besoin.id}
                    onClick={() => navigate(`/entreprise/besoins/${besoin.id}`)}
                    className="bg-white rounded-2xl shadow-md border border-gray-100 hover:shadow-xl transition-all cursor-pointer overflow-hidden group"
                  >
                    {/* Header with status */}
                    <div className="bg-gradient-to-r from-jlc-purple-50 to-indigo-50 p-4 border-b border-gray-200">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900 group-hover:text-jlc-purple-600 transition-colors line-clamp-2">
                            {besoin.titre}
                          </h3>
                          <p className="text-sm text-gray-600 mt-1">{besoin.type_poste}</p>
                        </div>
                        <span
                          className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${statusColorClass}`}
                        >
                          <StatusIcon className="h-4 w-4" />
                          {getStatusLabel(besoin.status)}
                        </span>
                      </div>
                    </div>

                    {/* Body */}
                    <div className="p-4 space-y-3">
                      <p className="text-sm text-gray-600 line-clamp-3">{besoin.description}</p>

                      {/* Competences */}
                      {besoin.competences_attendues.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {besoin.competences_attendues.slice(0, 3).map((comp) => (
                            <span
                              key={comp}
                              className="px-2 py-1 bg-jlc-purple-100 text-jlc-purple-700 text-xs rounded-full"
                            >
                              {comp}
                            </span>
                          ))}
                          {besoin.competences_attendues.length > 3 && (
                            <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                              +{besoin.competences_attendues.length - 3}
                            </span>
                          )}
                        </div>
                      )}

                      {/* Footer */}
                      <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                        <div className="text-xs text-gray-500">
                          Créé le {formatDate(besoin.created_at)}
                        </div>
                        {besoin.comments_count > 0 && (
                          <div className="flex items-center gap-1 text-xs text-gray-500">
                            💬 {besoin.comments_count}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>

            {/* Pagination */}
            {besoinsData.total_pages > 1 && (
              <div className="flex justify-center gap-2 mt-6">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Précédent
                </button>
                <span className="px-4 py-2 text-gray-700">
                  Page {page} sur {besoinsData.total_pages}
                </span>
                <button
                  onClick={() => setPage((p) => Math.min(besoinsData.total_pages, p + 1))}
                  disabled={page === besoinsData.total_pages}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Suivant
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-12">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
              <ClockIcon className="h-8 w-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Aucun besoin trouvé</h3>
            <p className="text-gray-600 mb-6">Commencez par créer votre premier besoin de recrutement</p>
            <button
              onClick={() => navigate('/entreprise/besoins/create')}
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-jlc-purple-600 to-indigo-600 text-white rounded-lg hover:from-jlc-purple-700 hover:to-indigo-700 shadow-md transition-all"
            >
              <PlusIcon className="h-5 w-5" />
              Créer mon premier besoin
            </button>
          </div>
        )}
      </div>
    </Layout>
  )
}
