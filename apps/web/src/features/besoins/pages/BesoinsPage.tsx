/**
 * Page Besoins – Version améliorée, clean et 100% config-driven
 * Préfusée pour migration NeedListTemplate
 */

import { useState, useMemo } from "react"
import { useNavigate } from "react-router-dom"
import NeedListTemplate from "@/templates/NeedListTemplate"
import EntityListTemplate from "@/templates/EntityListTemplate"
import { usePermissions } from "@/hooks/usePermission"
import { BesoinsPageConfig } from "../config/besoins.config"
import type { Besoin } from "../api/besoinsApi"
import toast from "react-hot-toast"

export default function BesoinsPage() {
  const navigate = useNavigate()
  const { permissions: userPermissions } = usePermissions([
    'besoins.read.all',
    'besoins.create',
    'besoins.edit',
    'besoins.delete',
    'besoins.validate',
  ])

  // États locaux
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [page, setPage] = useState(1)

  // RTK Query
  const { data, isLoading } = BesoinsPageConfig.api.list({
    status: statusFilter || undefined,
    page,
    page_size: 20,
    search: searchQuery || undefined,
  })

  // Handlers
  const handleCreateBesoin = () => {
    navigate('/admin/besoins/new')
  }

  const handleViewBesoin = (besoin: Besoin) => {
    navigate(`/admin/besoins/${besoin.id}`)
  }

  const handleEditBesoin = (besoin: Besoin) => {
    navigate(`/admin/besoins/${besoin.id}/edit`)
  }

  const handleValidateBesoin = (besoin: Besoin) => {
    // TODO: Ouvrir modale de validation
    toast.success('Validation à implémenter')
  }

  const handleRejectBesoin = (besoin: Besoin) => {
    // TODO: Ouvrir modale de rejet
    toast.error('Rejet à implémenter')
  }

  const handleDeleteBesoin = (besoin: Besoin) => {
    if (window.confirm(`Voulez-vous vraiment supprimer le besoin "${besoin.titre}" ?`)) {
      // TODO: Implémenter la suppression
      toast.error('Suppression à implémenter')
    }
  }

  // Rendu des colonnes
  const renderColumns = BesoinsPageConfig.columns.map((col) => ({
    ...col,
    render:
      col.key === 'status'
        ? (status: string) => {
            const statusConfig: Record<string, { label: string; color: string }> = {
              brouillon: { label: 'Brouillon', color: 'bg-gray-100 text-gray-700' },
              soumis: { label: 'Soumis', color: 'bg-blue-100 text-blue-700' },
              validé: { label: 'Validé', color: 'bg-green-100 text-green-700' },
              rejeté: { label: 'Rejeté', color: 'bg-red-100 text-red-700' },
              annulé: { label: 'Annulé', color: 'bg-gray-100 text-gray-700' },
            }
            const config = statusConfig[status] || statusConfig.brouillon
            return (
              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
                {config.label}
              </span>
            )
          }
        : col.key === 'date_debut_souhaitee' || col.key === 'date_fin_souhaitee'
        ? (value: string) => (value ? new Date(value).toLocaleDateString('fr-FR') : '-')
        : undefined,
  }))

  // Configuration template
  const templateConfig: EntityListConfig = {
    entityName: 'Besoin',
    entityNamePlural: 'Besoins',
    title: BesoinsPageConfig.title,
    subtitle: BesoinsPageConfig.subtitle,
    icon: BriefcaseIcon,

    columns: renderColumns,

    data: data?.items || [],
    isLoading,

    pagination: data
      ? {
          currentPage: data.page,
          totalPages: data.total_pages,
          onPageChange: setPage,
        }
      : undefined,

    onSearch: setSearchQuery,
    searchPlaceholder: 'Rechercher par titre, entreprise...',

    filters: [
      {
        key: 'status',
        label: 'Filtrer par statut',
        type: 'select',
        options: [
          { value: '', label: 'Tous les statuts' },
          { value: 'brouillon', label: 'Brouillon' },
          { value: 'soumis', label: 'Soumis' },
          { value: 'validé', label: 'Validé' },
          { value: 'rejeté', label: 'Rejeté' },
          { value: 'annulé', label: 'Annulé' },
        ],
      },
    ],

    actions: {
      create: {
        label: 'Créer un besoin',
        onClick: handleCreateBesoin,
        permission: 'besoins.create',
      },
      row: [
        {
          key: 'view',
          label: 'Voir les détails',
          icon: EyeIcon,
          onClick: handleViewBesoin,
          variant: 'secondary' as const,
        },
        {
          key: 'edit',
          label: 'Modifier',
          icon: PencilIcon,
          onClick: handleEditBesoin,
          variant: 'primary' as const,
          permission: 'besoins.edit',
        },
        {
          key: 'validate',
          label: 'Valider',
          icon: CheckCircleIcon,
          onClick: handleValidateBesoin,
          variant: 'primary' as const,
          permission: 'besoins.validate',
          show: (besoin: Besoin) => besoin.status === 'soumis',
        },
        {
          key: 'reject',
          label: 'Rejeter',
          icon: XCircleIcon,
          onClick: handleRejectBesoin,
          variant: 'danger' as const,
          permission: 'besoins.validate',
          show: (besoin: Besoin) => besoin.status === 'soumis',
        },
        {
          key: 'delete',
          label: 'Supprimer',
          icon: TrashIcon,
          onClick: handleDeleteBesoin,
          variant: 'danger' as const,
          permission: 'besoins.delete',
        },
      ],
    },

    emptyState: {
      message: 'Aucun besoin trouvé',
      action: {
        label: 'Créer le premier besoin',
        onClick: handleCreateBesoin,
      },
    },
  }

  return <EntityListTemplate config={templateConfig} permissions={userPermissions} />
}
