/**
 * MissionDetailModal - Modal réutilisable pour afficher les détails d'une mission
 * Permet la candidature rapide avec sélection de CV
 * 
 * Features:
 * - Affichage complet des détails de mission
 * - Candidature rapide avec sélection de CV depuis les documents
 * - Gestion d'erreurs robuste
 * - Notifications toast
 * - Validation des permissions IAM
 */
import { useState } from 'react'
import Modal from '@/components/Modal'
import Button from '@/components/Button'
import InlineDocumentUpload from '@/components/InlineDocumentUpload'
import { useAppSelector } from '@/store/hooks'
import { useGetMyProfileQuery } from '@/features/profile/api/profileApi'
import { useApplyToMissionMutation, type Mission } from '../api/missionApi'
import { useGetActiveContractQuery } from '@/features/contracts/api/contractApi'
import {
  BriefcaseIcon,
  MapPinIcon,
  CalendarIcon,
  ClockIcon,
  CurrencyDollarIcon,
  AcademicCapIcon,
  CheckCircleIcon,
  XCircleIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

interface MissionDetailModalProps {
  mission: Mission | null
  isOpen: boolean
  onClose: () => void
  hasAlreadyApplied?: boolean
}

export default function MissionDetailModal({
  mission,
  isOpen,
  onClose,
  hasAlreadyApplied = false,
}: MissionDetailModalProps) {
  const currentUser = useAppSelector((state) => state.auth.user)
  const { data: profileData } = useGetMyProfileQuery()
  const [applyToMission, { isLoading: isApplying }] = useApplyToMissionMutation()
  
  const [selectedCvId, setSelectedCvId] = useState<string>('')
  const [showQuickApply, setShowQuickApply] = useState(false)

  if (!mission) return null

  // Récupérer les documents de type CV de l'utilisateur
  const profile = profileData?.profile
  const userDocuments = profile?.documents || []
  const cvDocuments = userDocuments.filter((doc: any) => 
    doc.type === 'cv' || 
    doc.type === 'CV' || 
    doc.document_type === 'cv' ||
    doc.filename?.toLowerCase().includes('cv') ||
    doc.filename?.toLowerCase().includes('resume')
  )

  // Vérifier si l'utilisateur a un CV par défaut
  const defaultCvId = profile?.cv_document_id

  const handleQuickApply = async () => {
    if (!currentUser) {
      toast.error('Vous devez être connecté pour postuler')
      return
    }

    // Validation : au moins un CV doit être sélectionné ou disponible
    if (!selectedCvId && !defaultCvId) {
      toast.error('Veuillez sélectionner un CV ou uploader un CV dans votre profil')
      return
    }

    try {
      const cvId = selectedCvId || defaultCvId

      await applyToMission({
        mission_id: mission.id,
        user_id: currentUser.id,
        additional_info: `Candidature rapide avec CV: ${cvId}`,
      }).unwrap()

      toast.success('🎉 Candidature envoyée avec succès !', {
        duration: 4000,
      })
      
      // Fermer la modale après succès
      setTimeout(() => {
        onClose()
        setShowQuickApply(false)
        setSelectedCvId('')
      }, 1500)
    } catch (error: any) {
      console.error('❌ Erreur lors de la candidature:', error)
      
      // Gestion d'erreurs robuste et originale
      const errorMessage = error?.data?.detail || error?.message || 'Une erreur est survenue'
      
      if (error?.status === 403) {
        toast.error('⛔ Accès refusé : Vous n\'avez pas les permissions nécessaires', {
          duration: 5000,
        })
      } else if (error?.status === 409) {
        toast.error('⚠️ Vous avez déjà postulé à cette mission', {
          duration: 4000,
        })
      } else if (error?.status === 400) {
        toast.error(`📋 ${errorMessage}`, {
          duration: 5000,
        })
      } else if (error?.status >= 500) {
        toast.error('🔧 Erreur serveur. Veuillez réessayer plus tard', {
          duration: 5000,
        })
      } else {
        toast.error(`❌ ${errorMessage}`, {
          duration: 4000,
        })
      }
    }
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Non spécifié'
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    })
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} maxWidth="2xl" title={mission.title}>
      <div className="space-y-6">
        {/* Status Badge */}
        <div className="flex items-center gap-3">
          <span
            className={`px-3 py-1 text-sm font-medium rounded-full ${
              mission.status === 'published' || mission.status === 'accepting_applications'
                ? 'bg-green-100 text-green-800'
                : mission.status === 'draft'
                ? 'bg-gray-100 text-gray-800'
                : 'bg-yellow-100 text-yellow-800'
            }`}
          >
            {mission.status}
          </span>
          {hasAlreadyApplied && (
            <span className="px-3 py-1 text-sm font-medium rounded-full bg-blue-100 text-blue-800 flex items-center gap-1">
              <CheckCircleIcon className="h-4 w-4" />
              Déjà postulé
            </span>
          )}
        </div>

        {/* Description */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Description</h3>
          <p className="text-gray-600 whitespace-pre-line">{mission.description}</p>
        </div>

        {/* Informations principales */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
            <MapPinIcon className="h-5 w-5 text-gray-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-gray-900">Localisation</p>
              <p className="text-sm text-gray-600">{mission.location}</p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
            <BriefcaseIcon className="h-5 w-5 text-gray-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-gray-900">Type de poste</p>
              <p className="text-sm text-gray-600">{mission.job_type}</p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
            <CalendarIcon className="h-5 w-5 text-gray-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-gray-900">Dates</p>
              <p className="text-sm text-gray-600">
                {formatDate(mission.start_date)} - {formatDate(mission.end_date)}
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
            <ClockIcon className="h-5 w-5 text-gray-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-gray-900">Durée</p>
              <p className="text-sm text-gray-600">{mission.duration || 'Non spécifié'}</p>
            </div>
          </div>

          {mission.salary_range && (
            <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
              <CurrencyDollarIcon className="h-5 w-5 text-gray-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-gray-900">Rémunération</p>
                <p className="text-sm text-gray-600">{mission.salary_range}</p>
              </div>
            </div>
          )}

          {mission.education_level && (
            <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
              <AcademicCapIcon className="h-5 w-5 text-gray-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-gray-900">Niveau d'études</p>
                <p className="text-sm text-gray-600">{mission.education_level}</p>
              </div>
            </div>
          )}
        </div>

        {/* Compétences requises */}
        {mission.required_skills.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Compétences requises</h3>
            <div className="flex flex-wrap gap-2">
              {mission.required_skills.map((skill, index) => (
                <span
                  key={index}
                  className="px-3 py-1 text-sm bg-jlc-purple-100 text-jlc-purple-700 rounded-full"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Type de contrat et horaires */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-2">Type de contrat</h4>
            <p className="text-sm text-gray-600">{mission.contract_type}</p>
          </div>
          {mission.working_hours && (
            <div>
              <h4 className="text-sm font-semibold text-gray-900 mb-2">Horaires de travail</h4>
              <p className="text-sm text-gray-600">{mission.working_hours}</p>
            </div>
          )}
        </div>

        {/* Avantages */}
        {mission.benefits && mission.benefits.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Avantages</h3>
            <ul className="space-y-2">
              {mission.benefits.map((benefit, index) => (
                <li key={index} className="flex items-start gap-2 text-sm text-gray-600">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                  {benefit}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Section candidature rapide */}
        {!hasAlreadyApplied && (
          <div className="border-t pt-6">
            {!showQuickApply ? (
              <Button
                variant="primary"
                onClick={() => setShowQuickApply(true)}
                className="w-full"
              >
                <BriefcaseIcon className="h-5 w-5 mr-2" />
                Postuler rapidement
              </Button>
            ) : (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900">Candidature rapide</h3>
                
                {/* Alerte si pas de CV */}
                {cvDocuments.length === 0 && !defaultCvId && (
                  <div className="flex items-start gap-3 p-4 bg-orange-50 border border-orange-200 rounded-lg">
                    <ExclamationTriangleIcon className="h-5 w-5 text-orange-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-orange-900">Aucun CV trouvé</p>
                      <p className="text-sm text-orange-700 mt-1">
                        Veuillez uploader un CV dans votre profil avant de postuler.
                      </p>
                    </div>
                  </div>
                )}

                {/* Sélection du CV */}
                {(cvDocuments.length > 0 || defaultCvId) && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Sélectionnez votre CV
                    </label>
                    <select
                      value={selectedCvId}
                      onChange={(e) => setSelectedCvId(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
                    >
                      {defaultCvId && (
                        <option value={defaultCvId}>CV par défaut (recommandé)</option>
                      )}
                      {cvDocuments.map((doc: any) => (
                        <option key={doc.id} value={doc.id}>
                          {doc.filename || doc.original_filename || `CV ${doc.id.slice(0, 8)}`}
                        </option>
                      ))}
                    </select>
                    <p className="text-xs text-gray-500 mt-2">
                      💡 Votre CV sera automatiquement joint à votre candidature
                    </p>
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-3">
                  <Button
                    variant="secondary"
                    onClick={() => {
                      setShowQuickApply(false)
                      setSelectedCvId('')
                    }}
                    disabled={isApplying}
                    className="flex-1"
                  >
                    Annuler
                  </Button>
                  <Button
                    variant="primary"
                    onClick={handleQuickApply}
                    disabled={isApplying || (cvDocuments.length === 0 && !defaultCvId)}
                    isLoading={isApplying}
                    className="flex-1"
                  >
                    {isApplying ? 'Envoi...' : 'Confirmer la candidature'}
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Message si déjà postulé */}
        {hasAlreadyApplied && (
          <div className="flex items-start gap-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <CheckCircleIcon className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-blue-900">Candidature déjà envoyée</p>
              <p className="text-sm text-blue-700 mt-1">
                Vous pouvez suivre l'évolution de votre candidature dans "Mes Candidatures".
              </p>
            </div>
          </div>
        )}
      </div>
    </Modal>
  )
}
