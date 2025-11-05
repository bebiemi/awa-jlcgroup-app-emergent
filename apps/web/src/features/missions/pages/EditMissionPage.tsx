import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Layout from '@/components/Layout'
import ReferenceSelect from '@/components/ReferenceSelect'
import {
  useGetMissionQuery,
  useUpdateMissionMutation,
  type MissionUpdate,
} from '../api/missionApi'
import { ArrowLeftIcon, PlusIcon, XMarkIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

export default function EditMissionPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  
  const { data: mission, isLoading: loadingMission } = useGetMissionQuery(id!)
  const [updateMission, { isLoading: updating }] = useUpdateMissionMutation()

  const [formData, setFormData] = useState<Partial<MissionUpdate>>({})
  const [skillInput, setSkillInput] = useState('')
  const [benefitInput, setBenefitInput] = useState('')

  // Load mission data when available
  useEffect(() => {
    if (mission) {
      setFormData({
        title: mission.title,
        description: mission.description,
        job_type: mission.job_type,
        required_skills: mission.required_skills,
        experience_required: mission.experience_required,
        education_level: mission.education_level,
        location: mission.location,
        contract_type: mission.contract_type,
        salary_range: mission.salary_range,
        duration: mission.duration,
        working_hours: mission.working_hours,
        benefits: mission.benefits,
        requires_medical_check: mission.requires_medical_check,
      })
    }
  }, [mission])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.title || !formData.description) {
      toast.error('Veuillez remplir tous les champs obligatoires')
      return
    }

    try {
      await updateMission({
        id: id!,
        data: formData as MissionUpdate,
      }).unwrap()
      toast.success('Mission mise à jour avec succès')
      navigate(`/missions/${id}`)
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la mise à jour')
    }
  }

  const addSkill = () => {
    if (skillInput.trim() && !formData.required_skills?.includes(skillInput.trim())) {
      setFormData({
        ...formData,
        required_skills: [...(formData.required_skills || []), skillInput.trim()],
      })
      setSkillInput('')
    }
  }

  const removeSkill = (skill: string) => {
    setFormData({
      ...formData,
      required_skills: formData.required_skills?.filter(s => s !== skill) || [],
    })
  }

  const addBenefit = () => {
    if (benefitInput.trim() && !formData.benefits?.includes(benefitInput.trim())) {
      setFormData({
        ...formData,
        benefits: [...(formData.benefits || []), benefitInput.trim()],
      })
      setBenefitInput('')
    }
  }

  const removeBenefit = (benefit: string) => {
    setFormData({
      ...formData,
      benefits: formData.benefits?.filter(b => b !== benefit) || [],
    })
  }

  if (loadingMission) {
    return (
      <Layout>
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
        </div>
      </Layout>
    )
  }

  if (!mission) {
    return (
      <Layout>
        <div className="text-center py-12">
          <p className="text-gray-600">Mission non trouvée</p>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => navigate(`/missions/${id}`)}
            className="flex items-center text-gray-600 hover:text-gray-900"
          >
            <ArrowLeftIcon className="h-5 w-5 mr-2" />
            Retour
          </button>
          <h1 className="text-2xl font-bold text-gray-900">Modifier la Mission</h1>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-8 space-y-6">
          {/* Basic Info */}
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-900">Informations de base</h2>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Titre de la mission *
              </label>
              <input
                type="text"
                value={formData.title || ''}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description *
              </label>
              <textarea
                value={formData.description || ''}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={6}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                required
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Type de poste *
                </label>
                <input
                  type="text"
                  value={formData.job_type || ''}
                  onChange={(e) => setFormData({ ...formData, job_type: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Localisation *
                </label>
                <input
                  type="text"
                  value={formData.location || ''}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                />
              </div>
            </div>
          </div>

          {/* Contract Details */}
          <div className="space-y-4 border-t pt-6">
            <h2 className="text-lg font-semibold text-gray-900">Détails du contrat</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <ReferenceSelect
                category="contract_types"
                value={formData.contract_type || ''}
                onChange={(value) => setFormData({ ...formData, contract_type: value })}
                label="Type de contrat"
              />

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Durée
                </label>
                <input
                  type="text"
                  value={formData.duration || ''}
                  onChange={(e) => setFormData({ ...formData, duration: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Salaire
                </label>
                <input
                  type="text"
                  value={formData.salary_range || ''}
                  onChange={(e) => setFormData({ ...formData, salary_range: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Horaires de travail
              </label>
              <input
                type="text"
                value={formData.working_hours || ''}
                onChange={(e) => setFormData({ ...formData, working_hours: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
              />
            </div>
          </div>

          {/* Requirements */}
          <div className="space-y-4 border-t pt-6">
            <h2 className="text-lg font-semibold text-gray-900">Exigences</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Expérience requise
                </label>
                <input
                  type="text"
                  value={formData.experience_required || ''}
                  onChange={(e) => setFormData({ ...formData, experience_required: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Niveau d'études
                </label>
                <input
                  type="text"
                  value={formData.education_level || ''}
                  onChange={(e) => setFormData({ ...formData, education_level: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                />
              </div>
            </div>

            {/* Skills */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Compétences requises
              </label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={skillInput}
                  onChange={(e) => setSkillInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                  placeholder="Ajouter une compétence..."
                />
                <button
                  type="button"
                  onClick={addSkill}
                  className="px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700"
                >
                  <PlusIcon className="h-5 w-5" />
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {formData.required_skills?.map((skill) => (
                  <span
                    key={skill}
                    className="inline-flex items-center px-3 py-1 bg-jlc-purple-100 text-jlc-purple-700 rounded-full text-sm"
                  >
                    {skill}
                    <button
                      type="button"
                      onClick={() => removeSkill(skill)}
                      className="ml-2 hover:text-jlc-purple-900"
                    >
                      <XMarkIcon className="h-4 w-4" />
                    </button>
                  </span>
                ))}
              </div>
            </div>

            {/* Benefits */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Avantages
              </label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={benefitInput}
                  onChange={(e) => setBenefitInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addBenefit())}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                  placeholder="Ajouter un avantage..."
                />
                <button
                  type="button"
                  onClick={addBenefit}
                  className="px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700"
                >
                  <PlusIcon className="h-5 w-5" />
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {formData.benefits?.map((benefit) => (
                  <span
                    key={benefit}
                    className="inline-flex items-center px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm"
                  >
                    {benefit}
                    <button
                      type="button"
                      onClick={() => removeBenefit(benefit)}
                      className="ml-2 hover:text-green-900"
                    >
                      <XMarkIcon className="h-4 w-4" />
                    </button>
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Medical Check */}
          <div className="border-t pt-6">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="requires_medical_check"
                checked={formData.requires_medical_check}
                onChange={(e) => setFormData({ ...formData, requires_medical_check: e.target.checked })}
                className="h-4 w-4 text-jlc-purple-600 focus:ring-jlc-purple-500 border-gray-300 rounded"
              />
              <label htmlFor="requires_medical_check" className="ml-2 block text-sm text-gray-900">
                Visite médicale obligatoire
              </label>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-4 pt-6">
            <button
              type="button"
              onClick={() => navigate(`/missions/${id}`)}
              className="flex-1 px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={updating}
              className="flex-1 px-6 py-3 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 transition disabled:opacity-50"
            >
              {updating ? 'Mise à jour...' : 'Enregistrer les modifications'}
            </button>
          </div>
        </form>
      </div>
    </Layout>
  )
}
