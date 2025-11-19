/**
 * Attach To Existing Modal
 * Phase 3: Workflow de rattachement
 */
import { useState } from 'react'
import Modal from '@/components/Modal'
import Button from '@/components/Button'
import {
  CheckCircleIcon,
  ExclamationTriangleIcon,
  BuildingOfficeIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline'
import type { Validation } from '../api/validationApi'
import { 
  useAttachToExistingRepresentantMutation,
  useRejectAttachmentMutation 
} from '../api/validationApi'
import toast from 'react-hot-toast'

interface RepresentantEntreprise {
  id: string
  nom: string
  email?: string
  status: string
  created_at?: string
}

interface Props {
  isOpen: boolean
  onClose: () => void
  validation: Validation | null
  representantEntreprises: RepresentantEntreprise[]
  onAttach: () => void
}

export default function AttachToExistingModal({
  isOpen,
  onClose,
  validation,
  representantEntreprises,
  onAttach,
}: Props) {
  const [contactConfirmation, setContactConfirmation] = useState(false)
  const [selectedEntrepriseId, setSelectedEntrepriseId] = useState<string>('')
  const [notes, setNotes] = useState('')
  
  const [attachToExisting, { isLoading: isAttaching }] = useAttachToExistingRepresentantMutation()
  const [rejectAttachment, { isLoading: isRejecting }] = useRejectAttachmentMutation()

  const handleSubmit = async () => {
    if (!validation) return

    if (!contactConfirmation) {
      toast.error('Veuillez confirmer la prise de contact avec le client')
      return
    }

    if (entreprises.length > 1 && !selectedEntrepriseId) {
      toast.error('Veuillez sélectionner une entreprise cible')
      return
    }

    setIsSubmitting(true)

    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/validations/${validation.id}/attach-to-existing`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          },
          body: JSON.stringify({
            contact_confirmation: contactConfirmation,
            target_entreprise_id: entreprises.length === 1 ? entreprises[0].id : selectedEntrepriseId,
            notes: notes || undefined,
          }),
        }
      )

      if (response.ok) {
        const result = await response.json()
        toast.success(result.message || 'Entreprise rattachée avec succès')
        onSuccess()
        handleClose()
      } else {
        const error = await response.json()
        toast.error(error.detail || 'Erreur lors du rattachement')
      }
    } catch (error) {
      console.error('Error attaching validation:', error)
      toast.error('Erreur lors du rattachement')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleClose = () => {
    setContactConfirmation(false)
    setSelectedEntrepriseId('')
    setNotes('')
    onClose()
  }

  if (!validation) return null

  return (
    <Modal isOpen={isOpen} onClose={handleClose}>
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-orange-100 rounded-lg">
              <BuildingOfficeIcon className="h-6 w-6 text-orange-600" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900">
                Rattacher à un client existant
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                {validation.user_full_name} • {validation.user_email}
              </p>
            </div>
          </div>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        {/* Warning Banner */}
        <div className="bg-orange-50 border-l-4 border-orange-500 rounded-lg p-4 mb-6">
          <div className="flex items-start space-x-3">
            <ExclamationTriangleIcon className="h-5 w-5 text-orange-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="text-sm font-semibold text-orange-900">
                Représentant légal existant détecté
              </h4>
              <p className="text-sm text-orange-700 mt-1">
                {validation.representant_legal_nom} ({validation.representant_legal_email})
              </p>
            </div>
          </div>
        </div>

        {/* Sélection entreprise cible si plusieurs */}
        {entreprises.length > 1 && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Sélectionner l'entreprise cible *
            </label>
            <div className="space-y-2">
              {entreprises.map((entreprise) => (
                <label
                  key={entreprise.id}
                  className={`flex items-center p-3 border-2 rounded-lg cursor-pointer transition-all ${
                    selectedEntrepriseId === entreprise.id
                      ? 'border-jlc-purple-500 bg-jlc-purple-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <input
                    type="radio"
                    name="target_entreprise"
                    value={entreprise.id}
                    checked={selectedEntrepriseId === entreprise.id}
                    onChange={(e) => setSelectedEntrepriseId(e.target.value)}
                    className="h-4 w-4 text-jlc-purple-600 focus:ring-jlc-purple-500"
                  />
                  <div className="ml-3 flex-1">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{entreprise.nom}</p>
                        {entreprise.email && (
                          <p className="text-xs text-gray-600">{entreprise.email}</p>
                        )}
                      </div>
                      <span
                        className={`text-xs px-2 py-1 rounded-full ${
                          entreprise.status === 'active'
                            ? 'bg-green-100 text-green-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {entreprise.status}
                      </span>
                    </div>
                  </div>
                </label>
              ))}
            </div>
          </div>
        )}

        {/* Entreprise unique */}
        {entreprises.length === 1 && (
          <div className="mb-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
            <p className="text-sm font-medium text-gray-700 mb-2">Entreprise cible :</p>
            <div className="flex items-center space-x-2">
              <BuildingOfficeIcon className="h-5 w-5 text-gray-500" />
              <div>
                <p className="text-sm font-medium text-gray-900">{entreprises[0].nom}</p>
                {entreprises[0].email && (
                  <p className="text-xs text-gray-600">{entreprises[0].email}</p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Checkbox confirmation de contact */}
        <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <label className="flex items-start space-x-3 cursor-pointer">
            <input
              type="checkbox"
              checked={contactConfirmation}
              onChange={(e) => setContactConfirmation(e.target.checked)}
              className="mt-1 h-5 w-5 text-orange-600 focus:ring-orange-500 border-gray-300 rounded"
            />
            <div className="flex-1">
              <p className="text-sm font-semibold text-gray-900">
                ✅ Confirmation de prise de contact
              </p>
              <p className="text-xs text-gray-700 mt-1">
                Je confirme avoir contacté le client existant et obtenu son accord pour rattacher
                cette nouvelle entreprise à son compte.
              </p>
            </div>
          </label>
        </div>

        {/* Notes optionnelles */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Notes (optionnel)
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
            placeholder="Détails de l'échange avec le client..."
          />
        </div>

        {/* Information sur le rattachement */}
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h4 className="text-sm font-semibold text-blue-900 mb-2">
            ℹ️ Conséquences du rattachement
          </h4>
          <ul className="text-xs text-blue-800 space-y-1">
            <li>• L'utilisateur pourra gérer plusieurs entreprises</li>
            <li>• Les entreprises restent séparées mais liées</li>
            <li>• Les données ne sont pas fusionnées automatiquement</li>
            <li>• Un regroupement peut être demandé ultérieurement</li>
          </ul>
        </div>

        {/* Actions */}
        <div className="flex justify-end space-x-3">
          <Button
            type="button"
            onClick={handleClose}
            variant="secondary"
            disabled={isSubmitting}
          >
            Annuler
          </Button>
          <Button
            type="button"
            onClick={handleSubmit}
            variant="primary"
            disabled={!contactConfirmation || isSubmitting || (entreprises.length > 1 && !selectedEntrepriseId)}
            className="bg-orange-600 hover:bg-orange-700"
          >
            {isSubmitting ? (
              <>
                <div className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent mr-2"></div>
                Rattachement...
              </>
            ) : (
              <>
                <CheckCircleIcon className="h-5 w-5 mr-2" />
                Valider le rattachement
              </>
            )}
          </Button>
        </div>
      </div>
    </Modal>
  )
}
