import { useState } from 'react'
import { useUpdateMyProfileMutation } from '../api/profileApi'
import type { CompanyManagerProfile } from '../api/profileApi'
import toast from 'react-hot-toast'

interface Props {
  profile: CompanyManagerProfile
}

export default function CompanyProfileForm({ profile }: Props) {
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
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Poste / Fonction
          </label>
          <input
            type="text"
            value={formData.job_title || ''}
            onChange={(e) => setFormData({ ...formData, job_title: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
            placeholder="Ex: Directeur RH"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Département
          </label>
          <input
            type="text"
            value={formData.department || ''}
            onChange={(e) => setFormData({ ...formData, department: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
            placeholder="Ex: Ressources Humaines"
          />
        </div>
      </div>

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
