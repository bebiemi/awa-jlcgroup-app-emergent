/**
 * Page Liste Missions - Refactorisée avec EntityListTemplate
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import EntityListTemplate, { type EntityListConfig } from '@/templates/EntityListTemplate'
import { usePermissions } from '@/hooks/usePermission'
import { useGetMissionsQuery } from '../api/missionsApi'
import {
  BriefcaseIcon,
  PencilIcon,
  EyeIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

export default function MissionsListPageNew() {
  const navigate = useNavigate()
  const [page, setPage] = useState(1)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const { permissions } = usePermissions([
    'missions.create',
    'missions.read',
    'missions.edit',
    'missions.delete',
  ])

  const { data, isLoading } = useGetMissionsQuery({
    page,
    page_size: 15,
    search: searchQuery || undefined,
    status: statusFilter || undefined,
  })

  const handleCreateMission = () => {
    navigate('/missions/create')
  }

  const handleViewMission = (mission: any) => {
    navigate(`/missions/${mission.id}`)
  }

  const handleEditMission = (mission: any) => {
    navigate(`/missions/${mission.id}/edit`)
  }

  const handleViewCandidatures = (mission: any) => {
    navigate(`/missions/${mission.id}/candidatures`)
  }

  const config: EntityListConfig = {
    entityName: 'Mission',
    entityNamePlural: 'Missions',
    title: 'Gestion des Missions',
    subtitle: 'Créez, gérez et suivez vos missions d\'intérim',
    icon: BriefcaseIcon,

    columns: [
      {
        key: 'titre',
        label: 'Titre',
        sortable: true,
        render: (titre: string, mission: any) => (
          <div>
            <div className="font-medium text-gray-900">{titre}</div>
            {mission.entreprise_name && (
              <div className="text-sm text-gray-500">{mission.entreprise_name}</div>
            )}
          </div>
        ),
      },
      {
        key: 'localisation',
        label: 'Localisation',
        render: (localisation: string) => (
          <span className="text-gray-700">📍 {localisation}</span>
        ),
      },
      {
        key: 'date_debut',
        label: 'Début',
        render: (date: string) => date ? new Date(date).toLocaleDateString('fr-FR') : '-',
      },
      {
        key: 'status',
        label: 'Statut',
        render: (status: string) => {
          const statusConfig: Record<string, { label: string; color: string }> = {
            brouillon: { label: 'Brouillon', color: 'bg-gray-100 text-gray-700' },
            publiee: { label: 'Publiée', color: 'bg-green-100 text-green-700' },
            en_cours: { label: 'En cours', color: 'bg-blue-100 text-blue-700' },
            terminee: { label: 'Terminée', color: 'bg-gray-100 text-gray-700' },
          }
          const config = statusConfig[status] || statusConfig.brouillon
          return (
            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
              {config.label}
            </span>
          )
        },
      },
    ],

    filters: [
      {
        key: 'status',
        label: 'Filtrer par statut',
        type: 'select',
        options: [
          { value: '', label: 'Tous les statuts' },
          { value: 'brouillon', label: 'Brouillon' },
          { value: 'publiee', label: 'Publiée' },
          { value: 'en_cours', label: 'En cours' },
          { value: 'terminee', label: 'Terminée' },
        ],
      },
    ],

    actions: {
      create: {
        label: 'Créer une mission',
        onClick: handleCreateMission,
        permission: 'missions.create',
      },
      row: [
        {
          key: 'view',
          label: 'Voir les détails',
          icon: EyeIcon,
          onClick: handleViewMission,
          variant: 'secondary',
          permission: 'missions.read',
        },
        {
          key: 'edit',
          label: 'Modifier',
          icon: PencilIcon,
          onClick: handleEditMission,
          variant: 'primary',
          permission: 'missions.edit',
        },
        {
          key: 'candidatures',
          label: 'Candidatures',
          icon: UserGroupIcon,
          onClick: handleViewCandidatures,
          variant: 'secondary',
          permission: 'applications.manage',
        },
      ],
    },

    data: data?.missions || [],
    isLoading,

    pagination: data
      ? {
          currentPage: page,
          totalPages: Math.ceil(data.total / 15),
          onPageChange: setPage,
        }
      : undefined,

    onSearch: setSearchQuery,
    searchPlaceholder: 'Rechercher une mission...',

    emptyState: {
      message: 'Aucune mission pour le moment',
      action: {
        label: 'Créer la première mission',
        onClick: handleCreateMission,
      },
    },
  }

  return <EntityListTemplate config={config} permissions={permissions} />
}
