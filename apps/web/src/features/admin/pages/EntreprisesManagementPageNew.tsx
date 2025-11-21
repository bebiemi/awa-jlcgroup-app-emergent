/**
 * Entreprises Management Page - Refactorisée avec EntityListTemplate
 * Configuration complète, zéro duplication
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import EntityListTemplate, { type EntityListConfig } from '@/templates/EntityListTemplate'
import { usePermissions } from '@/hooks/usePermission'
import {
  useListEntreprisesQuery,
  useUpdateEntrepriseMutation,
  type Entreprise,
} from '@/features/company/api/entrepriseApi'
import {
  BuildingOfficeIcon,
  PencilIcon,
  EyeIcon,
  MapPinIcon,
  EnvelopeIcon,
  PhoneIcon,
} from '@heroicons/react/24/outline'
import CreateEntrepriseModal from '../components/CreateEntrepriseModal'
import toast from 'react-hot-toast'

export default function EntreprisesManagementPageNew() {
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)

  const { permissions } = usePermissions([
    'company.create',
    'company.read',
    'company.edit',
    'company.delete',
  ])

  const { data = [], isLoading, refetch } = useListEntreprisesQuery({ limit: 1000 })
  const [updateEntreprise] = useUpdateEntrepriseMutation()

  const handleCreateModalOpen = () => {
    setIsCreateModalOpen(true)
  }

  const handleViewEntreprise = (entreprise: Entreprise) => {
    navigate(`/admin/entreprises/${entreprise.id}`)
  }

  const handleEditEntreprise = (entreprise: Entreprise) => {
    navigate(`/admin/entreprises/${entreprise.id}/edit`)
  }

  // Filtrer selon recherche et statut
  const filteredData = data.filter((e: Entreprise) => {
    const matchesSearch = 
      e.nom?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      e.siret?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      e.email?.toLowerCase().includes(searchQuery.toLowerCase())
    
    const matchesStatus = !statusFilter || e.status === statusFilter
    
    return matchesSearch && matchesStatus
  })

  const config: EntityListConfig = {
    entityName: 'Entreprise',
    entityNamePlural: 'Entreprises',
    title: 'Gestion des Entreprises',
    subtitle: 'Gérez toutes les entreprises inscrites sur la plateforme',
    icon: BuildingOfficeIcon,

    columns: [
      {
        key: 'nom',
        label: 'Entreprise',
        sortable: true,
        render: (nom: string, entreprise: Entreprise) => (
          <div className="flex items-center gap-2">
            <div className="h-10 w-10 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 flex items-center justify-center text-white text-sm font-semibold">
              {nom[0]?.toUpperCase() || 'E'}
            </div>
            <div>
              <div className="font-medium text-gray-900">{nom}</div>
              <div className="text-sm text-gray-500">SIRET: {entreprise.siret}</div>
            </div>
          </div>
        ),
      },
      {
        key: 'email',
        label: 'Contact',
        render: (email: string, entreprise: Entreprise) => (
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
        ),
      },
      {
        key: 'ville',
        label: 'Localisation',
        render: (ville: string, entreprise: Entreprise) => (
          <div className="flex items-center gap-1 text-sm text-gray-900">
            <MapPinIcon className="h-4 w-4 text-gray-400" />
            {ville}, {entreprise.pays}
          </div>
        ),
      },
      {
        key: 'secteur_activite',
        label: 'Secteur',
        render: (secteur: string) => (
          <span className="text-sm text-gray-900">{secteur || '-'}</span>
        ),
      },
      {
        key: 'effectif',
        label: 'Effectif',
        render: (effectif: string) => (
          <span className="text-sm text-gray-900">{effectif || '-'}</span>
        ),
      },
      {
        key: 'status',
        label: 'Statut',
        render: (status: string) => {
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
          variant: 'secondary',
          permission: 'company.read',
        },
        {
          key: 'edit',
          label: 'Modifier',
          icon: PencilIcon,
          onClick: handleEditEntreprise,
          variant: 'primary',
          permission: 'company.edit',
        },
      ],
    },

    data: filteredData,
    isLoading,

    onSearch: (query: string) => {
      setSearchQuery(query)
    },
    searchPlaceholder: 'Rechercher par nom, SIRET ou email...',

    emptyState: {
      message: 'Aucune entreprise trouvée',
      action: {
        label: 'Créer la première entreprise',
        onClick: handleCreateModalOpen,
      },
    },
  }

  return (
    <>
      <EntityListTemplate config={config} permissions={permissions} />
      <CreateEntrepriseModal
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
