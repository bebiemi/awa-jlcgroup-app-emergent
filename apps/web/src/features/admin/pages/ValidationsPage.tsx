import { useState } from 'react'
import Layout from '@/components/Layout'
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

type TabType = 'interim' | 'company' | 'collaborator'

export default function ValidationsPage() {
  const [activeTab, setActiveTab] = useState<TabType>('interim')
  const [statusFilter, setStatusFilter] = useState<string>('pending')
  const [selectedValidation, setSelectedValidation] = useState<Validation | null>(null)
  const [showRejectModal, setShowRejectModal] = useState(false)
  const [showAssignModal, setShowAssignModal] = useState(false)
  const [showBulkActionsModal, setShowBulkActionsModal] = useState(false)
  const [bulkActionType, setBulkActionType] = useState<'all' | 'interim' | 'company' | 'collaborator' | 'warnings'>('all')
  const [rejectionReason, setRejectionReason] = useState('')
  const [selectedValidator, setSelectedValidator] = useState('')
  const [selectedValidations, setSelectedValidations] = useState<string[]>([])

  const handleTileClick = (type: 'all' | 'interim' | 'company' | 'collaborator' | 'warnings') => {
    // Filter validations based on tile clicked
    let filtered = validations
    if (type === 'interim') {
      filtered = validations.filter((v: Validation) => v.validation_type === 'interim' && v.status === 'pending')
    } else if (type === 'company') {
      filtered = validations.filter((v: Validation) => v.validation_type === 'company' && v.status === 'pending')
    } else if (type === 'collaborator') {
      filtered = validations.filter((v: Validation) => v.validation_type === 'collaborator' && v.status === 'pending')
    } else if (type === 'warnings') {
      filtered = validations.filter((v: Validation) => v.has_location_warning && v.status === 'pending')
    } else {
      filtered = validations.filter((v: Validation) => v.status === 'pending')
    }
    
    // Don't open modal if no validations
    if (filtered.length === 0) {
      toast.info('Aucune validation disponible pour cette catégorie')
      return
    }
    
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
    
    if (selectedValidation?.validation_type === 'collaborator') {
      // For collaborators, only show users in RH or Commerciales groups
      // Since we don't have group membership in user data yet, filter by roles
      return allUsers.filter((user: any) => 
        user.roles?.some((role: string) => ['admin', 'super_admin'].includes(role)) ||
        user.email?.toLowerCase().includes('rh') ||
        user.email?.toLowerCase().includes('hr') ||
        user.email?.toLowerCase().includes('commercial')
      )
    }
    
    // For interim and company, show all admins and commercials
    return allUsers.filter((user: any) => 
      user.roles?.some((role: string) => ['admin', 'super_admin', 'commercial'].includes(role))
    )
  }
  
  const validators = getFilteredValidators()

  const [approveValidation] = useApproveValidationMutation()
  const [rejectValidation] = useRejectValidationMutation()
  const [addCountry] = useAddCountryFromValidationMutation()
  const [assignValidation] = useAssignValidationMutation()

  const handleApprove = async (validation: Validation) => {
    if (!confirm(`Approuver l'inscription de ${validation.user_full_name} ?`)) return

    try {
      await approveValidation({ id: validation.id }).unwrap()
      toast.success('Validation approuvée')
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de l\'approbation')
    }
  }

  const handleReject = async () => {
    if (!selectedValidation || !rejectionReason.trim()) {
      toast.error('Veuillez entrer une raison de rejet')
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
    if (!validation.missing_country) return

    if (!confirm(`Ajouter "${validation.missing_country}" à la liste des pays ?`)) return

    try {
      await addCountry(validation.id).unwrap()
      toast.success(`Pays "${validation.missing_country}" ajouté`)
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
      toast.success('Validation assignée avec succès')
      setShowAssignModal(false)
      setSelectedValidator('')
      setSelectedValidation(null)
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de l\'assignation')
    }
  }

  const getStatusBadge = (status: string) => {
    const badges = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
    }
    const labels = {
      pending: 'En attente',
      approved: 'Approuvé',
      rejected: 'Rejeté',
    }
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${badges[status as keyof typeof badges]}`}>
        {labels[status as keyof typeof labels]}
      </span>
    )
  }

  if (isLoading) {
    return (
      <Layout>
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Validations</h1>
          <p className="text-gray-600 mt-2">Gérez les demandes d'inscription des utilisateurs et entreprises</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <button
            onClick={() => handleTileClick('all')}
            className="bg-white rounded-lg shadow p-4 border-l-4 border-yellow-500 hover:shadow-lg transition-shadow cursor-pointer text-left"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">En attente</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.total_pending || 0}</p>
              </div>
              <ClockIcon className="h-8 w-8 text-yellow-500" />
            </div>
          </button>

          <button
            onClick={() => handleTileClick('interim')}
            className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500 hover:shadow-lg transition-shadow cursor-pointer text-left"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Intérimaires</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.pending_interim || 0}</p>
              </div>
              <UserIcon className="h-8 w-8 text-blue-500" />
            </div>
          </button>

          <button
            onClick={() => handleTileClick('company')}
            className="bg-white rounded-lg shadow p-4 border-l-4 border-green-500 hover:shadow-lg transition-shadow cursor-pointer text-left"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Entreprises</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.pending_company || 0}</p>
              </div>
              <BuildingOfficeIcon className="h-8 w-8 text-green-500" />
            </div>
          </button>

          <button
            onClick={() => handleTileClick('collaborator')}
            className="bg-white rounded-lg shadow p-4 border-l-4 border-purple-500 hover:shadow-lg transition-shadow cursor-pointer text-left"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Collaborateurs</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.pending_collaborator || 0}</p>
              </div>
              <UserIcon className="h-8 w-8 text-purple-500" />
            </div>
          </button>

          <button
            onClick={() => handleTileClick('warnings')}
            className="bg-white rounded-lg shadow p-4 border-l-4 border-orange-500 hover:shadow-lg transition-shadow cursor-pointer text-left"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Warnings</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.with_location_warnings || 0}</p>
              </div>
              <ExclamationTriangleIcon className="h-8 w-8 text-orange-500" />
            </div>
          </button>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
              <button
                onClick={() => setActiveTab('interim')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'interim'
                    ? 'border-jlc-purple-600 text-jlc-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Intérimaires ({stats?.pending_interim || 0})
              </button>
              <button
                onClick={() => setActiveTab('company')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'company'
                    ? 'border-jlc-purple-600 text-jlc-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Entreprises ({stats?.pending_company || 0})
              </button>
              <button
                onClick={() => setActiveTab('collaborator')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'collaborator'
                    ? 'border-jlc-purple-600 text-jlc-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Collaborateurs ({stats?.pending_collaborator || 0})
              </button>
            </nav>
          </div>

          {/* Status Filter */}
          <div className="p-4 border-b border-gray-200">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
            >
              <option value="pending">En attente</option>
              <option value="approved">Approuvées</option>
              <option value="rejected">Rejetées</option>
              <option value="">Toutes</option>
            </select>
          </div>

          {/* Validations List */}
          <div className="divide-y divide-gray-200">
            {validations.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-600">Aucune validation {statusFilter}</p>
              </div>
            ) : (
              validations.map((validation) => (
                <div key={validation.id} className="p-6 hover:bg-gray-50 transition">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">{validation.user_full_name}</h3>
                        {getStatusBadge(validation.status)}
                        
                        {/* Collaborator Badge */}
                        {validation.validation_type === 'collaborator' && (
                          <span className="inline-flex items-center px-3 py-1 text-xs font-semibold rounded-full bg-purple-100 text-purple-800 border border-purple-300">
                            <UserIcon className="h-4 w-4 mr-1" />
                            Collaborateur JLC
                          </span>
                        )}
                        
                        {validation.has_location_warning && (
                          <span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-full bg-orange-100 text-orange-800">
                            <ExclamationTriangleIcon className="h-4 w-4 mr-1" />
                            Pays non-standard
                          </span>
                        )}
                      </div>

                      <p className="text-sm text-gray-600 mb-2">{validation.user_email}</p>
                      
                      {/* Collaborator-specific info */}
                      {validation.validation_type === 'collaborator' && (
                        <div className="bg-purple-50 border border-purple-200 rounded-lg p-3 mb-2">
                          <div className="grid grid-cols-3 gap-4 text-sm">
                            {validation.employee_number && (
                              <div>
                                <span className="font-medium text-gray-700">Matricule:</span>
                                <span className="ml-1 text-gray-900">{validation.employee_number}</span>
                              </div>
                            )}
                            {validation.department && (
                              <div>
                                <span className="font-medium text-gray-700">Département:</span>
                                <span className="ml-1 text-gray-900">{validation.department}</span>
                              </div>
                            )}
                            {validation.job_title && (
                              <div>
                                <span className="font-medium text-gray-700">Poste:</span>
                                <span className="ml-1 text-gray-900">{validation.job_title}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {validation.country_name && (
                        <div className="flex items-center space-x-2 text-sm text-gray-600 mb-2">
                          <MapPinIcon className="h-4 w-4" />
                          <span>
                            {validation.country_name}
                            {validation.province_name && ` → ${validation.province_name}`}
                            {validation.city_name && ` → ${validation.city_name}`}
                            {validation.neighborhood_name && ` → ${validation.neighborhood_name}`}
                          </span>
                        </div>
                      )}

                      {validation.has_location_warning && validation.missing_country && (
                        <div className="bg-orange-50 border border-orange-200 rounded-lg p-3 mt-2">
                          <p className="text-sm text-orange-800">
                            <strong>Pays non disponible :</strong> {validation.missing_country}
                          </p>
                          <button
                            onClick={() => handleAddCountry(validation)}
                            className="mt-2 text-sm text-orange-700 hover:text-orange-900 font-medium underline"
                          >
                            + Ajouter ce pays à la liste
                          </button>
                        </div>
                      )}

                      <p className="text-xs text-gray-500 mt-2">
                        Demande créée le {new Date(validation.created_at).toLocaleDateString('fr-FR')}
                      </p>
                    </div>

                    {validation.status === 'pending' && (
                      <div className="flex flex-wrap gap-2 ml-4">
                        <button
                          onClick={() => handleApprove(validation)}
                          className="inline-flex items-center px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition text-sm"
                        >
                          <CheckCircleIcon className="h-4 w-4 mr-1" />
                          Approuver
                        </button>
                        <button
                          onClick={() => {
                            setSelectedValidation(validation)
                            setShowRejectModal(true)
                          }}
                          className="inline-flex items-center px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition text-sm"
                        >
                          <XCircleIcon className="h-4 w-4 mr-1" />
                          Rejeter
                        </button>
                        <button
                          onClick={() => {
                            setSelectedValidation(validation)
                            setShowAssignModal(true)
                          }}
                          className="inline-flex items-center px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm"
                        >
                          <UserPlusIcon className="h-4 w-4 mr-1" />
                          {validation.assigned_to ? 'Réassigner' : 'Assigner'}
                        </button>
                      </div>
                    )}
                    
                    {validation.assigned_to && (
                      <div className="mt-2 text-xs text-gray-600">
                        <span className="font-medium">Assigné à:</span> {validation.assigned_to}
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Reject Modal */}
      {showRejectModal && selectedValidation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Rejeter la validation</h3>
            <p className="text-sm text-gray-600 mb-4">
              Vous êtes sur le point de rejeter l'inscription de <strong>{selectedValidation.user_full_name}</strong>.
            </p>
            <textarea
              value={rejectionReason}
              onChange={(e) => setRejectionReason(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 mb-4"
              rows={4}
              placeholder="Raison du rejet (obligatoire)"
              required
            />
            <div className="flex space-x-3">
              <button
                onClick={() => {
                  setShowRejectModal(false)
                  setRejectionReason('')
                  setSelectedValidation(null)
                }}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
              >
                Annuler
              </button>
              <button
                onClick={handleReject}
                disabled={!rejectionReason.trim()}
                className="flex-1 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition disabled:opacity-50"
              >
                Rejeter
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Assign Validator Modal */}
      {showAssignModal && selectedValidation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Assigner un validateur</h3>
            <p className="text-sm text-gray-600 mb-2">
              Sélectionnez un validateur pour <strong>{selectedValidation.user_full_name}</strong>
            </p>
            
            {/* Info message for collaborator validation */}
            {selectedValidation.validation_type === 'collaborator' && (
              <div className="mb-4 bg-purple-50 border border-purple-200 rounded-lg p-3">
                <p className="text-xs text-purple-800">
                  ℹ️ Pour les collaborateurs, seuls les membres des équipes RH et Commerciales peuvent valider.
                </p>
              </div>
            )}
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Validateur
              </label>
              <select
                value={selectedValidator}
                onChange={(e) => setSelectedValidator(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">-- Sélectionner un validateur --</option>
                {validators.map((validator: any) => (
                  <option key={validator.id} value={validator.id}>
                    {validator.full_name} ({validator.email}) - {validator.roles?.join(', ')}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={() => {
                  setShowAssignModal(false)
                  setSelectedValidator('')
                  setSelectedValidation(null)
                }}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
              >
                Annuler
              </button>
              <button
                onClick={handleAssign}
                disabled={!selectedValidator}
                className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
              >
                Assigner
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Bulk Actions Modal */}
      {showBulkActionsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full p-6 max-h-[80vh] overflow-y-auto">
            <h3 className="text-xl font-bold text-gray-900 mb-4">
              Actions en masse - {bulkActionType === 'all' ? 'Toutes' : 
                bulkActionType === 'interim' ? 'Intérimaires' : 
                bulkActionType === 'company' ? 'Entreprises' : 
                bulkActionType === 'collaborator' ? 'Collaborateurs' : 
                'Warnings'}
            </h3>
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
              <p className="text-sm text-blue-800">
                {selectedValidations.length} validation(s) sélectionnée(s)
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Actions disponibles:</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <button
                    onClick={async () => {
                      if (!confirm(`Approuver ${selectedValidations.length} validation(s) ?`)) return
                      
                      try {
                        for (const id of selectedValidations) {
                          await approveValidation({ id }).unwrap()
                        }
                        toast.success(`${selectedValidations.length} validation(s) approuvée(s)`)
                        setShowBulkActionsModal(false)
                        setSelectedValidations([])
                        refetch()
                      } catch (error: any) {
                        toast.error(error?.data?.detail || 'Erreur lors de l\'approbation en masse')
                      }
                    }}
                    className="flex items-center justify-center px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
                  >
                    <CheckCircleIcon className="h-5 w-5 mr-2" />
                    Tout approuver
                  </button>

                  <button
                    onClick={() => {
                      const reason = prompt('Raison du rejet (obligatoire):')
                      if (!reason || !reason.trim()) {
                        toast.error('Raison du rejet requise')
                        return
                      }
                      
                      if (!confirm(`Rejeter ${selectedValidations.length} validation(s) ?`)) return
                      
                      Promise.all(
                        selectedValidations.map(id => rejectValidation({ id, reason }).unwrap())
                      ).then(() => {
                        toast.success(`${selectedValidations.length} validation(s) rejetée(s)`)
                        setShowBulkActionsModal(false)
                        setSelectedValidations([])
                        refetch()
                      }).catch((error: any) => {
                        toast.error(error?.data?.detail || 'Erreur lors du rejet en masse')
                      })
                    }}
                    className="flex items-center justify-center px-4 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
                  >
                    <XCircleIcon className="h-5 w-5 mr-2" />
                    Tout rejeter
                  </button>

                  <button
                    onClick={() => {
                      const validatorId = prompt('ID du validateur à assigner:')
                      if (!validatorId) return
                      
                      if (!confirm(`Assigner ${selectedValidations.length} validation(s) ?`)) return
                      
                      Promise.all(
                        selectedValidations.map(id => assignValidation({ id, assigned_to: validatorId }).unwrap())
                      ).then(() => {
                        toast.success(`${selectedValidations.length} validation(s) assignée(s)`)
                        setShowBulkActionsModal(false)
                        setSelectedValidations([])
                        refetch()
                      }).catch((error: any) => {
                        toast.error(error?.data?.detail || 'Erreur lors de l\'assignation en masse')
                      })
                    }}
                    className="flex items-center justify-center px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                  >
                    <UserPlusIcon className="h-5 w-5 mr-2" />
                    Assigner en masse
                  </button>

                  <button
                    onClick={() => {
                      setShowBulkActionsModal(false)
                      setSelectedValidations([])
                    }}
                    className="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
                  >
                    Annuler
                  </button>
                </div>
              </div>

              <div className="border-t pt-4">
                <h4 className="font-semibold text-gray-900 mb-2">Validations concernées:</h4>
                <div className="max-h-48 overflow-y-auto space-y-2">
                  {validations.filter((v: Validation) => selectedValidations.includes(v.id)).map((v: Validation) => (
                    <div key={v.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">{v.user_full_name}</p>
                        <p className="text-xs text-gray-500">{v.user_email}</p>
                      </div>
                      <button
                        onClick={() => setSelectedValidations(selectedValidations.filter(id => id !== v.id))}
                        className="text-red-600 hover:text-red-800"
                      >
                        <XCircleIcon className="h-5 w-5" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </Layout>
  )
}
