import { useState } from 'react'
import { useUpdateMyProfileMutation } from '../api/profileApi'
import type { InterimProfile } from '../api/profileApi'
import toast from 'react-hot-toast'

interface Props {
  profile: InterimProfile
}

export default function InterimProfileForm({ profile }: Props) {
  const [updateProfile, { isLoading }] = useUpdateMyProfileMutation()
  const [formData, setFormData] = useState(profile)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await updateProfile(formData).unwrap()
      toast.success('Profil mis à jour avec succès')
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la mise à jour')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <p className="text-sm text-blue-800">
          ℹ️ Complétez votre profil pour améliorer vos chances de trouver des missions
        </p>
      </div>

      {/* Informations de base */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Informations de Base</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Prénom <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.first_name || ''}
              onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
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
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
              placeholder="Votre nom"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Date de naissance
            </label>
            <input
              type="date"
              value={formData.date_of_birth || ''}
              onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
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
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
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
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
              placeholder="+241 XX XX XX XX"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email <span className="text-red-500">*</span>
            </label>
            <input
              type="email"
              value={formData.email || ''}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
              placeholder="votre.email@exemple.com"
              required
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Adresse complète
            </label>
            <input
              type="text"
              value={formData.address || ''}
              onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
              placeholder="Adresse, ville, quartier"
            />
          </div>
        </div>
      </div>

      {/* Informations personnelles */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Informations Personnelles</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nationalité
            </label>
            <input
              type="text"
              value={formData.nationality || ''}
              onChange={(e) => setFormData({ ...formData, nationality: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
              placeholder="Ex: Gabonaise"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Niveau d'études
            </label>
            <select
              value={formData.education_level || ''}
              onChange={(e) => setFormData({ ...formData, education_level: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
            >
              <option value="">Sélectionner</option>
              <option value="none">Aucun diplôme</option>
              <option value="primary">Primaire</option>
              <option value="secondary">Secondaire</option>
              <option value="bac">Baccalauréat</option>
              <option value="license">Licence</option>
              <option value="master">Master</option>
              <option value="doctorat">Doctorat</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Années d'expérience
            </label>
            <input
              type="number"
              min="0"
              value={formData.years_of_experience || 0}
              onChange={(e) => setFormData({ ...formData, years_of_experience: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
            />
          </div>

          <div>
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={formData.has_driving_license}
                onChange={(e) => setFormData({ ...formData, has_driving_license: e.target.checked })}
                className="rounded border-gray-300 text-jlc-purple-600 focus:ring-jlc-purple-500"
              />
              <span className="text-sm font-medium text-gray-700">J'ai un permis de conduire</span>
            </label>
          </div>
        </div>
      </div>

      {/* Disponibilités */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Disponibilités</h3>
        <div className="space-y-4">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={formData.available_immediately}
              onChange={(e) => setFormData({ ...formData, available_immediately: e.target.checked })}
              className="rounded border-gray-300 text-jlc-purple-600 focus:ring-jlc-purple-500"
            />
            <span className="text-sm font-medium text-gray-700">Disponible immédiatement</span>
          </label>

          {!formData.available_immediately && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Disponible à partir du
              </label>
              <input
                type="date"
                value={formData.available_from_date || ''}
                onChange={(e) => setFormData({ ...formData, available_from_date: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
              />
            </div>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-end space-x-4 pt-6 border-t">
        <button
          type="submit"
          disabled={isLoading}
          className="px-6 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 disabled:opacity-50 transition"
        >
          {isLoading ? 'Enregistrement...' : 'Enregistrer'}
        </button>
      </div>
    </form>
  )
}
