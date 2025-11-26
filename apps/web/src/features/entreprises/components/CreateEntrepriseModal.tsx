import { useState } from 'react'
import { useCreateEntrepriseMutation } from '../api/entreprisesApi'
import { useCreateBulkInvitationsMutation } from '@/features/company/api/invitationApi'
import { XMarkIcon, PlusIcon, TrashIcon, EnvelopeIcon } from '@heroicons/react/24/outline'
import Button from '@/components/Button'
import { usePermissions } from '@/hooks/usePermission'

interface CreateEntrepriseModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess?: () => void
}

export default function CreateEntrepriseModal({ isOpen, onClose, onSuccess }: CreateEntrepriseModalProps) {
  const [createEntreprise, { isLoading: isCreating }] = useCreateEntrepriseMutation()
  const [createInvitations, { isLoading: isInviting }] = useCreateBulkInvitationsMutation()
  const { permissions } = usePermissions(['entreprises.create.all', 'entreprises.create.own'])

  const [formData, setFormData] = useState({
    nom: '',
    raison_sociale: '',
    siret: '',
    adresse: '',
    code_postal: '',
    ville: '',
    pays: 'France',
    email: '',
    telephone: '',
    description: '',
    secteur_activite: '',
    effectif: '',
    site_web: '',
  })

  const [invitations, setInvitations] = useState<string[]>([''])
  const [inviteUsers, setInviteUsers] = useState(false)
  const [invitationMessage, setInvitationMessage] = useState('')
  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev }
        delete newErrors[name]
        return newErrors
      })
    }
  }

  const handleInvitationChange = (index: number, value: string) => {
    const newInvitations = [...invitations]
    newInvitations[index] = value
    setInvitations(newInvitations)
  }

  const addInvitationField = () => {
    setInvitations([...invitations, ''])
  }

  const removeInvitationField = (index: number) => {
    if (invitations.length > 1) {
      setInvitations(invitations.filter((_, i) => i !== index))
    }
  }

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.nom) newErrors.nom = 'Le nom est requis'
    if (!formData.raison_sociale) newErrors.raison_sociale = 'La raison sociale est requise'
    if (!formData.siret) newErrors.siret = 'Le SIRET est requis'
    else if (!/^\d{14}$/.test(formData.siret)) newErrors.siret = 'Le SIRET doit contenir 14 chiffres'
    if (!formData.adresse) newErrors.adresse = "L'adresse est requise"
    if (!formData.email) newErrors.email = "L'email est requis"
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) newErrors.email = 'Email invalide'
    if (!formData.telephone) newErrors.telephone = 'Le téléphone est requis'

    // Validation des invitations si activée
    if (inviteUsers) {
      const validEmails = invitations.filter(email => email.trim() !== '')
      const invalidEmails = validEmails.filter(email => !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
      
      if (invalidEmails.length > 0) {
        newErrors.invitations = 'Certains emails sont invalides'
      }
      
      if (validEmails.length === 0) {
        newErrors.invitations = 'Ajoutez au moins un email pour les invitations'
      }
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    try {
      // 1. Créer l'entreprise
      const result = await createEntreprise(formData).unwrap()
      
      // 2. Si invitation activée, envoyer les invitations
      if (inviteUsers) {
        const validEmails = invitations.filter(email => email.trim() !== '' && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
        
        if (validEmails.length > 0) {
          await createInvitations({
            emails: validEmails,
            entreprise_id: result.id,
            profile_code: 'company_manager',
            message: invitationMessage || undefined,
          }).unwrap()
        }
      }

      // Succès
      onSuccess?.()
      onClose()
      
      // Reset form
      setFormData({
        nom: '',
        raison_sociale: '',
        siret: '',
        adresse: '',
        code_postal: '',
        ville: '',
        pays: 'France',
        email: '',
        telephone: '',
        description: '',
        secteur_activite: '',
        effectif: '',
        site_web: '',
      })
      setInvitations([''])
      setInviteUsers(false)
      setInvitationMessage('')
    } catch (error: any) {
      console.error('Failed to create entreprise:', error)
      setErrors({ submit: error?.data?.detail || 'Erreur lors de la création' })
    }
  }

  if (!isOpen) return null

  const canCreate = permissions['entreprises.create.all'] || permissions['entreprises.create.own']
  if (!canCreate) {
    return null
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">Créer une entreprise</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            disabled={isCreating || isInviting}
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Error général */}
          {errors.submit && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {errors.submit}
            </div>
          )}

          {/* Informations générales */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Informations générales</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nom commercial <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="nom"
                  value={formData.nom}
                  onChange={handleChange}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-jlc-purple-500 ${
                    errors.nom ? 'border-red-500' : 'border-gray-300'
                  }`}
                  disabled={isCreating || isInviting}
                />
                {errors.nom && <p className="text-sm text-red-500 mt-1">{errors.nom}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Raison sociale <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="raison_sociale"
                  value={formData.raison_sociale}
                  onChange={handleChange}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-jlc-purple-500 ${
                    errors.raison_sociale ? 'border-red-500' : 'border-gray-300'
                  }`}
                  disabled={isCreating || isInviting}
                />
                {errors.raison_sociale && <p className="text-sm text-red-500 mt-1">{errors.raison_sociale}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  SIRET <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="siret"
                  value={formData.siret}
                  onChange={handleChange}
                  maxLength={14}
                  placeholder="14 chiffres"
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-jlc-purple-500 ${
                    errors.siret ? 'border-red-500' : 'border-gray-300'
                  }`}
                  disabled={isCreating || isInviting}
                />
                {errors.siret && <p className="text-sm text-red-500 mt-1">{errors.siret}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email <span className="text-red-500">*</span>
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-jlc-purple-500 ${
                    errors.email ? 'border-red-500' : 'border-gray-300'
                  }`}
                  disabled={isCreating || isInviting}
                />
                {errors.email && <p className="text-sm text-red-500 mt-1">{errors.email}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Téléphone <span className="text-red-500">*</span>
                </label>
                <input
                  type="tel"
                  name="telephone"
                  value={formData.telephone}
                  onChange={handleChange}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-jlc-purple-500 ${
                    errors.telephone ? 'border-red-500' : 'border-gray-300'
                  }`}
                  disabled={isCreating || isInviting}
                />
                {errors.telephone && <p className="text-sm text-red-500 mt-1">{errors.telephone}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Site web</label>
                <input
                  type="url"
                  name="site_web"
                  value={formData.site_web}
                  onChange={handleChange}
                  placeholder="https://..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                  disabled={isCreating || isInviting}
                />
              </div>
            </div>
          </div>

          {/* Adresse */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Adresse</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Adresse <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="adresse"
                  value={formData.adresse}
                  onChange={handleChange}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-jlc-purple-500 ${
                    errors.adresse ? 'border-red-500' : 'border-gray-300'
                  }`}
                  disabled={isCreating || isInviting}
                />
                {errors.adresse && <p className="text-sm text-red-500 mt-1">{errors.adresse}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Code postal</label>
                <input
                  type="text"
                  name="code_postal"
                  value={formData.code_postal}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                  disabled={isCreating || isInviting}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Ville</label>
                <input
                  type="text"
                  name="ville"
                  value={formData.ville}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                  disabled={isCreating || isInviting}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Pays</label>
                <input
                  type="text"
                  name="pays"
                  value={formData.pays}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                  disabled={isCreating || isInviting}
                />
              </div>
            </div>
          </div>

          {/* Autres informations */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Autres informations</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Secteur d'activité</label>
                <input
                  type="text"
                  name="secteur_activite"
                  value={formData.secteur_activite}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                  disabled={isCreating || isInviting}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Effectif</label>
                <select
                  name="effectif"
                  value={formData.effectif}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                  disabled={isCreating || isInviting}
                >
                  <option value="">Sélectionner</option>
                  <option value="TPE">TPE (1-19 salariés)</option>
                  <option value="PME">PME (20-249 salariés)</option>
                  <option value="ETI">ETI (250-4999 salariés)</option>
                  <option value="GE">GE (5000+ salariés)</option>
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                  disabled={isCreating || isInviting}
                />
              </div>
            </div>
          </div>

          {/* Section Invitations */}
          <div className="border-t border-gray-200 pt-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Inviter des utilisateurs</h3>
                <p className="text-sm text-gray-600 mt-1">
                  Invitez des personnes à rejoindre cette entreprise (optionnel)
                </p>
              </div>
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={inviteUsers}
                  onChange={(e) => setInviteUsers(e.target.checked)}
                  className="w-4 h-4 text-jlc-purple-600 border-gray-300 rounded focus:ring-jlc-purple-500"
                  disabled={isCreating || isInviting}
                />
                <span className="ml-2 text-sm text-gray-700">Activer les invitations</span>
              </label>
            </div>

            {inviteUsers && (
              <div className="space-y-4">
                {invitations.map((email, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <EnvelopeIcon className="h-5 w-5 text-gray-400 flex-shrink-0" />
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => handleInvitationChange(index, e.target.value)}
                      placeholder="email@example.com"
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                      disabled={isCreating || isInviting}
                    />
                    {invitations.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeInvitationField(index)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        disabled={isCreating || isInviting}
                      >
                        <TrashIcon className="h-5 w-5" />
                      </button>
                    )}
                  </div>
                ))}

                <button
                  type="button"
                  onClick={addInvitationField}
                  className="flex items-center gap-2 text-sm text-jlc-purple-600 hover:text-jlc-purple-700 font-medium"
                  disabled={isCreating || isInviting}
                >
                  <PlusIcon className="h-4 w-4" />
                  Ajouter un email
                </button>

                {errors.invitations && (
                  <p className="text-sm text-red-500">{errors.invitations}</p>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Message personnalisé (optionnel)
                  </label>
                  <textarea
                    value={invitationMessage}
                    onChange={(e) => setInvitationMessage(e.target.value)}
                    rows={2}
                    placeholder="Message à inclure dans l'email d'invitation..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                    disabled={isCreating || isInviting}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <Button
              type="button"
              onClick={onClose}
              variant="secondary"
              disabled={isCreating || isInviting}
            >
              Annuler
            </Button>
            <Button
              type="submit"
              variant="primary"
              disabled={isCreating || isInviting}
            >
              {isCreating || isInviting ? 'Création en cours...' : 'Créer l\'entreprise'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
