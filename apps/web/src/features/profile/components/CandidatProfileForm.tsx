/**
 * Candidat/Postulant Profile Form
 * Form for editing candidate/applicant profile information
 */
import { useState } from 'react'
import { useUpdateMyProfileMutation } from '../api/profileApi'
import toast from 'react-hot-toast'

interface CandidatProfile {
  first_name?: string
  last_name?: string
  date_of_birth?: string
  place_of_birth?: string
  phone?: string
  address?: string
  city?: string
  postal_code?: string
  country?: string
  nationality?: string
  gender?: string
  skills?: string[]
  years_of_experience?: number
  education_level?: string
  cv_document_id?: string
  photo_url?: string
  availability?: string
  desired_position?: string
  desired_salary?: string
  linkedin_url?: string
  bio?: string
  [key: string]: any
}

interface Props {
  profile: CandidatProfile
}

export default function CandidatProfileForm({ profile }: Props) {
  const [updateProfile, { isLoading }] = useUpdateMyProfileMutation()
  const [formData, setFormData] = useState<CandidatProfile>(profile || {})

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await updateProfile(formData).unwrap()
      toast.success('Profil mis à jour avec succès')
      // The query will be automatically refetched by RTK Query
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la mise à jour')
    }
  }

  const handleSkillsChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const skillsArray = e.target.value.split(',').map(s => s.trim()).filter(Boolean)
    setFormData({ ...formData, skills: skillsArray })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      {/* Alert */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          ℹ️ Complétez votre profil pour améliorer vos chances de trouver des opportunités
        </p>
      </div>

      {/* Informations personnelles */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">
          Informations Personnelles
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Prénom <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.first_name || ''}
              onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              placeholder="Votre prénom"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nom <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.last_name || ''}
              onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              placeholder="Votre nom"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Date de naissance <span className="text-red-500">*</span>
            </label>
            <input
              type="date"
              value={formData.date_of_birth || ''}
              onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Lieu de naissance
            </label>
            <input
              type="text"
              value={formData.place_of_birth || ''}
              onChange={(e) => setFormData({ ...formData, place_of_birth: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              placeholder="Ville, Pays"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Téléphone <span className="text-red-500">*</span>
            </label>
            <input
              type="tel"
              value={formData.phone || ''}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              placeholder="+241 XX XX XX XX"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Genre
            </label>
            <select
              value={formData.gender || ''}
              onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
            >
              <option value="">Sélectionner</option>
              <option value="male">Homme</option>
              <option value="female">Femme</option>
              <option value="other">Autre</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nationalité
            </label>
            <input
              type="text"
              value={formData.nationality || ''}
              onChange={(e) => setFormData({ ...formData, nationality: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              placeholder="Ex: Gabonaise"
            />
          </div>
        </div>
      </div>

      {/* Adresse */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">
          Adresse
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Adresse complète <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.address || ''}
              onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              placeholder="Rue, Numéro, Quartier"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Ville <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.city || ''}
              onChange={(e) => setFormData({ ...formData, city: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              placeholder="Ex: Libreville"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Code postal
            </label>
            <input
              type="text"
              value={formData.postal_code || ''}
              onChange={(e) => setFormData({ ...formData, postal_code: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              placeholder="Ex: BP 1234"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Pays <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.country || 'GA'}
              onChange={(e) => setFormData({ ...formData, country: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              required
            >
              <option value="GA">Gabon</option>
              <option value="FR">France</option>
              <option value="CM">Cameroun</option>
              <option value="CI">Côte d'Ivoire</option>
              <option value="SN">Sénégal</option>
            </select>
          </div>
        </div>
      </div>

      {/* Expérience & Formation */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">
          Expérience & Formation
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Années d'expérience
            </label>
            <input
              type="number"
              min="0"
              max="50"
              value={formData.years_of_experience || ''}
              onChange={(e) => setFormData({ ...formData, years_of_experience: parseInt(e.target.value) || 0 })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              placeholder="Ex: 5"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Niveau d'éducation
            </label>
            <select
              value={formData.education_level || ''}
              onChange={(e) => setFormData({ ...formData, education_level: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
            >
              <option value="">Sélectionner</option>
              <option value="no_diploma">Sans diplôme</option>
              <option value="cap_bep">CAP/BEP</option>
              <option value="bac">Baccalauréat</option>
              <option value="bac_2">Bac+2 (BTS/DUT)</option>
              <option value="bac_3">Bac+3 (Licence)</option>
              <option value="bac_5">Bac+5 (Master)</option>
              <option value="bac_8">Bac+8 (Doctorat)</option>
            </select>
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Compétences (séparées par des virgules)
            </label>
            <textarea
              value={formData.skills?.join(', ') || ''}
              onChange={handleSkillsChange}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              placeholder="Ex: Gestion de projet, Communication, Microsoft Office, Anglais"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Poste recherché
            </label>
            <input
              type="text"
              value={formData.desired_position || ''}
              onChange={(e) => setFormData({ ...formData, desired_position: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              placeholder="Ex: Assistant RH"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Disponibilité
            </label>
            <select
              value={formData.availability || ''}
              onChange={(e) => setFormData({ ...formData, availability: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
            >
              <option value="">Sélectionner</option>
              <option value="immediate">Immédiate</option>
              <option value="1_week">1 semaine</option>
              <option value="2_weeks">2 semaines</option>
              <option value="1_month">1 mois</option>
              <option value="negotiable">Négociable</option>
            </select>
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              LinkedIn (optionnel)
            </label>
            <input
              type="url"
              value={formData.linkedin_url || ''}
              onChange={(e) => setFormData({ ...formData, linkedin_url: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              placeholder="https://linkedin.com/in/votre-profil"
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Présentation (Bio)
            </label>
            <textarea
              value={formData.bio || ''}
              onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              placeholder="Décrivez brièvement votre parcours, vos motivations et vos objectifs professionnels..."
            />
          </div>
        </div>
      </div>

      {/* Submit Button */}
      <div className="flex justify-end gap-4 pt-6 border-t">
        <button
          type="submit"
          disabled={isLoading}
          className="px-6 py-3 bg-jlc-purple-600 text-white font-medium rounded-lg hover:bg-jlc-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Enregistrement...' : 'Enregistrer les modifications'}
        </button>
      </div>
    </form>
  )
}
