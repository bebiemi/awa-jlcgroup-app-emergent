/**
 * Company Settings Page - Version Dynamique
 * Utilise les champs de formulaire configurés dynamiquement
 */
import { useState, useEffect } from 'react'
import Layout from '@/components/Layout'
import Card from '@/components/Card'
import Button from '@/components/Button'
import DynamicFormField from '@/features/company/components/DynamicFormField'
import {
  BuildingOfficeIcon,
  PencilIcon,
  CheckCircleIcon,
  XMarkIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline'
import {
  useGetMyEntrepriseQuery,
  useUpdateMyEntrepriseMutation,
} from '@/features/company/api/entrepriseApi'
import { useGetFormFieldsQuery } from '@/features/company/api/entrepriseFormConfigApi'
import toast from 'react-hot-toast'

export default function CompanySettingsPageDynamic() {
  const { data: entreprise, isLoading: isLoadingEntreprise } = useGetMyEntrepriseQuery()
  const { data: formConfig, isLoading: isLoadingFields } = useGetFormFieldsQuery({ is_active: true })
  const [updateEntreprise, { isLoading: isUpdating }] = useUpdateMyEntrepriseMutation()

  // État du formulaire dynamique
  const [formData, setFormData] = useState<Record<string, any>>({})
  const [isEditing, setIsEditing] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  // Charger les données de l'entreprise dans le formulaire
  useEffect(() => {
    if (entreprise && formConfig?.fields) {
      const initialData: Record<string, any> = {}
      
      // Mapper les données de l'entreprise vers les clés des champs dynamiques
      formConfig.fields.forEach((field) => {
        // Mapping des anciens champs vers les nouveaux
        const fieldMapping: Record<string, string> = {
          'nom_commercial': 'nom',
          'raison_sociale': 'raison_sociale',
          'siret': 'siret',
          'nif': 'nif',
          'email': 'email',
          'telephone': 'telephone',
          'representant_legal': 'legal_representative',
          'adresse': 'adresse',
          'code_postal': 'code_postal',
          'ville': 'ville',
          'pays': 'pays',
          'secteur_activite': 'secteur_activite',
          'effectif': 'effectif',
          'site_web': 'site_web',
          'description': 'description',
        }
        
        const apiFieldKey = fieldMapping[field.field_key] || field.field_key
        initialData[field.field_key] = (entreprise as any)[apiFieldKey] || field.default_value || ''
      })
      
      setFormData(initialData)
    }
  }, [entreprise, formConfig])

  const handleFieldChange = (key: string, value: any) => {
    setFormData(prev => ({ ...prev, [key]: value }))
    // Effacer l'erreur du champ modifié
    if (errors[key]) {
      setErrors(prev => {
        const newErrors = { ...prev }
        delete newErrors[key]
        return newErrors
      })
    }
  }

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    formConfig?.fields.forEach((field) => {
      if (field.validation.required && field.visible_for_roles.includes('company')) {
        const value = formData[field.field_key]
        if (!value || (typeof value === 'string' && !value.trim())) {
          newErrors[field.field_key] = field.validation.custom_error_message || `${field.field_label} est requis`
        }
      }
    })

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      toast.error('Veuillez corriger les erreurs du formulaire')
      return
    }

    try {
      // Mapper les données du formulaire vers le format API
      const payload: any = {
        nom: formData.nom_commercial || formData.raison_sociale,
        raison_sociale: formData.raison_sociale,
        siret: formData.siret,
        nif: formData.nif,
        email: formData.email,
        telephone: formData.telephone,
        adresse: formData.adresse,
        code_postal: formData.code_postal,
        ville: formData.ville,
        pays: formData.pays,
        secteur_activite: formData.secteur_activite,
        effectif: formData.effectif,
        site_web: formData.site_web,
        description: formData.description,
      }

      await updateEntreprise(payload).unwrap()
      toast.success('Les informations de votre entreprise ont été mises à jour avec succès.')
      setIsEditing(false)
    } catch (err: any) {
      toast.error(err?.data?.detail || 'Une erreur est survenue lors de la mise à jour.')
    }
  }

  const handleCancel = () => {
    // Recharger les données depuis l'entreprise
    if (entreprise && formConfig?.fields) {
      const initialData: Record<string, any> = {}
      
      formConfig.fields.forEach((field) => {
        const fieldMapping: Record<string, string> = {
          'nom_commercial': 'nom',
          'raison_sociale': 'raison_sociale',
          'siret': 'siret',
          'nif': 'nif',
          'email': 'email',
          'telephone': 'telephone',
          'representant_legal': 'legal_representative',
          'adresse': 'adresse',
          'code_postal': 'code_postal',
          'ville': 'ville',
          'pays': 'pays',
          'secteur_activite': 'secteur_activite',
          'effectif': 'effectif',
          'site_web': 'site_web',
          'description': 'description',
        }
        
        const apiFieldKey = fieldMapping[field.field_key] || field.field_key
        initialData[field.field_key] = (entreprise as any)[apiFieldKey] || field.default_value || ''
      })
      
      setFormData(initialData)
    }
    setIsEditing(false)
    setErrors({})
  }

  if (isLoadingEntreprise || isLoadingFields) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <ArrowPathIcon className="h-8 w-8 animate-spin text-jlc-purple-600" />
        </div>
      </Layout>
    )
  }

  if (!entreprise) {
    return (
      <Layout>
        <Card>
          <p className="text-red-600">Aucune entreprise associée à ce compte.</p>
        </Card>
      </Layout>
    )
  }

  // Grouper les champs par catégorie
  const fieldsByCategory = formConfig?.fields.reduce((acc, field) => {
    if (field.visible_for_roles.includes('company')) {
      if (!acc[field.category]) {
        acc[field.category] = []
      }
      acc[field.category].push(field)
    }
    return acc
  }, {} as Record<string, typeof formConfig.fields>)

  // Mapping des titres de catégories
  const categoryTitles: Record<string, { title: string; icon: any }> = {
    'informations_generales': { title: 'Informations Générales', icon: BuildingOfficeIcon },
    'informations_legales': { title: 'Informations Légales', icon: CheckCircleIcon },
    'contact': { title: 'Coordonnées de Contact', icon: BuildingOfficeIcon },
    'localisation': { title: 'Localisation', icon: BuildingOfficeIcon },
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Paramètres de l'Entreprise
            </h1>
            <p className="mt-2 text-gray-600">
              Gérez les informations de votre entreprise
            </p>
          </div>
          {!isEditing && (
            <Button onClick={() => setIsEditing(true)} variant="primary">
              <PencilIcon className="h-5 w-5 mr-2" />
              Modifier
            </Button>
          )}
        </div>

        {/* Formulaire */}
        <form onSubmit={handleSubmit}>
          {/* Afficher les champs par catégorie */}
          {Object.entries(fieldsByCategory || {}).map(([category, fields]) => {
            const categoryInfo = categoryTitles[category] || { title: category, icon: BuildingOfficeIcon }
            const Icon = categoryInfo.icon

            return (
              <Card key={category} className="mb-6">
                <div className="flex items-center mb-4 pb-4 border-b border-gray-200">
                  <Icon className="h-6 w-6 text-jlc-purple-600 mr-3" />
                  <h2 className="text-xl font-semibold text-gray-900">
                    {categoryInfo.title}
                  </h2>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {fields
                    .sort((a, b) => a.order - b.order)
                    .map((field) => (
                      <div
                        key={field.id}
                        className={field.field_type === 'textarea' ? 'md:col-span-2' : ''}
                      >
                        <DynamicFormField
                          field={field}
                          value={formData[field.field_key]}
                          onChange={handleFieldChange}
                          error={errors[field.field_key]}
                          disabled={!isEditing}
                        />
                      </div>
                    ))}
                </div>
              </Card>
            )
          })}

          {/* Boutons d'action */}
          {isEditing && (
            <div className="flex justify-end space-x-4">
              <Button
                type="button"
                onClick={handleCancel}
                variant="secondary"
                disabled={isUpdating}
              >
                <XMarkIcon className="h-5 w-5 mr-2" />
                Annuler
              </Button>
              <Button
                type="submit"
                variant="primary"
                disabled={isUpdating}
              >
                {isUpdating ? (
                  <>
                    <ArrowPathIcon className="h-5 w-5 mr-2 animate-spin" />
                    Enregistrement...
                  </>
                ) : (
                  <>
                    <CheckCircleIcon className="h-5 w-5 mr-2" />
                    Enregistrer
                  </>
                )}
              </Button>
            </div>
          )}
        </form>
      </div>
    </Layout>
  )
}
