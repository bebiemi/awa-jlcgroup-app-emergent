/**
 * ExperiencesSection - Gestion des expériences professionnelles
 * 
 * Features:
 * - Liste des expériences (JLC internes & externes)
 * - Formulaire de création/édition d'expérience
 * - Actions CRUD complètes
 * - Validation robuste des dates
 * - Gestion d'erreurs avec notifications
 * - Design responsive
 */
import { useState } from 'react'
import {
  useGetMyExperiencesQuery,
  useCreateExperienceMutation,
  useUpdateExperienceMutation,
  useDeleteExperienceMutation,
  type ProfessionalExperience,
  type ExperienceCreate,
} from '../api/experiencesApi'
import Button from '@/components/Button'
import Modal from '@/components/Modal'
import {
  BriefcaseIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  MapPinIcon,
  CalendarIcon,
  BuildingOfficeIcon,
  CheckCircleIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

export default function ExperiencesSection() {
  const { data: experiences = [], isLoading, refetch } = useGetMyExperiencesQuery()
  const [createExperience, { isLoading: isCreating }] = useCreateExperienceMutation()
  const [updateExperience, { isLoading: isUpdating }] = useUpdateExperienceMutation()
  const [deleteExperience, { isLoading: isDeleting }] = useDeleteExperienceMutation()

  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingExperience, setEditingExperience] = useState<ProfessionalExperience | null>(null)
  
  // Form state
  const [formData, setFormData] = useState<ExperienceCreate>({
    type: 'external',
    job_title: '',
    company_name: '',
    location: '',
    start_date: '',
    end_date: '',
    is_current: false,
    description: '',
    achievements: [],
    skills_used: [],
  })
  
  // Achievements & Skills temporary inputs
  const [achievementInput, setAchievementInput] = useState('')
  const [skillInput, setSkillInput] = useState('')

  // Reset form
  const resetForm = () => {
    setFormData({
      type: 'external',
      job_title: '',
      company_name: '',
      location: '',
      start_date: '',
      end_date: '',
      is_current: false,
      description: '',
      achievements: [],
      skills_used: [],
    })
    setAchievementInput('')
    setSkillInput('')
    setEditingExperience(null)
  }

  // Open modal for creating new experience
  const handleCreate = () => {
    resetForm()
    setIsModalOpen(true)
  }

  // Open modal for editing experience
  const handleEdit = (experience: ProfessionalExperience) => {
    setEditingExperience(experience)
    setFormData({
      type: experience.type as 'internal_jlc' | 'external',
      job_title: experience.job_title,
      company_name: experience.company_name,
      location: experience.location || '',
      start_date: experience.start_date.split('T')[0],
      end_date: experience.end_date ? experience.end_date.split('T')[0] : '',
      is_current: experience.is_current,
      description: experience.description || '',
      achievements: [...experience.achievements],
      skills_used: [...experience.skills_used],
    })
    setIsModalOpen(true)
  }

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Validation
    if (!formData.job_title.trim()) {
      toast.error('📋 Veuillez saisir un intitulé de poste')
      return
    }
    if (!formData.company_name.trim()) {
      toast.error('🏢 Veuillez saisir le nom de l\'entreprise')
      return
    }
    if (!formData.start_date) {
      toast.error('📅 Veuillez saisir une date de début')
      return
    }
    if (!formData.is_current && !formData.end_date) {
      toast.error('📅 Veuillez saisir une date de fin ou cocher "Poste actuel"')
      return
    }

    try {
      const experienceData = {
        ...formData,
        end_date: formData.is_current ? undefined : formData.end_date,
      }

      if (editingExperience) {
        // Update existing
        await updateExperience({
          id: editingExperience.id,
          data: experienceData,
        }).unwrap()
        toast.success('✅ Expérience mise à jour avec succès')
      } else {
        // Create new
        await createExperience(experienceData).unwrap()
        toast.success('🎉 Expérience ajoutée avec succès')
      }

      setIsModalOpen(false)
      resetForm()
      refetch()
    } catch (error: any) {
      console.error('Erreur lors de la sauvegarde:', error)
      
      const errorMessage = error?.data?.detail || error?.message || 'Une erreur est survenue'
      
      if (error?.status === 400) {
        toast.error(`📋 ${errorMessage}`)
      } else if (error?.status === 404) {
        toast.error('⚠️ Profil non trouvé. Veuillez compléter votre profil d\'abord.')
      } else {
        toast.error(`❌ ${errorMessage}`)
      }
    }
  }

  // Handle delete
  const handleDelete = async (experience: ProfessionalExperience) => {
    if (!confirm(`Êtes-vous sûr de vouloir supprimer l'expérience "${experience.job_title}" ?`)) {
      return
    }

    try {
      await deleteExperience(experience.id).unwrap()
      toast.success('🗑️ Expérience supprimée')
      refetch()
    } catch (error: any) {
      console.error('Erreur lors de la suppression:', error)
      toast.error('❌ Erreur lors de la suppression')
    }
  }

  // Add achievement
  const addAchievement = () => {
    if (achievementInput.trim()) {
      setFormData({
        ...formData,
        achievements: [...(formData.achievements || []), achievementInput.trim()],
      })
      setAchievementInput('')
    }
  }

  // Remove achievement
  const removeAchievement = (index: number) => {
    setFormData({
      ...formData,
      achievements: formData.achievements?.filter((_, i) => i !== index) || [],
    })
  }

  // Add skill
  const addSkill = () => {
    if (skillInput.trim()) {
      setFormData({
        ...formData,
        skills_used: [...(formData.skills_used || []), skillInput.trim()],
      })
      setSkillInput('')
    }
  }

  // Remove skill
  const removeSkill = (index: number) => {
    setFormData({
      ...formData,
      skills_used: formData.skills_used?.filter((_, i) => i !== index) || [],
    })
  }

  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('fr-FR', { year: 'numeric', month: 'long' })
  }

  // Calculate duration
  const calculateDuration = (start: string, end?: string) => {
    const startDate = new Date(start)
    const endDate = end ? new Date(end) : new Date()
    const diffInMonths = (endDate.getFullYear() - startDate.getFullYear()) * 12 + (endDate.getMonth() - startDate.getMonth())
    
    if (diffInMonths < 12) {
      return `${diffInMonths} mois`
    } else {
      const years = Math.floor(diffInMonths / 12)
      const months = diffInMonths % 12
      return months > 0 ? `${years} an${years > 1 ? 's' : ''} ${months} mois` : `${years} an${years > 1 ? 's' : ''}`
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-jlc-purple-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Expériences Professionnelles</h2>
          <p className="text-sm text-gray-600 mt-1">
            Ajoutez vos expériences passées pour valoriser votre profil
          </p>
        </div>
        <Button variant="primary" onClick={handleCreate}>
          <PlusIcon className="h-5 w-5 mr-2" />
          Ajouter
        </Button>
      </div>

      {/* Experiences List */}
      {experiences.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <BriefcaseIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-4">Aucune expérience professionnelle ajoutée</p>
          <Button variant="primary" onClick={handleCreate}>
            <PlusIcon className="h-5 w-5 mr-2" />
            Ajouter votre première expérience
          </Button>
        </div>
      ) : (
        <div className="space-y-4">
          {experiences.map((experience) => (
            <div
              key={experience.id}
              className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  {/* Header */}
                  <div className="flex items-start gap-3">
                    <BriefcaseIcon className="h-6 w-6 text-jlc-purple-600 flex-shrink-0 mt-1" />
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {experience.job_title}
                      </h3>
                      <div className="flex items-center gap-2 mt-1">
                        <BuildingOfficeIcon className="h-4 w-4 text-gray-400" />
                        <span className="text-gray-700">{experience.company_name}</span>
                        {experience.type === 'internal_jlc' && (
                          <span className="px-2 py-0.5 text-xs bg-jlc-purple-100 text-jlc-purple-700 rounded-full">
                            Mission JLC
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Date & Location */}
                  <div className="mt-3 flex flex-wrap items-center gap-4 text-sm text-gray-600">
                    <div className="flex items-center gap-1">
                      <CalendarIcon className="h-4 w-4" />
                      <span>
                        {formatDate(experience.start_date)} -{' '}
                        {experience.is_current ? 'Présent' : formatDate(experience.end_date!)}
                      </span>
                      <span className="text-gray-400 ml-2">
                        ({calculateDuration(experience.start_date, experience.end_date)})
                      </span>
                    </div>
                    {experience.location && (
                      <div className="flex items-center gap-1">
                        <MapPinIcon className="h-4 w-4" />
                        <span>{experience.location}</span>
                      </div>
                    )}
                  </div>

                  {/* Description */}
                  {experience.description && (
                    <p className="mt-3 text-gray-600 text-sm whitespace-pre-line">
                      {experience.description}
                    </p>
                  )}

                  {/* Achievements */}
                  {experience.achievements.length > 0 && (
                    <div className="mt-3">
                      <h4 className="text-sm font-semibold text-gray-700 mb-2">
                        Réalisations clés :
                      </h4>
                      <ul className="space-y-1">
                        {experience.achievements.map((achievement, index) => (
                          <li key={index} className="flex items-start gap-2 text-sm text-gray-600">
                            <CheckCircleIcon className="h-4 w-4 text-green-500 flex-shrink-0 mt-0.5" />
                            <span>{achievement}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Skills */}
                  {experience.skills_used.length > 0 && (
                    <div className="mt-3">
                      <h4 className="text-sm font-semibold text-gray-700 mb-2">Compétences :</h4>
                      <div className="flex flex-wrap gap-2">
                        {experience.skills_used.map((skill, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 ml-4">
                  <button
                    onClick={() => handleEdit(experience)}
                    className="p-2 text-gray-600 hover:text-jlc-purple-600 hover:bg-jlc-purple-50 rounded transition-colors"
                    title="Modifier"
                  >
                    <PencilIcon className="h-5 w-5" />
                  </button>
                  <button
                    onClick={() => handleDelete(experience)}
                    className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                    title="Supprimer"
                    disabled={isDeleting}
                  >
                    <TrashIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal for Create/Edit */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          resetForm()
        }}
        title={editingExperience ? 'Modifier l\'expérience' : 'Ajouter une expérience'}
        maxWidth="3xl"
      >
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Type d'expérience
            </label>
            <select
              value={formData.type}
              onChange={(e) =>
                setFormData({ ...formData, type: e.target.value as 'internal_jlc' | 'external' })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
            >
              <option value="external">Expérience externe</option>
              <option value="internal_jlc">Mission JLC</option>
            </select>
          </div>

          {/* Job Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Intitulé du poste <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.job_title}
              onChange={(e) => setFormData({ ...formData, job_title: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              placeholder="ex: Développeur Full Stack"
              required
            />
          </div>

          {/* Company Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Entreprise <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.company_name}
              onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              placeholder="ex: JLC Group"
              required
            />
          </div>

          {/* Location */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Localisation</label>
            <input
              type="text"
              value={formData.location}
              onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              placeholder="ex: Paris, France"
            />
          </div>

          {/* Dates */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Date de début <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                value={formData.start_date}
                onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Date de fin</label>
              <input
                type="date"
                value={formData.end_date}
                onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
                disabled={formData.is_current}
              />
            </div>
          </div>

          {/* Is Current */}
          <div className="flex items-center">
            <input
              type="checkbox"
              id="is_current"
              checked={formData.is_current}
              onChange={(e) =>
                setFormData({ ...formData, is_current: e.target.checked, end_date: '' })
              }
              className="h-4 w-4 text-jlc-purple-600 focus:ring-jlc-purple-500 border-gray-300 rounded"
            />
            <label htmlFor="is_current" className="ml-2 text-sm text-gray-700">
              Je travaille actuellement dans ce poste
            </label>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              placeholder="Décrivez vos missions et responsabilités..."
            />
          </div>

          {/* Achievements */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Réalisations clés
            </label>
            <div className="flex gap-2 mb-3">
              <input
                type="text"
                value={achievementInput}
                onChange={(e) => setAchievementInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addAchievement())}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
                placeholder="ex: Réduction des coûts de 30%"
              />
              <Button type="button" variant="secondary" onClick={addAchievement}>
                <PlusIcon className="h-5 w-5" />
              </Button>
            </div>
            {formData.achievements && formData.achievements.length > 0 && (
              <div className="space-y-2">
                {formData.achievements.map((achievement, index) => (
                  <div key={index} className="flex items-center gap-2 p-2 bg-gray-50 rounded">
                    <CheckCircleIcon className="h-4 w-4 text-green-500 flex-shrink-0" />
                    <span className="flex-1 text-sm">{achievement}</span>
                    <button
                      type="button"
                      onClick={() => removeAchievement(index)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <XMarkIcon className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Skills */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Compétences utilisées</label>
            <div className="flex gap-2 mb-3">
              <input
                type="text"
                value={skillInput}
                onChange={(e) => setSkillInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
                placeholder="ex: React, Node.js, MongoDB"
              />
              <Button type="button" variant="secondary" onClick={addSkill}>
                <PlusIcon className="h-5 w-5" />
              </Button>
            </div>
            {formData.skills_used && formData.skills_used.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {formData.skills_used.map((skill, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center gap-1 px-3 py-1 text-sm bg-jlc-purple-100 text-jlc-purple-700 rounded-full"
                  >
                    {skill}
                    <button
                      type="button"
                      onClick={() => removeSkill(index)}
                      className="hover:text-jlc-purple-900"
                    >
                      <XMarkIcon className="h-4 w-4" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button
              type="button"
              variant="secondary"
              onClick={() => {
                setIsModalOpen(false)
                resetForm()
              }}
            >
              Annuler
            </Button>
            <Button
              type="submit"
              variant="primary"
              isLoading={isCreating || isUpdating}
              disabled={isCreating || isUpdating}
            >
              {editingExperience ? 'Mettre à jour' : 'Ajouter'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
