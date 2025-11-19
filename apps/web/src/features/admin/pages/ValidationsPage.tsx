import { useState, useEffect } from 'react'
import Layout from '@/components/Layout'
import Modal from '@/components/Modal'
import ActionButton, { ActionButtonGroup } from '@/components/ActionButton'
import RepresentantExistantBadge from '../components/RepresentantExistantBadge'
import AttachToExistingModal from '../components/AttachToExistingModal'
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

export default function ValidationsPage() {
  const [selectedType, setSelectedType] = useState<string>('all')
  const [selectedStatus, setSelectedStatus] = useState<string>('pending')
  const [selectedValidation, setSelectedValidation] = useState<Validation | null>(null)
  const [showApproveModal, setShowApproveModal] = useState(false)
  const [showRejectModal, setShowRejectModal] = useState(false)
  const [showAssignModal, setShowAssignModal] = useState(false)
  const [showBulkActionsModal, setShowBulkActionsModal] = useState(false)
  const [showAttachModal, setShowAttachModal] = useState(false)
  const [bulkActionType, setBulkActionType] = useState<'all' | 'candidat' | 'interim' | 'company' | 'collaborator' | 'warnings'>('all')
  const [rejectionReason, setRejectionReason] = useState('')
  const [selectedValidator, setSelectedValidator] = useState('')
  const [selectedValidations, setSelectedValidations] = useState<string[]>([])
  const [contactConfirmation, setContactConfirmation] = useState(false)

  // Charger les entreprises du représentant quand la modal s'ouvre
  useEffect(() => {
    if (showAttachModal && selectedValidation?.existing_representant_user_id) {
      loadRepresentantEntreprises(selectedValidation.existing_representant_user_id)
    }
  }, [showAttachModal, selectedValidation])

  const loadRepresentantEntreprises = async (userId: string) => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/validations/representant/${userId}/details`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      )

      if (response.ok) {
        const data = await response.json()
        setRepresentantEntreprises(data.entreprises || [])
      }
    } catch (error) {
      console.error('Error loading representant entreprises:', error)
      setRepresentantEntreprises([])
    }
  }

  const { data: validations = [], isLoading, refetch } = useGetValidationsQuery({
    type: selectedType === 'all' ? undefined : selectedType,
    status: selectedStatus === 'all' ? undefined : selectedStatus,
  })

  const { data: stats } = useGetValidationStatsQuery()
  const { data: users = [] } = useGetUsersQuery({ page: 1, page_size: 1000 })
  const { references } = useReferences()

  const [approveValidation] = useApproveValidationMutation()
  const [rejectValidation] = useRejectValidationMutation()
  const [addCountry] = useAddCountryFromValidationMutation()
  const [assignValidation] = useAssignValidationMutation()

  const handleTileClick = (type: 'all' | 'candidat' | 'interim' | 'company' | 'collaborator' | 'warnings') => {
    // Filter validations based on type
    let filtered: Validation[] = []
    if (type === 'all') {
      filtered = validations.filter((v: Validation) => v.status === validationStatusesConfig.pending)
    } else if (type === 'warnings') {
      filtered = validations.filter((v: Validation) => 
        v.status === validationStatusesConfig.pending && v.has_location_warning
      )
    } else {
      filtered = validations.filter((v: Validation) => v.status === validationStatusesConfig.pending)
    }
    
    // Don't open modal if no validations
    if (filtered.length === 0) {
      toast('Aucune validation disponible pour cette catégorie')
      return
    }
    
    setBulkActionType(type)
    setShowBulkActionsModal(true)
  }

  // ... rest of the file content remains the same
}
