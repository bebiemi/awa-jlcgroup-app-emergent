import { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import Layout from '@/components/Layout'
import {
  useGetMissionQuery,
  useApplyToMissionMutation,
  type ApplicationCreate,
} from '../api/missionApi'
import { useAppSelector } from '@/store/hooks'
import { ArrowLeftIcon, PlusIcon, XMarkIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

export default function ApplyMissionPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAppSelector((state) => state.auth)
  
  const { data: mission, isLoading: missionLoading } = useGetMissionQuery(id!)
  const [applyToMission, { isLoading: applying }] = useApplyToMissionMutation()

  const [formData, setFormData] = useState<Partial<ApplicationCreate>>({
    mission_id: id!,
    user_id: user?.id || '',
    cover_letter: '',
    matching_skills: [],
    additional_info: '',
  })

  const [skillInput, setSkillInput] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.cover_letter?.trim()) {
      toast.error('Veuillez rédiger une lettre de motivation')
      return
    }

    try {
      await applyToMission(formData as ApplicationCreate).unwrap()
      toast.success('Candidature envoyée avec succès !')
      navigate('/offres')
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la candidature')
    }
  }

  const addSkill = () => {
    if (skillInput.trim() && !formData.matching_skills?.includes(skillInput.trim())) {
      setFormData({
        ...formData,
        matching_skills: [...(formData.matching_skills || []), skillInput.trim()],
      })
      setSkillInput('')
    }
  }

  const removeSkill = (skill: string) => {
    setFormData({
      ...formData,
      matching_skills: formData.matching_skills?.filter(s => s !== skill) || [],
    })
  }

  if (missionLoading) {
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
          <Link to="/offres" className="text-jlc-purple-600 hover:text-jlc-purple-700 mt-4 inline-block">
            Retour aux offres
          </Link>
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
            onClick={() => navigate(-1)}
            className="flex items-center text-gray-600 hover:text-gray-900"
          >
            <ArrowLeftIcon className="h-5 w-5 mr-2" />
            Retour
          </button>
        </div>

        {/* Mission Summary */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">{mission.title}</h2>
          <div className="flex flex-wrap gap-4 text-sm text-gray-600">
            <div>📍 {mission.location}</div>
            <div>💼 {mission.contract_type}</div>
            {mission.salary_range && <div>💰 {mission.salary_range}</div>}
          </div>
          <p className="text-gray-600 mt-4 line-clamp-3">{mission.description}</p>
        </div>

        {/* Application Form */}
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-8 space-y-6">
          <h2 className="text-xl font-bold text-gray-900">Postuler à cette mission</h2>

          {/* Cover Letter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Lettre de motivation *
            </label>
            <textarea
              value={formData.cover_letter}
              onChange={(e) => setFormData({ ...formData, cover_letter: e.target.value })}
              rows={8}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
              placeholder="Expliquez pourquoi vous êtes le candidat idéal pour cette mission..."
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              Conseil: Mettez en avant vos compétences et votre expérience en lien avec la mission
            </p>
          </div>

          {/* Matching Skills */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Vos compétences correspondantes
            </label>
            <p className="text-sm text-gray-600 mb-3">
              Compétences requises : {mission.required_skills.join(', ')}
            </p>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={skillInput}
                onChange={(e) => setSkillInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                placeholder="Ajoutez vos compétences..."
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
              {formData.matching_skills?.map((skill) => {
                const isRequired = mission.required_skills.includes(skill)
                return (
                  <span
                    key={skill}
                    className={`inline-flex items-center px-3 py-1 rounded-full text-sm ${
                      isRequired
                        ? 'bg-green-100 text-green-700'
                        : 'bg-jlc-purple-100 text-jlc-purple-700'
                    }`}
                  >
                    {skill}
                    {isRequired && ' ✓'}
                    <button
                      type="button"
                      onClick={() => removeSkill(skill)}
                      className="ml-2 hover:opacity-70"
                    >
                      <XMarkIcon className="h-4 w-4" />
                    </button>
                  </span>
                )
              })}
            </div>
            {formData.matching_skills && formData.matching_skills.length > 0 && (
              <p className="text-xs text-gray-500 mt-2">
                {formData.matching_skills.filter(s => mission.required_skills.includes(s)).length} / {mission.required_skills.length} compétences requises
              </p>
            )}
          </div>

          {/* Additional Info */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Informations complémentaires
            </label>
            <textarea
              value={formData.additional_info}
              onChange={(e) => setFormData({ ...formData, additional_info: e.target.value })}
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
              placeholder="Ajoutez des informations supplémentaires (disponibilité, références, etc.)"
            />
          </div>

          {/* Info Box */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-medium text-blue-900 mb-2">📋 Prochaines étapes</h4>
            <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
              <li>Votre candidature sera analysée par l'équipe</li>
              <li>Si présélectionné, vous serez contacté pour un entretien</li>
              <li>Après sélection, une visite médicale sera programmée</li>
              <li>Le contrat sera finalisé et signé</li>
            </ol>
          </div>

          {/* Actions */}
          <div className="flex gap-4 pt-4">
            <button
              type="button"
              onClick={() => navigate(-1)}
              className="flex-1 px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={applying}
              className="flex-1 px-6 py-3 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 transition disabled:opacity-50"
            >
              {applying ? 'Envoi en cours...' : 'Envoyer ma candidature'}
            </button>
          </div>
        </form>
      </div>
    </Layout>
  )
}
