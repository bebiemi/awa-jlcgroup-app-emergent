/**
 * Template réutilisable pour la liste des besoins
 * Utilisé par :
 * - Entreprise : "Mes besoins"
 * - Commercial : "Demandes clientes"
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
  PlusIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  ClockIcon,
  CheckCircleIcon,
  PaperAirplaneIcon,
} from '@heroicons/react/24/outline'
import { useGetBesoinsQuery } from '@/features/besoins/api/besoinsApi'
import { useGetWorkflowConfigQuery } from '@/features/besoins/api/configApi'
import { toast } from 'react-hot-toast'
import Breadcrumb from '@/components/Breadcrumb'

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

export type NeedListMode = 'entreprise' | 'commercial'

interface NeedListTemplateProps {
  mode: NeedListMode
  canCreate?: boolean
  canEdit?: boolean
  canDelete?: boolean
  canValidate?: boolean
}

export default function NeedListTemplate({
  mode,
  canCreate = true,
  canEdit = true,
  canDelete = false,
  canValidate = false,
}: NeedListTemplateProps) {
  const { t } = useTranslation()
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
    if (!status?.label) return statusKey
    
    // Si label est un objet de traduction {fr, en}, extraire la langue appropriée
    if (typeof status.label === 'object' && status.label !== null) {
      return status.label.fr || status.label.en || statusKey
    }
    
    return status.label
  }

  const handleCreateClick = () => {
    navigate('/entreprise/besoins/create')
  }

  const handleBesoinClick = (besoinId: string) => {
    navigate(`/entreprise/besoins/${besoinId}`)
  }

  // Labels contextuels selon le mode
  const labels = {
    entreprise: {
      title: t('besoins.entreprise.title', 'Mes besoins'),
      subtitle: t('besoins.entreprise.subtitle', 'Gérez vos demandes de recrutement'),
      createButton: t('besoins.entreprise.create', 'Créer un besoin'),
      emptyMessage: t('besoins.entreprise.empty', 'Aucun besoin pour le moment'),
      emptyAction: t('besoins.entreprise.emptyAction', 'Créer votre premier besoin'),
    },
    commercial: {
      title: t('besoins.commercial.title', 'Demandes clientes'),
      subtitle: t('besoins.commercial.subtitle', 'Gérez les demandes de recrutement des entreprises'),
      createButton: t('besoins.commercial.create', 'Créer une demande'),
      emptyMessage: t('besoins.commercial.empty', 'Aucune demande cliente pour le moment'),
      emptyAction: t('besoins.commercial.emptyAction', 'Créer une nouvelle demande'),
    },
  }

  const currentLabels = labels[mode]

  if (error) {
    toast.error('Erreur lors du chargement des besoins')
  }

  const besoins = besoinsData?.besoins || []
  const totalPages = Math.ceil((besoinsData?.total || 0) / 12)

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Breadcrumb */}
      <Breadcrumb className="mb-4" />

      <div className="max-w-7xl mx-auto">
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{currentLabels.title}</h1>
              <p className="text-gray-600 mt-1">{currentLabels.subtitle}</p>
            </div>
            {canCreate && (
              <button
                onClick={handleCreateClick}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-jlc-purple-600 to-indigo-600 text-white rounded-lg hover:from-jlc-purple-700 hover:to-indigo-700 shadow-md transition-all"
              >
                <PlusIcon className="h-5 w-5" />
                {currentLabels.createButton}
              </button>
            )}
          </div>

          {/* Filtres et recherche */}
          <div className="bg-white rounded-lg shadow-sm p-4">
            <div className="flex flex-col md:flex-row gap-4">
              {/* Recherche */}
              <div className="flex-1">
                <div className="relative">
                  <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Rechercher un besoin..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Filtre par statut */}
              <div className="md:w-64">
                <div className="relative">
                  <FunnelIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent appearance-none bg-white"
                  >
                    <option value="">Tous les statuts</option>
                    {workflowConfig?.statuses.map((status) => {
                      // Extraire le label correctement si c'est un objet de traduction
                      const label = typeof status.label === 'object' && status.label !== null
                        ? (status.label.fr || status.label.en || status.key)
                        : status.label
                      
                      return (
                        <option key={status.key} value={status.key}>
                          {label}
                        </option>
                      )
                    })}
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* Liste des besoins */}
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
            </div>
          ) : besoins.length === 0 ? (
            <div className="bg-white rounded-lg shadow-sm p-12 text-center">
              <div className="max-w-md mx-auto">
                <ClockIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {currentLabels.emptyMessage}
                </h3>
                {canCreate && (
                  <button
                    onClick={handleCreateClick}
                    className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 transition-colors"
                  >
                    <PlusIcon className="h-5 w-5" />
                    {currentLabels.emptyAction}
                  </button>
                )}
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {besoins.map((besoin: any) => {
                const StatusIcon = STATUS_ICONS[besoin.status] || ClockIcon
                const statusColor = STATUS_COLORS[besoin.status] || 'bg-gray-100 text-gray-700'

                return (
                  <div
                    key={besoin.id}
                    onClick={() => handleBesoinClick(besoin.id)}
                    className="bg-white rounded-lg shadow-sm hover:shadow-md transition-all cursor-pointer overflow-hidden border border-gray-200"
                  >
                    <div className="p-6">
                      {/* Statut */}
                      <div className="flex items-center justify-between mb-4">
                        <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium ${statusColor}`}>
                          <StatusIcon className="h-4 w-4" />
                          {getStatusLabel(besoin.status)}
                        </span>
                        {mode === 'commercial' && besoin.entreprise_name && (
                          <span className="text-xs text-gray-500 truncate max-w-[120px]">
                            {besoin.entreprise_name}
                          </span>
                        )}
                      </div>

                      {/* Titre */}
                      <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                        {besoin.titre}
                      </h3>

                      {/* Détails */}
                      <div className="space-y-2 text-sm text-gray-600">
                        {besoin.poste && (
                          <p className="truncate">📋 {besoin.poste}</p>
                        )}
                        {besoin.localisation && (
                          <p className="truncate">📍 {besoin.localisation}</p>
                        )}
                        {besoin.nombre_postes && (
                          <p>👥 {besoin.nombre_postes} poste(s)</p>
                        )}
                      </div>

                      {/* Date */}
                      <div className="mt-4 pt-4 border-t border-gray-100">
                        <p className="text-xs text-gray-500">
                          Créé le {new Date(besoin.created_at).toLocaleDateString('fr-FR')}
                        </p>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-6">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Précédent
              </button>
              <span className="px-4 py-2 text-gray-600">
                Page {page} / {totalPages}
              </span>
              <button
                onClick={() => setPage(Math.min(totalPages, page + 1))}
                disabled={page === totalPages}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Suivant
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
