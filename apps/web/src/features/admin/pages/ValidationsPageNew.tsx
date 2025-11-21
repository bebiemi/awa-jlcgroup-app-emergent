/**
 * Validations Page - Refactorisée avec EntityListTemplate
 * Configuration complète, zéro duplication
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import EntityListTemplate, { type EntityListConfig } from '@/templates/EntityListTemplate'
import { usePermissions } from '@/hooks/usePermission'
import {
  useGetValidationsQuery,
  useGetValidationStatsQuery,
  useApproveValidationMutation,
  useRejectValidationMutation,
  useAssignValidationMutation,
  type Validation,
} from '../api/validationApi'
import {
  UserIcon,
  CheckCircleIcon,
  XCircleIcon,
  UserPlusIcon,
  ExclamationTriangleIcon,
  MapPinIcon,
} from '@heroicons/react/24/outline'
import Modal from '@/components/Modal'
import { ValidationTypes, getRoleLabel } from '@/constants/iamConstants'
import toast from 'react-hot-toast'

type TabType = 'candidat' | 'company' | 'collaborator'

export default function ValidationsPageNew() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<TabType>('candidat')
  const [statusFilter, setStatusFilter] = useState('pending')
  const [selectedValidation, setSelectedValidation] = useState<Validation | null>(null)
  const [showRejectModal, setShowRejectModal] = useState(false)
  const [showAssignModal, setShowAssignModal] = useState(false)
  const [rejectionReason, setRejectionReason] = useState('')
  const [selectedValidator, setSelectedValidator] = useState('')

  const { permissions } = usePermissions([
    'validations.read',
    'validations.manage',
    'validations.approve',
    'validations.reject',
  ])

  const { data: stats } = useGetValidationStatsQuery()
  const { data: validations = [], isLoading, refetch } = useGetValidationsQuery({
    validation_type: activeTab,
    status: statusFilter,
    page: 1,
    page_size: 50,
  })

  const [approveValidation] = useApproveValidationMutation()
  const [rejectValidation] = useRejectValidationMutation()
  const [assignValidation] = useAssignValidationMutation()

  const handleApprove = async (validation: Validation) => {
    try {
      await approveValidation({ id: validation.id }).unwrap()
      toast.success('Validation approuvée avec succès')
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de l\'approbation')
    }
  }

  const handleReject = async () => {
    if (!selectedValidation || !rejectionReason.trim()) {
      toast.error('Veuillez fournir une raison du rejet')
      return
    }

    try {
      await rejectValidation({
        id: selectedValidation.id,
        rejection_reason: rejectionReason,
      }).unwrap()
      toast.success('Validation rejetée')
      setShowRejectModal(false)
      setRejectionReason('')
      setSelectedValidation(null)
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors du rejet')
    }
  }

  const handleAssign = async () => {
    if (!selectedValidation || !selectedValidator) {
      toast.error('Veuillez sélectionner un validateur')
      return
    }

    try {
      await assignValidation({
        id: selectedValidation.id,
        assigned_to: selectedValidator,
      }).unwrap()
      toast.success('Validateur assigné')
      setShowAssignModal(false)
      setSelectedValidator('')
      setSelectedValidation(null)
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de l\'assignation')
    }
  }

  const handleViewDetail = (validation: Validation) => {
    navigate(`/admin/validations/${validation.id}`)
  }

  const getValidationTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      [ValidationTypes.CANDIDAT]: getRoleLabel('candidat'),
      [ValidationTypes.INTERIM]: getRoleLabel('interim'),
      [ValidationTypes.COMPANY]: getRoleLabel('company'),
      [ValidationTypes.COLLABORATEUR]: getRoleLabel('collaborateur'),
    }
    return labels[type] || type
  }

  const config: EntityListConfig = {
    entityName: 'Validation',
    entityNamePlural: 'Validations',
    title: 'Gestion des Validations',
    subtitle: 'Gérez les validations des comptes utilisateurs',
    icon: CheckCircleIcon,

    columns: [
      {
        key: 'user_full_name',
        label: 'Utilisateur',
        sortable: true,
        render: (name: string, validation: Validation) => (
          <div className="flex items-center gap-2">
            <div className="h-10 w-10 rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 flex items-center justify-center text-white text-sm font-semibold">
              {name[0]?.toUpperCase() || 'U'}
            </div>
            <div>
              <div className="font-medium text-gray-900">{name}</div>
              <div className="text-sm text-gray-500">{validation.user_email}</div>
            </div>
          </div>
        ),
      },
      {
        key: 'validation_type',
        label: 'Type',
        render: (type: string) => (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            {getValidationTypeLabel(type)}
          </span>
        ),
      },
      {
        key: 'country_name',
        label: 'Localisation',
        render: (country: string, validation: Validation) => (
          <div className="flex items-center gap-1 text-sm text-gray-900">
            <MapPinIcon className="h-4 w-4 text-gray-400" />
            {[country, validation.city_name].filter(Boolean).join(', ') || '-'}
          </div>
        ),
      },
      {
        key: 'has_location_warning',
        label: 'Avertissements',
        render: (hasWarning: boolean) => (
          hasWarning ? (
            <div className="flex items-center gap-1 text-yellow-600">
              <ExclamationTriangleIcon className="h-5 w-5" />
              <span className="text-xs">Pays non autorisé</span>
            </div>
          ) : (
            <span className="text-xs text-gray-500">-</span>
          )
        ),
      },
      {
        key: 'status',
        label: 'Statut',
        render: (status: string) => {
          const statusConfig: Record<string, { label: string; color: string }> = {
            pending: { label: 'En attente', color: 'bg-yellow-100 text-yellow-700' },
            approved: { label: 'Approuvée', color: 'bg-green-100 text-green-700' },
            rejected: { label: 'Rejetée', color: 'bg-red-100 text-red-700' },
          }
          const config = statusConfig[status] || statusConfig.pending
          return (
            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
              {config.label}
            </span>
          )
        },
      },
      {
        key: 'created_at',
        label: 'Date de demande',
        render: (date: string) => new Date(date).toLocaleDateString('fr-FR'),
      },
    ],

    filters: [
      {
        key: 'status',
        label: 'Filtrer par statut',
        type: 'select',
        options: [
          { value: 'pending', label: 'En attente' },
          { value: 'approved', label: 'Approuvées' },
          { value: 'rejected', label: 'Rejetées' },
        ],
      },
    ],

    actions: {
      row: [
        {
          key: 'view',
          label: 'Voir les détails',
          icon: UserIcon,
          onClick: handleViewDetail,
          variant: 'secondary',
          permission: 'validations.read',
        },
        {
          key: 'approve',
          label: 'Approuver',
          icon: CheckCircleIcon,
          onClick: handleApprove,
          variant: 'primary',
          permission: 'validations.approve',
          show: (validation: Validation) => validation.status === 'pending',
        },
        {
          key: 'reject',
          label: 'Rejeter',
          icon: XCircleIcon,
          onClick: (validation: Validation) => {
            setSelectedValidation(validation)
            setShowRejectModal(true)
          },
          variant: 'danger',
          permission: 'validations.reject',
          show: (validation: Validation) => validation.status === 'pending',
        },
        {
          key: 'assign',
          label: 'Assigner',
          icon: UserPlusIcon,
          onClick: (validation: Validation) => {
            setSelectedValidation(validation)
            setShowAssignModal(true)
          },
          variant: 'secondary',
          permission: 'validations.manage',
          show: (validation: Validation) => validation.status === 'pending',
        },
      ],
    },

    data: validations,
    isLoading,

    onSearch: () => {},
    searchPlaceholder: 'Rechercher une validation...',

    emptyState: {
      message: 'Aucune validation en attente',
    },
  }

  return (
    <>
      {/* Tabs de navigation */}
      <div className="bg-white rounded-lg shadow mb-6">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-4 px-6" aria-label="Tabs">
            <button
              onClick={() => setActiveTab('candidat')}
              className={`
                ${activeTab === 'candidat'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Candidats ({(stats?.pending_candidat || 0) + (stats?.pending_interim || 0)})
            </button>
            <button
              onClick={() => setActiveTab('company')}
              className={`
                ${activeTab === 'company'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Entreprises ({stats?.pending_company || 0})
            </button>
            <button
              onClick={() => setActiveTab('collaborator')}
              className={`
                ${activeTab === 'collaborator'
                  ? 'border-green-500 text-green-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Collaborateurs ({stats?.pending_collaborator || 0})
            </button>
          </nav>
        </div>
      </div>

      <EntityListTemplate config={config} permissions={permissions} />

      {/* Reject Modal */}
      <Modal
        isOpen={showRejectModal}
        onClose={() => {
          setShowRejectModal(false)
          setRejectionReason('')
          setSelectedValidation(null)
        }}
        title="Rejeter la validation"
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-500">
            Veuillez fournir une raison pour le rejet de cette validation.
          </p>
          <textarea
            value={rejectionReason}
            onChange={(e) => setRejectionReason(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
            rows={4}
            placeholder="Raison du rejet..."
          />
          <div className="flex justify-end gap-2">
            <button
              onClick={() => {
                setShowRejectModal(false)
                setRejectionReason('')
                setSelectedValidation(null)
              }}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Annuler
            </button>
            <button
              onClick={handleReject}
              className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700"
              disabled={!rejectionReason.trim()}
            >
              Rejeter
            </button>
          </div>
        </div>
      </Modal>

      {/* Assign Validator Modal */}
      <Modal
        isOpen={showAssignModal}
        onClose={() => {
          setShowAssignModal(false)
          setSelectedValidator('')
          setSelectedValidation(null)
        }}
        title="Assigner un validateur"
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-500">
            Sélectionnez un validateur pour cette demande.
          </p>
          <select
            value={selectedValidator}
            onChange={(e) => setSelectedValidator(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Sélectionner un validateur</option>
            {/* TODO: Load validators dynamically */}
          </select>
          <div className="flex justify-end gap-2">
            <button
              onClick={() => {
                setShowAssignModal(false)
                setSelectedValidator('')
                setSelectedValidation(null)
              }}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Annuler
            </button>
            <button
              onClick={handleAssign}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
              disabled={!selectedValidator}
            >
              Assigner
            </button>
          </div>
        </div>
      </Modal>
    </>
  )
}
