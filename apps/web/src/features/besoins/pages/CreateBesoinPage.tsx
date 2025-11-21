import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout from '@/components/Layout'
import { ArrowLeftIcon, PaperAirplaneIcon } from '@heroicons/react/24/outline'
import { useCreateBesoinMutation } from '../api/besoinsApi'
import { useGetFormSchemaQuery, useGetReferenceDataQuery } from '../api/configApi'
import { toast } from 'react-hot-toast'
import DynamicForm from '../components/DynamicForm'

export default function CreateBesoinPage() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState<Record<string, any>>({})
  const [errors, setErrors] = useState<Record<string, string>>({})

  const { data: formSchema, isLoading: loadingSchema } = useGetFormSchemaQuery('besoin')
  const { data: typesPoste } = useGetReferenceDataQuery('types_poste')
  const { data: competences } = useGetReferenceDataQuery('competences')
  
  const [createBesoin, { isLoading: creating }] = useCreateBesoinMutation()

  // Set default values from schema
  useEffect(() => {
    if (formSchema) {
      const defaults: Record<string, any> = {}
      formSchema.fields.forEach((field) => {
        if (field.default_value !== undefined) {
          defaults[field.key] = field.default_value
        }
      })
      setFormData(defaults)
    }
  }, [formSchema])

  const validateForm = (): boolean => {
    if (!formSchema) return false

    const newErrors: Record<string, string> = {}
    
    formSchema.fields.forEach((field) => {
      if (field.required && !formData[field.key]) {
        newErrors[field.key] = field.validations.find((v) => v.type === 'required')?.message || 'Ce champ est requis'
      }

      // Additional validations
      if (formData[field.key]) {
        field.validations.forEach((validation) => {
          if (validation.type === 'min_length' && formData[field.key].length < (validation.value as number)) {
            newErrors[field.key] = validation.message
          }
          if (validation.type === 'max_length' && formData[field.key].length > (validation.value as number)) {
            newErrors[field.key] = validation.message
          }
        })
      }
    })

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (saveAsDraft: boolean = false) => {
    if (!validateForm()) {
      toast.error('Veuillez corriger les erreurs du formulaire')
      return
    }

    try {
      const payload = {
        titre: formData.titre,
        description: formData.description,
        duree: formData.duree,
        date_debut_souhaitee: formData.date_debut_souhaitee || undefined,
        date_fin_souhaitee: formData.date_fin_souhaitee || undefined,
        type_poste: formData.type_poste,
        competences_attendues: formData.competences_attendues || [],
        pieces_jointes: formData.pieces_jointes || [],
        custom_fields: {},
      }

      const result = await createBesoin(payload).unwrap()
      
      if (saveAsDraft) {
        toast.success('Besoin enregistré en brouillon')
      } else {
        toast.success('Besoin créé avec succès')
      }
      
      navigate(`/entreprise/besoins/${result.id}`)
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la création du besoin')
    }
  }

  if (loadingSchema) {
    return (
      <Layout>
        <div className="animate-pulse space-y-6">
          <div className="h-10 bg-gray-200 rounded w-1/3" />
          <div className="h-64 bg-gray-200 rounded" />
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/entreprise/besoins')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeftIcon className="h-5 w-5 text-gray-600" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Créer un besoin</h1>
            <p className="text-gray-600 mt-1">Décrivez votre besoin de recrutement</p>
          </div>
        </div>

        {/* Form */}
        <div className="bg-white rounded-2xl shadow-md border border-gray-100 overflow-hidden">
          <div className="bg-gradient-to-r from-jlc-purple-50 to-indigo-50 px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Informations du besoin</h2>
          </div>

          <div className="p-6">
            {formSchema && (
              <DynamicForm
                schema={formSchema}
                data={formData}
                onChange={setFormData}
                errors={errors}
                referenceData={{
                  types_poste: typesPoste?.items || [],
                  competences: competences?.items || [],
                }}
              />
            )}
          </div>

          {/* Actions */}
          <div className="bg-gray-50 px-6 py-4 border-t border-gray-200 flex items-center justify-between">
            <button
              onClick={() => navigate('/entreprise/besoins')}
              className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              disabled={creating}
            >
              Annuler
            </button>
            <div className="flex gap-3">
              <button
                onClick={() => handleSubmit(true)}
                disabled={creating}
                className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                {creating ? 'Enregistrement...' : 'Enregistrer en brouillon'}
              </button>
              <button
                onClick={() => handleSubmit(false)}
                disabled={creating}
                className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-jlc-purple-600 to-indigo-600 text-white rounded-lg hover:from-jlc-purple-700 hover:to-indigo-700 shadow-md transition-all disabled:opacity-50"
              >
                <PaperAirplaneIcon className="h-5 w-5" />
                {creating ? 'Création...' : 'Créer le besoin'}
              </button>
            </div>
          </div>
        </div>

        {/* Help text */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-900">
            💡 <strong>Astuce:</strong> Vous pouvez enregistrer votre besoin en brouillon et le compléter plus tard. 
            Une fois créé, vous pourrez le soumettre à JLC pour validation.
          </p>
        </div>
      </div>
    </Layout>
  )
}
