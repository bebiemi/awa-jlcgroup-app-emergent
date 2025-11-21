/**
 * Page de Gestion des Entreprises
 * Utilise EntityListTemplate avec entreprises.config.ts
 * Architecture Config-Driven
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  BuildingOfficeIcon,
  PencilIcon,
  EyeIcon,
  MapPinIcon,
  EnvelopeIcon,
  PhoneIcon,
  TrashIcon,
} from '@heroicons/react/24/outline'
import { EntreprisesPageConfig } from '../config/entreprises.config'
import EntityListTemplate from '@/templates/EntityListTemplate'
import { usePermissions } from '@/hooks/usePermission'
import type { EntityListConfig } from '@/templates/EntityListTemplate'
import type { Entreprise } from '../api/entreprisesApi'
import toast from 'react-hot-toast'

export default function EntreprisesPage() {
  const navigate = useNavigate()
  const { permissions: userPermissions } = usePermissions([
    'entreprises.read.all',
    'company.create',
    'company.edit',
    'company.delete',
  ])

  // États locaux pour les filtres et recherche
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)

  // RTK Query pour récupérer les entreprises
  const { data = [], isLoading, refetch } = EntreprisesPageConfig.api.list({ limit: 1000 })

  // Filtrer selon recherche et statut
  const filteredData = data.filter((e: Entreprise) => {
    const matchesSearch =
      e.nom?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      e.siret?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      e.email?.toLowerCase().includes(searchQuery.toLowerCase())

    const matchesStatus = !statusFilter || e.status === statusFilter

    return matchesSearch && matchesStatus
  })

  // Handlers
  const handleCreateModalOpen = () => {
    setIsCreateModalOpen(true)
  }

  const handleViewEntreprise = (entreprise: Entreprise) => {
    navigate(`/admin/entreprises/${entreprise.id}`)
  }

  const handleEditEntreprise = (entreprise: Entreprise) => {
    navigate(`/admin/entreprises/${entreprise.id}/edit`)
  }

  const handleDeleteEntreprise = (entreprise: Entreprise) => {
    if (window.confirm(`Voulez-vous vraiment supprimer l'entreprise "${entreprise.nom}" ?`)) {
      // TODO: Implémenter la suppression
      toast.error('Fonction de suppression à implémenter')
    }
  }

  // Rendu personnalisé des colonnes
  const renderColumns = EntreprisesPageConfig.columns.map((col) => ({
    ...col,
    render:
      col.key === 'nom'
        ? (nom: string, entreprise: Entreprise) => (
            <div className="flex items-center gap-2">
              <div className="h-10 w-10 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 flex items-center justify-center text-white text-sm font-semibold">
                {nom[0]?.toUpperCase() || 'E'}
              </div>
              <div>
                <div className="font-medium text-gray-900">{nom}</div>
                <div className="text-sm text-gray-500">SIRET: {entreprise.siret}</div>
              </div>
            </div>
          )
        : col.key === 'email'
        ? (email: string, entreprise: Entreprise) => (
            <div className="space-y-1">
              {email && (
                <div className="flex items-center gap-1 text-sm text-gray-900">
                  <EnvelopeIcon className="h-4 w-4 text-gray-400" />
                  {email}
                </div>
              )}
              {entreprise.telephone && (
                <div className="flex items-center gap-1 text-sm text-gray-600">
                  <PhoneIcon className="h-4 w-4 text-gray-400" />
                  {entreprise.telephone}
                </div>
              )}
            </div>
          )
        : col.key === 'ville'
        ? (ville: string, entreprise: Entreprise) => (
            <div className="flex items-center gap-1 text-sm text-gray-900">
              <MapPinIcon className="h-4 w-4 text-gray-400" />
              {ville}, {entreprise.pays}
            </div>
          )
        : col.key === 'status'
        ? (status: string) => {
            const statusConfig: Record<string, { label: string; color: string }> = {
              active: { label: 'Active', color: 'bg-green-100 text-green-700' },
              inactive: { label: 'Inactive', color: 'bg-gray-100 text-gray-700' },
              pending: { label: 'En attente', color: 'bg-yellow-100 text-yellow-700' },
            }
            const config = statusConfig[status] || statusConfig.inactive
            return (
              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
                {config.label}
              </span>
            )
          }
        : (value: any) => <span className="text-sm text-gray-900">{value || '-'}</span>,
  }))

  // Configuration adaptée pour EntityListTemplate
  const templateConfig: EntityListConfig = {
    entityName: 'Entreprise',
    entityNamePlural: 'Entreprises',
    title: EntreprisesPageConfig.title,
    subtitle: EntreprisesPageConfig.subtitle,
    icon: BuildingOfficeIcon,

    columns: renderColumns,

    data: filteredData,
    isLoading,

    onSearch: setSearchQuery,
    searchPlaceholder: 'Rechercher par nom, SIRET ou email...',

    filters: [
      {
        key: 'status',
        label: 'Filtrer par statut',
        type: 'select',
        options: [
          { value: '', label: 'Tous les statuts' },
          { value: 'active', label: 'Active' },
          { value: 'inactive', label: 'Inactive' },
          { value: 'pending', label: 'En attente' },
        ],
      },
    ],

    actions: {
      create: {
        label: 'Créer une entreprise',
        onClick: handleCreateModalOpen,
        permission: 'company.create',
      },
      row: [
        {
          key: 'view',
          label: 'Voir les détails',
          icon: EyeIcon,
          onClick: handleViewEntreprise,
          variant: 'secondary' as const,
          permission: 'company.read',
        },
        {
          key: 'edit',
          label: 'Modifier',
          icon: PencilIcon,
          onClick: handleEditEntreprise,
          variant: 'primary' as const,
          permission: 'company.edit',
        },
        {
          key: 'delete',
          label: 'Supprimer',
          icon: TrashIcon,
          onClick: handleDeleteEntreprise,
          variant: 'danger' as const,
          permission: 'company.delete',
        },
      ],
    },

    emptyState: {
      message: 'Aucune entreprise trouvée',
      action: {
        label: 'Créer la première entreprise',
        onClick: handleCreateModalOpen,
      },
    },
  }

  // Permissions pour le template
  const permissions = userPermissions

  // Récupération du composant modal depuis la config
  const CreateModal = EntreprisesPageConfig.actions.create

  return (
    <>
      <EntityListTemplate config={templateConfig} permissions={permissions} />

      {/* Modale de création */}
      <CreateModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSuccess={() => {
          refetch()
          setIsCreateModalOpen(false)
          toast.success('Entreprise créée avec succès')
        }}
      />
    </>
  )
}
