/**
 * Représentant Existant Badge & Details
 * Phase 2: Display warning when legal representative already exists
 */
import { useState, useEffect } from 'react'
import {
  ExclamationTriangleIcon,
  BuildingOfficeIcon,
  UserIcon,
  ChevronDownIcon,
  ChevronUpIcon,
} from '@heroicons/react/24/outline'
import type { Validation } from '../api/validationApi'

interface RepresentantEntreprise {
  id: string
  nom: string
  email?: string
  status: string
  created_at?: string
}

interface RepresentantDetails {
  found: boolean
  user?: {
    id: string
    full_name: string
    email: string
    username: string
    status: string
    created_at: string
  }
  entreprises: RepresentantEntreprise[]
  total_entreprises: number
}

interface Props {
  validation: Validation
  onAttachClick?: () => void
  onRejectClick?: () => void
}

export default function RepresentantExistantBadge({ validation, onAttachClick, onRejectClick }: Props) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [details, setDetails] = useState<RepresentantDetails | null>(null)
  const [isLoadingDetails, setIsLoadingDetails] = useState(false)

  // Vérifier si c'est une validation company avec représentant existant
  const hasExistingRepresentant = validation.has_existing_representant && 
                                   validation.existing_representant_user_id

  useEffect(() => {
    if (isExpanded && hasExistingRepresentant && !details) {
      loadRepresentantDetails()
    }
  }, [isExpanded, hasExistingRepresentant])

  const loadRepresentantDetails = async () => {
    if (!validation.existing_representant_user_id) return

    setIsLoadingDetails(true)
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/validations/representant/${validation.existing_representant_user_id}/details`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      )

      if (response.ok) {
        const data = await response.json()
        setDetails(data)
      }
    } catch (error) {
      console.error('Error loading representant details:', error)
    } finally {
      setIsLoadingDetails(false)
    }
  }

  if (!hasExistingRepresentant) {
    return null
  }

  return (
    <div className="mt-3 border-l-4 border-orange-500 bg-orange-50 rounded-lg">
      <div className="p-4">
        {/* Badge Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-2">
            <ExclamationTriangleIcon className="h-5 w-5 text-orange-600 flex-shrink-0" />
            <div>
              <h4 className="text-sm font-semibold text-orange-900">
                Représentant Légal Déjà Existant
              </h4>
              <p className="text-xs text-orange-700 mt-1">
                {validation.representant_legal_nom} ({validation.representant_legal_email})
              </p>
            </div>
          </div>

          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-orange-700 hover:text-orange-900 transition-colors"
          >
            {isExpanded ? (
              <ChevronUpIcon className="h-5 w-5" />
            ) : (
              <ChevronDownIcon className="h-5 w-5" />
            )}
          </button>
        </div>

        {/* Quick Info */}
        <div className="mt-3 flex items-center space-x-4 text-xs text-orange-700">
          <div className="flex items-center space-x-1">
            <BuildingOfficeIcon className="h-4 w-4" />
            <span>{validation.existing_representant_entreprises?.length || 0} entreprise(s) liée(s)</span>
          </div>
          <div className="flex items-center space-x-1">
            <UserIcon className="h-4 w-4" />
            <span>Contact client requis</span>
          </div>
        </div>

        {/* Expanded Details */}
        {isExpanded && (
          <div className="mt-4 pt-4 border-t border-orange-200">
            {isLoadingDetails ? (
              <div className="text-center py-2">
                <div className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-orange-600 border-t-transparent"></div>
                <span className="ml-2 text-xs text-orange-700">Chargement...</span>
              </div>
            ) : details && details.found ? (
              <div className="space-y-3">
                {/* User Info */}
                <div className="bg-white rounded-lg p-3">
                  <h5 className="text-xs font-semibold text-gray-900 mb-2">Informations du contact</h5>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <span className="text-gray-600">Nom:</span>
                      <span className="ml-1 font-medium text-gray-900">{details.user?.full_name}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Email:</span>
                      <span className="ml-1 font-medium text-gray-900">{details.user?.email}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Username:</span>
                      <span className="ml-1 font-medium text-gray-900">{details.user?.username}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Statut:</span>
                      <span className={`ml-1 font-medium ${details.user?.status === 'active' ? 'text-green-600' : 'text-gray-600'}`}>
                        {details.user?.status}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Entreprises List */}
                {details.entreprises && details.entreprises.length > 0 && (
                  <div className="bg-white rounded-lg p-3">
                    <h5 className="text-xs font-semibold text-gray-900 mb-2">
                      Entreprises associées ({details.total_entreprises})
                    </h5>
                    <div className="space-y-2">
                      {details.entreprises.map((entreprise) => (
                        <div
                          key={entreprise.id}
                          className="flex items-center justify-between p-2 bg-gray-50 rounded border border-gray-200"
                        >
                          <div>
                            <div className="flex items-center space-x-2">
                              <BuildingOfficeIcon className="h-4 w-4 text-gray-500" />
                              <span className="text-xs font-medium text-gray-900">{entreprise.nom}</span>
                            </div>
                            {entreprise.email && (
                              <p className="text-xs text-gray-600 mt-1 ml-6">{entreprise.email}</p>
                            )}
                          </div>
                          <span className={`text-xs px-2 py-1 rounded-full ${
                            entreprise.status === 'active' 
                              ? 'bg-green-100 text-green-700' 
                              : 'bg-gray-100 text-gray-700'
                          }`}>
                            {entreprise.status}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="bg-orange-100 rounded-lg p-3">
                  <p className="text-xs font-semibold text-orange-900 mb-3">
                    🔔 Action requise du validateur
                  </p>
                  <div className="flex flex-col space-y-2">
                    <button
                      onClick={onAttachClick}
                      className="w-full px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white text-sm font-medium rounded-lg transition-colors"
                    >
                      Rattacher à ce client existant
                    </button>
                    <button
                      onClick={onRejectClick}
                      className="w-full px-4 py-2 bg-white hover:bg-gray-50 text-orange-600 text-sm font-medium rounded-lg border border-orange-300 transition-colors"
                    >
                      Créer nouvelle entreprise indépendante
                    </button>
                  </div>
                  <p className="text-xs text-orange-700 mt-3 italic">
                    ⚠️ Recommandation : Contacter le client avant de rattacher
                  </p>
                </div>
              </div>
            ) : (
              <p className="text-xs text-orange-700">Détails non disponibles</p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
