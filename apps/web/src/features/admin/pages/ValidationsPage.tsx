import { useState } from 'react'
import Layout from '@/components/Layout'
import Modal from '@/components/Modal'
import ActionButton, { ActionButtonGroup } from '@/components/ActionButton'
import {
  useGetValidationsQuery,
  useGetValidationStatsQuery,
  useApproveValidationMutation,
  useRejectValidationMutation,
  useAddCountryFromValidationMutation,
  useAssignValidationMutation,
  type Validation,
} from '../api/validationApi'
import { useGetUsersQuery } from '../api/usersApi'
import { useReferences } from '@/hooks/useReferences'
import {
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  MapPinIcon,
  UserIcon,
  BuildingOfficeIcon,
  UserPlusIcon,
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'
import { ValidationTypes, UserRoles, getRoleLabel } from '@/constants/iamConstants'

type TabType = 'candidat' | 'company' | 'collaborator'

export default function ValidationsPage() {
  // Charger les référentiels de configuration
  const { options: validationTypes = [] } = useReferences('validation_types')
  const { options: validationStatuses = [] } = useReferences('validation_statuses')
  
  const validationTypesConfig = {
    candidat: validationTypes.find(vt => vt.code === ValidationTypes.CANDIDAT)?.code || ValidationTypes.CANDIDAT,
    interim: validationTypes.find(vt => vt.code === ValidationTypes.INTERIM)?.code || ValidationTypes.INTERIM,
    company: validationTypes.find(vt => vt.code === ValidationTypes.COMPANY)?.code || ValidationTypes.COMPANY,
    collaborator: validationTypes.find(vt => vt.code === ValidationTypes.COLLABORATEUR)?.code || ValidationTypes.COLLABORATEUR
  }
  
  const validationStatusesConfig = {
    pending: validationStatuses.find(vs => vs.code === 'pending')?.code || 'pending',
    approved: validationStatuses.find(vs => vs.code === 'approved')?.code || 'approved',
    rejected: validationStatuses.find(vs => vs.code === 'rejected')?.code || 'rejected'
  }
  
  const [activeTab, setActiveTab] = useState<TabType>('candidat')
  const [statusFilter, setStatusFilter] = useState<string>(validationStatusesConfig.pending)
  const [selectedValidation, setSelectedValidation] = useState<Validation | null>(null)
  const [showRejectModal, setShowRejectModal] = useState(false)
  const [showAssignModal, setShowAssignModal] = useState(false)
  const [showBulkActionsModal, setShowBulkActionsModal] = useState(false)
  const [bulkActionType, setBulkActionType] = useState<'all' | 'candidat' | 'interim' | 'company' | 'collaborator' | 'warnings'>('all')
  const [rejectionReason, setRejectionReason] = useState('')
  const [selectedValidator, setSelectedValidator] = useState('')
  const [selectedValidations, setSelectedValidations] = useState<string[]>([])
  const [showDetailPanel, setShowDetailPanel] = useState(false)
  const [detailValidation, setDetailValidation] = useState<Validation | null>(null)

  const handleViewDetail = (validation: Validation) => {
    setDetailValidation(validation)
    setShowDetailPanel(true)
  }

  const handleTileClick = (type: 'all' | 'candidat' | 'interim' | 'company' | 'collaborator' | 'warnings') => {
    // Filter validations based on tile clicked
    let filtered = validations
    if (type === 'candidat') {
      filtered = validations.filter((v: Validation) => v.validation_type === validationTypesConfig.candidat && v.status === validationStatusesConfig.pending)
    } else if (type === 'interim') {
      filtered = validations.filter((v: Validation) => v.validation_type === validationTypesConfig.interim && v.status === validationStatusesConfig.pending)
    } else if (type === 'company') {
      filtered = validations.filter((v: Validation) => v.validation_type === validationTypesConfig.company && v.status === validationStatusesConfig.pending)
    } else if (type === 'collaborator') {
      filtered = validations.filter((v: Validation) => v.validation_type === validationTypesConfig.collaborator && v.status === validationStatusesConfig.pending)
    } else if (type === 'warnings') {
      filtered = validations.filter((v: Validation) => v.has_location_warning && v.status === validationStatusesConfig.pending)
    } else {
      filtered = validations.filter((v: Validation) => v.status === validationStatusesConfig.pending)
    }
    
    // Don't open modal if no validations
    if (filtered.length === 0) {
      toast.error('Aucune validation disponible pour cette catégorie')
      return
    }
    
    // Select all validations of this type
    setBulkActionType(type)
    setSelectedValidations(filtered.map((v: Validation) => v.id))
    setShowBulkActionsModal(true)
  }

  const { data: stats } = useGetValidationStatsQuery()
  const { data: validations = [], isLoading, refetch } = useGetValidationsQuery({
    validation_type: activeTab,
    status: statusFilter,
    page: 1,
    page_size: 50,
  })

  // Fetch validators (admins and commercials)
  const { data: usersData } = useGetUsersQuery({ page: 1, page_size: 200 })
  
  // Filter validators based on validation type
  const getFilteredValidators = () => {
    const allUsers = usersData?.users || []
    
    // For interim and company, show all admins and commercials
    return allUsers.filter(user =>
      user.roles.includes(UserRoles.ADMIN) ||
      user.roles.includes(UserRoles.SUPER_ADMIN) ||
      user.roles.includes('commercial')
    )
  }

  const validators = getFilteredValidators()

  const [approveValidation] = useApproveValidationMutation()
  const [rejectValidation] = useRejectValidationMutation()
  const [addCountryFromValidation] = useAddCountryFromValidationMutation()
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

  const handleAddCountry = async (validation: Validation) => {
    try {
      await addCountryFromValidation(validation.id).unwrap()
      toast.success('Pays ajouté à la liste')
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de l\'ajout du pays')
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

  const handleBulkApprove = async () => {
    if (selectedValidations.length === 0) {
      toast.error('Aucune validation sélectionnée')
      return
    }

    try {
      // Approuver toutes les validations sélectionnées
      await Promise.all(
        selectedValidations.map(id => approveValidation({ id }).unwrap())
      )
      toast.success(`${selectedValidations.length} validation(s) approuvée(s)`)
      setShowBulkActionsModal(false)
      setSelectedValidations([])
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de l\'approbation en masse')
    }
  }

  const handleBulkReject = async () => {
    if (selectedValidations.length === 0) {
      toast.error('Aucune validation sélectionnée')
      return
    }

    if (!rejectionReason.trim()) {
      toast.error('Veuillez fournir une raison du rejet')
      return
    }

    try {
      // Rejeter toutes les validations sélectionnées
      await Promise.all(
        selectedValidations.map(id => 
          rejectValidation({ id, rejection_reason: rejectionReason }).unwrap()
        )
      )
      toast.success(`${selectedValidations.length} validation(s) rejetée(s)`)
      setShowBulkActionsModal(false)
      setSelectedValidations([])
      setRejectionReason('')
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors du rejet en masse')
    }
  }

  const getValidationTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      [ValidationTypes.CANDIDAT]: getRoleLabel(UserRoles.CANDIDAT),
      [ValidationTypes.INTERIM]: getRoleLabel(UserRoles.INTERIM),
      [ValidationTypes.COMPANY]: getRoleLabel(UserRoles.COMPANY),
      [ValidationTypes.COLLABORATEUR]: getRoleLabel(UserRoles.COLLABORATEUR),
    }
    return labels[type] || type
  }

  return (
    <Layout>
      <div className="p-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Validations</h1>
          <p className="text-gray-600">Gérer les validations des comptes utilisateurs</p>
        </div>

        {/* Stats tiles */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {/* Candidats Tile */}
          <div
            className="bg-white rounded-lg p-6 border border-gray-200 hover:border-blue-500 hover:shadow-md cursor-pointer transition-all"
            onClick={() => handleTileClick('candidat')}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Candidats</p>
                <p className="text-2xl font-bold text-gray-900">{(stats?.pending_candidat || 0) + (stats?.pending_interim || 0)}</p>
              </div>
              <UserIcon className="w-10 h-10 text-blue-500" />
            </div>
          </div>

          {/* Companies Tile */}
          <div
            className="bg-white rounded-lg p-6 border border-gray-200 hover:border-indigo-500 hover:shadow-md cursor-pointer transition-all"
            onClick={() => handleTileClick('company')}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Entreprises</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.pending_company || 0}</p>
              </div>
              <BuildingOfficeIcon className="w-10 h-10 text-indigo-500" />
            </div>
          </div>

          {/* Collaborators Tile */}
          <div
            className="bg-white rounded-lg p-6 border border-gray-200 hover:border-green-500 hover:shadow-md cursor-pointer transition-all"
            onClick={() => handleTileClick('collaborator')}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Collaborateurs</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.pending_collaborator || 0}</p>
              </div>
              <UserPlusIcon className="w-10 h-10 text-green-500" />
            </div>
          </div>

          {/* Warnings Tile */}
          <div
            className="bg-white rounded-lg p-6 border border-gray-200 hover:border-yellow-500 hover:shadow-md cursor-pointer transition-all"
            onClick={() => handleTileClick('warnings')}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avertissements</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.location_warnings || 0}</p>
              </div>
              <ExclamationTriangleIcon className="w-10 h-10 text-yellow-500" />
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow">
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

          {/* Validations List */}
          <div className="p-6">
            {isLoading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                <p className="mt-4 text-gray-500">Chargement...</p>
              </div>
            ) : validations.length === 0 ? (
              <div className="text-center py-12">
                <CheckCircleIcon className="mx-auto h-12 w-12 text-gray-400" />
                <p className="mt-2 text-gray-500">Aucune validation en attente</p>
              </div>
            ) : (
              <div className="space-y-4">
                {validations.map((validation) => (
                  <div key={validation.id} className="border border-gray-200 rounded-lg p-4 hover:border-blue-500 transition">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h3 className="text-lg font-medium text-gray-900">{validation.full_name}</h3>
                          <span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                            {getValidationTypeLabel(validation.validation_type)}
                          </span>
                          {validation.validation_type === ValidationTypes.COLLABORATEUR && (
                            <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                              Collaborateur JLC
                            </span>
                          )}
                          {validation.has_location_warning && (
                            <ExclamationTriangleIcon className="w-5 h-5 text-yellow-500" />
                          )}
                        </div>
                        <p className="text-sm text-gray-500">{validation.email}</p>
                        {validation.phone && (
                          <p className="text-sm text-gray-500">{validation.phone}</p>
                        )}
                        {validation.location && validation.location_label && (
                          <div className="flex items-center gap-1 mt-1">
                            <MapPinIcon className="w-4 h-4 text-gray-400" />
                            <p className="text-sm text-gray-500">{validation.location_label}</p>
                          </div>
                        )}
                      </div>
                      <ActionButtonGroup>
                        <ActionButton
                          type="view"
                          onClick={() => handleViewDetail(validation)}
                          label="Voir détails"
                        />
                        <ActionButton
                          type="approve"
                          onClick={() => handleApprove(validation)}
                          label="Approuver"
                        />
                        <ActionButton
                          type="reject"
                          onClick={() => {
                            setSelectedValidation(validation)
                            setShowRejectModal(true)
                          }}
                          label="Rejeter"
                        />
                        <ActionButton
                          type="assign"
                          onClick={() => {
                            setSelectedValidation(validation)
                            setShowAssignModal(true)
                          }}
                          label="Assigner"
                        />
                        {validation.has_location_warning && (
                          <ActionButton
                            type="custom"
                            icon={MapPinIcon}
                            color="text-yellow-600 hover:bg-yellow-50"
                            onClick={() => handleAddCountry(validation)}
                            label="Ajouter le pays"
                          />
                        )}
                      </ActionButtonGroup>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

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
            {selectedValidation?.validation_type === ValidationTypes.COLLABORATEUR && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <p className="text-sm text-blue-800">
                  ℹ️ Pour les collaborateurs, seuls les membres des équipes RH et Commerciales peuvent valider.
                </p>
              </div>
            )}
            <select
              value={selectedValidator}
              onChange={(e) => setSelectedValidator(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Sélectionner un validateur</option>
              {validators.map((validator) => (
                <option key={validator.id} value={validator.id}>
                  {validator.full_name || validator.username} ({getRoleLabel(validator.roles[0])})
                </option>
              ))}
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

        {/* Bulk Actions Modal */}
        <Modal
          isOpen={showBulkActionsModal}
          onClose={() => {
            setShowBulkActionsModal(false)
            setSelectedValidations([])
            setRejectionReason('')
          }}
          title="Actions groupées"
        >
          <div className="space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm font-medium text-blue-900">
                {selectedValidations.length} validation(s) sélectionnée(s)
              </p>
              <p className="text-xs text-blue-700 mt-1">
                Type : {
                  bulkActionType === 'candidat' ? 'Candidats' :
                  bulkActionType === 'interim' ? 'Intérimaires' :
                  bulkActionType === 'company' ? 'Entreprises' :
                  bulkActionType === 'collaborator' ? 'Collaborateurs' :
                  bulkActionType === 'warnings' ? 'Avertissements' :
                  'Toutes'
                }
              </p>
            </div>

            {/* Rejection reason (shown when needed) */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Raison du rejet (optionnel pour approbation, requis pour rejet)
              </label>
              <textarea
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
                placeholder="Entrez une raison..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows={3}
              />
            </div>

            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowBulkActionsModal(false)
                  setSelectedValidations([])
                  setRejectionReason('')
                }}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Annuler
              </button>
              <button
                onClick={handleBulkReject}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 flex items-center gap-2"
              >
                <XCircleIcon className="w-4 h-4" />
                Rejeter tout ({selectedValidations.length})
              </button>
              <button
                onClick={handleBulkApprove}
                className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 flex items-center gap-2"
              >
                <CheckCircleIcon className="w-4 h-4" />
                Approuver tout ({selectedValidations.length})
              </button>
            </div>
          </div>
        </Modal>

        {/* Detail Panel Modal */}
        <Modal
          isOpen={showDetailPanel}
          onClose={() => {
            setShowDetailPanel(false)
            setDetailValidation(null)
          }}
          title="Détail de la validation"
        >
          {detailValidation && (
            <div className="space-y-6">
              {/* User Info */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                  <UserIcon className="w-5 h-5" />
                  Informations utilisateur
                </h3>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <p className="text-xs text-gray-500">Nom complet</p>
                    <p className="text-sm font-medium text-gray-900">{detailValidation.full_name}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Type</p>
                    <p className="text-sm font-medium text-gray-900">{getValidationTypeLabel(detailValidation.validation_type)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Email</p>
                    <p className="text-sm font-medium text-gray-900">{detailValidation.email}</p>
                  </div>
                  {detailValidation.phone && (
                    <div>
                      <p className="text-xs text-gray-500">Téléphone</p>
                      <p className="text-sm font-medium text-gray-900">{detailValidation.phone}</p>
                    </div>
                  )}
                  {detailValidation.location_label && (
                    <div>
                      <p className="text-xs text-gray-500">Localisation</p>
                      <p className="text-sm font-medium text-gray-900 flex items-center gap-1">
                        <MapPinIcon className="w-4 h-4 text-gray-400" />
                        {detailValidation.location_label}
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* Company Info (for company type) */}
              {detailValidation.validation_type === ValidationTypes.COMPANY && detailValidation.company_name && (
                <div className="bg-indigo-50 rounded-lg p-4">
                  <h3 className="text-sm font-semibold text-indigo-900 mb-3 flex items-center gap-2">
                    <BuildingOfficeIcon className="w-5 h-5" />
                    Informations entreprise
                  </h3>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <p className="text-xs text-indigo-600">Nom de l'entreprise</p>
                      <p className="text-sm font-medium text-indigo-900">{detailValidation.company_name}</p>
                    </div>
                    {(detailValidation as any).company_siret && (
                      <div>
                        <p className="text-xs text-indigo-600">SIRET</p>
                        <p className="text-sm font-medium text-indigo-900">{(detailValidation as any).company_siret}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Manager Info */}
              {(detailValidation as any).created_by_name && (
                <div className="bg-blue-50 rounded-lg p-4">
                  <h3 className="text-sm font-semibold text-blue-900 mb-3 flex items-center gap-2">
                    <UserPlusIcon className="w-5 h-5" />
                    Créé par (Manager)
                  </h3>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <p className="text-xs text-blue-600">Nom</p>
                      <p className="text-sm font-medium text-blue-900">{(detailValidation as any).created_by_name}</p>
                    </div>
                    {(detailValidation as any).created_by_email && (
                      <div>
                        <p className="text-xs text-blue-600">Email</p>
                        <p className="text-sm font-medium text-blue-900">{(detailValidation as any).created_by_email}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Warnings */}
              {detailValidation.has_location_warning && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <ExclamationTriangleIcon className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <h4 className="text-sm font-semibold text-yellow-900">Avertissement de localisation</h4>
                      <p className="text-sm text-yellow-700 mt-1">
                        Le pays de cette validation n'est pas dans la liste autorisée. Vous pouvez l'ajouter directement.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex justify-end gap-3 pt-4 border-t">
                <button
                  onClick={() => setShowDetailPanel(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Fermer
                </button>
                {detailValidation.has_location_warning && (
                  <button
                    onClick={() => {
                      handleAddCountry(detailValidation)
                      setShowDetailPanel(false)
                    }}
                    className="px-4 py-2 text-sm font-medium text-white bg-yellow-600 rounded-lg hover:bg-yellow-700 flex items-center gap-2"
                  >
                    <MapPinIcon className="w-4 h-4" />
                    Ajouter le pays
                  </button>
                )}
                <button
                  onClick={() => {
                    setSelectedValidation(detailValidation)
                    setShowDetailPanel(false)
                    setShowRejectModal(true)
                  }}
                  className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 flex items-center gap-2"
                >
                  <XCircleIcon className="w-4 h-4" />
                  Rejeter
                </button>
                <button
                  onClick={() => {
                    handleApprove(detailValidation)
                    setShowDetailPanel(false)
                  }}
                  className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 flex items-center gap-2"
                >
                  <CheckCircleIcon className="w-4 h-4" />
                  Approuver
                </button>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </Layout>
  )
}
