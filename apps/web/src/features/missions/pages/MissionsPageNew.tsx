/**
 * Missions Page - Refactorisée avec EntityListTemplate
 * Configuration complète, zéro duplication
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import EntityListTemplate, { type EntityListConfig } from '@/templates/EntityListTemplate'
import { usePermissions } from '@/hooks/usePermission'
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
  EyeIcon,
  CheckCircleIcon,
  XCircleIcon,
  MapPinIcon,
  CurrencyEuroIcon,
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

export default function MissionsPageNew() {
  const navigate = useNavigate()
  const [selectedStatus, setSelectedStatus] = useState<MissionStatus | 'all'>('all')
  const [searchQuery, setSearchQuery] = useState('')

  const { permissions } = usePermissions([
    'missions.create.all',
    'missions.create.own',
    'missions.read.all',
    'missions.read.own',
    'missions.edit.all',
    'missions.edit.own',
    'missions.delete.all',
    'missions.delete.own',
    'missions.publish.all',
    'missions.manage.all',
  ])

  const { data: missions = [], isLoading, refetch } = useGetMissionsQuery({
    ...(selectedStatus !== 'all' && { status: selectedStatus }),
  })

  const { getLabel: getContractTypeLabel } = useContractTypes()
  const [publishMission] = usePublishMissionMutation()
  const [deleteMission] = useDeleteMissionMutation()

  const handleCreateMission = () => {
    navigate('/missions/create')
  }

  const handleViewMission = (mission: Mission) => {
    navigate(`/missions/${mission.id}`)
  }

  const handlePublish = async (mission: Mission) => {
    if (!(permissions['missions.publish.all'] || permissions['missions.manage.all'])) return
    try {
      await publishMission(mission.id).unwrap()
      toast.success('Mission publiée avec succès')
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la publication')
    }
  }

  const handleCancel = async (mission: Mission) => {
    if (!(permissions['missions.delete.all'] || permissions['missions.delete.own'] || permissions['missions.manage.all'])) return
    if (!window.confirm('Êtes-vous sûr de vouloir annuler cette mission ?')) return
    
    try {
      await deleteMission(mission.id).unwrap()
      toast.success('Mission annulée')
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de l\'annulation')
    }
  }

  // Filtrer selon recherche
  const filteredData = missions.filter(mission =>
    mission.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    mission.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    mission.job_type.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const config: EntityListConfig = {
    entityName: 'Mission',
    entityNamePlural: 'Missions',
    title: 'Gestion des Missions',
    subtitle: 'Créez, gérez et suivez vos missions d\'intérim',
    icon: BriefcaseIcon,

    columns: [
      {
        key: 'title',
        label: 'Mission',
        sortable: true,
        render: (title: string, mission: Mission) => (
          <div>
            <div className="font-medium text-gray-900">{title}</div>
            <div className="text-sm text-gray-500 line-clamp-1">{mission.description}</div>
          </div>
        ),
      },
      {
        key: 'job_type',
        label: 'Type de poste',
        render: (jobType: string, mission: Mission) => (
          <div className="space-y-1">
            <div className="flex items-center gap-1 text-sm text-gray-900">
              <BriefcaseIcon className="h-4 w-4 text-gray-400" />
              {jobType}
            </div>
            <div className="text-xs text-gray-500">
              {getContractTypeLabel(mission.contract_type)}
            </div>
          </div>
        ),
      },
      {
        key: 'location',
        label: 'Localisation',
        render: (location: string) => (
          <div className="flex items-center gap-1 text-sm text-gray-900">
            <MapPinIcon className="h-4 w-4 text-gray-400" />
            {location}
          </div>
        ),
      },
      {
        key: 'salary_range',
        label: 'Salaire',
        render: (salaryRange: string) => (
          salaryRange ? (
            <div className="flex items-center gap-1 text-sm text-gray-900">
              <CurrencyEuroIcon className="h-4 w-4 text-gray-400" />
              {salaryRange}
            </div>
          ) : (
            <span className="text-xs text-gray-500">-</span>
          )
        ),
      },
      {
        key: 'applications_count',
        label: 'Candidatures',
        render: (count: number, mission: Mission) => (
          <div className="space-y-1 text-xs">
            <div className="flex items-center gap-1 text-blue-600">
              <UsersIcon className="h-4 w-4" />
              {count} candidatures
            </div>
            <div className="text-purple-600">{mission.shortlisted_count} présélectionnés</div>
            <div className="text-green-600">{mission.hired_count} embauchés</div>
          </div>
        ),
      },
      {
        key: 'status',
        label: 'Statut',
        render: (status: MissionStatus) => (
          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[status]}`}>
            {STATUS_LABELS[status]}
          </span>
        ),
      },
    ],

    filters: [
      {
        key: 'status',
        label: 'Filtrer par statut',
        type: 'select',
        options: [
          { value: 'all', label: 'Tous les statuts' },
          { value: 'draft', label: 'Brouillons' },
          { value: 'published', label: 'Publiées' },
          { value: 'in_review', label: 'En analyse' },
          { value: 'completed', label: 'Terminées' },
        ],
      },
    ],

    actions: {
      create: {
        label: 'Nouvelle Mission',
        onClick: handleCreateMission,
        permission: ['missions.create.all', 'missions.create.own'],
      },
      row: [
        {
          key: 'view',
          label: 'Voir les détails',
          icon: EyeIcon,
          onClick: handleViewMission,
          variant: 'secondary',
          permission: ['missions.read.all', 'missions.read.own'],
        },
        {
          key: 'publish',
          label: 'Publier',
          icon: CheckCircleIcon,
          onClick: handlePublish,
          variant: 'primary',
          permission: ['missions.publish.all', 'missions.manage.all'],
          show: (mission: Mission) => mission.status === 'draft',
        },
        {
          key: 'cancel',
          label: 'Annuler',
          icon: XCircleIcon,
          onClick: handleCancel,
          variant: 'danger',
          permission: ['missions.delete.all', 'missions.delete.own', 'missions.manage.all'],
          show: (mission: Mission) => !['completed', 'cancelled'].includes(mission.status),
        },
      ],
    },

    data: filteredData,
    isLoading,

    onSearch: setSearchQuery,
    searchPlaceholder: 'Rechercher une mission...',

    emptyState: {
      message: 'Aucune mission trouvée',
      action: {
        label: 'Créer votre première mission',
        onClick: handleCreateMission,
      },
    },
  }

  return <EntityListTemplate config={config} permissions={permissions} />
}
