import { useState } from 'react'
import Layout from '@/components/Layout'
import Button from '@/components/Button'
import {
  useGetFormFieldsQuery,
  useDeleteFormFieldMutation,
  useUpdateFormFieldMutation,
  type FormFieldConfig,
} from '@/features/company/api/entrepriseFormConfigApi'
import {
  Cog6ToothIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon,
  EyeSlashIcon,
  ArrowsUpDownIcon,
} from '@heroicons/react/24/outline'
import CreateFieldModal from '../components/CreateFieldModal'
import EditFieldModal from '../components/EditFieldModal'
import { usePermissions } from '@/hooks/usePermission'

export default function EntrepriseFormConfigPage() {
  const { permissions } = usePermissions(['forms.enterprise.manage'])
  const canManage = permissions['forms.enterprise.manage']
  const { data, isLoading, refetch } = useGetFormFieldsQuery({})
  const [deleteField] = useDeleteFormFieldMutation()
  const [updateField] = useUpdateFormFieldMutation()

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [editingField, setEditingField] = useState<FormFieldConfig | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')

  const fields = data?.fields || []
  const categories = data?.categories || []

  // Filtrer par catégorie
  const filteredFields = selectedCategory === 'all'
    ? fields
    : fields.filter((f) => f.category === selectedCategory)

  // Grouper par catégorie pour l'affichage
  const fieldsByCategory = filteredFields.reduce((acc, field) => {
    const cat = field.category || 'general'
    if (!acc[cat]) {
      acc[cat] = []
    }
    acc[cat].push(field)
    return acc
  }, {} as Record<string, FormFieldConfig[]>)

  const handleDelete = async (id: string, fieldKey: string) => {
    if (!canManage) return
    if (window.confirm(`Êtes-vous sûr de vouloir supprimer le champ "${fieldKey}" ?`)) {
      try {
        await deleteField(id).unwrap()
      } catch (error) {
        console.error('Failed to delete field:', error)
        alert('Erreur lors de la suppression')
      }
    }
  }

  const handleToggleActive = async (field: FormFieldConfig) => {
    if (!canManage) return
    try {
      await updateField({
        id: field.id,
        data: { is_active: !field.is_active },
      }).unwrap()
    } catch (error) {
      console.error('Failed to toggle field:', error)
    }
  }

  const getFieldTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      text: 'Texte',
      textarea: 'Zone de texte',
      select: 'Liste déroulante',
      multiselect: 'Liste multiple',
      checkbox: 'Case à cocher',
      radio: 'Boutons radio',
      date: 'Date',
      number: 'Nombre',
      email: 'Email',
      tel: 'Téléphone',
      url: 'URL',
      file: 'Fichier',
    }
    return labels[type] || type
  }

  if (!canManage) return null

  if (isLoading) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Cog6ToothIcon className="h-8 w-8 text-jlc-purple-600" />
              Configuration Formulaire Entreprise
            </h1>
            <p className="mt-2 text-gray-600">
              Gérez les champs dynamiques du formulaire entreprise
            </p>
          </div>
          {canManage && (
            <Button onClick={() => setIsCreateModalOpen(true)} variant="primary">
              <PlusIcon className="h-5 w-5 mr-2" />
              Nouveau champ
            </Button>
          )}
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Champs</p>
                <p className="text-2xl font-bold text-gray-900">{fields.length}</p>
              </div>
              <Cog6ToothIcon className="h-8 w-8 text-jlc-purple-600" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Champs Actifs</p>
                <p className="text-2xl font-bold text-green-600">
                  {fields.filter((f) => f.is_active).length}
                </p>
              </div>
              <EyeIcon className="h-8 w-8 text-green-600" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Champs Inactifs</p>
                <p className="text-2xl font-bold text-gray-400">
                  {fields.filter((f) => !f.is_active).length}
                </p>
              </div>
              <EyeSlashIcon className="h-8 w-8 text-gray-400" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Catégories</p>
                <p className="text-2xl font-bold text-blue-600">{categories.length}</p>
              </div>
              <ArrowsUpDownIcon className="h-8 w-8 text-blue-600" />
            </div>
          </div>
        </div>

        {/* Filtres */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-medium text-gray-700">Catégorie:</span>
            <button
              onClick={() => setSelectedCategory('all')}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                selectedCategory === 'all'
                  ? 'bg-jlc-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Toutes ({fields.length})
            </button>
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                  selectedCategory === cat
                    ? 'bg-jlc-purple-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {cat} ({fields.filter((f) => f.category === cat).length})
              </button>
            ))}
          </div>
        </div>

        {/* Liste des champs par catégorie */}
        {filteredFields.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <Cog6ToothIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Aucun champ configuré</h3>
            <p className="text-gray-600 mb-4">
              Commencez par créer votre premier champ personnalisé
            </p>
            <Button onClick={() => setIsCreateModalOpen(true)} variant="primary">
              <PlusIcon className="h-5 w-5 mr-2" />
              Créer un champ
            </Button>
          </div>
        ) : (
          <div className="space-y-6">
            {Object.entries(fieldsByCategory).map(([category, categoryFields]) => (
              <div key={category} className="bg-white rounded-lg shadow">
                {/* Category Header */}
                <div className="bg-gray-50 px-6 py-3 border-b border-gray-200">
                  <h2 className="text-lg font-semibold text-gray-900 capitalize">{category}</h2>
                  <p className="text-sm text-gray-600">{categoryFields.length} champ(s)</p>
                </div>

                {/* Fields List */}
                <div className="divide-y divide-gray-200">
                  {categoryFields
                    .sort((a, b) => a.order - b.order)
                    .map((field) => (
                      <div
                        key={field.id}
                        className={`p-6 hover:bg-gray-50 transition-colors ${
                          !field.is_active ? 'opacity-50' : ''
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <h3 className="text-lg font-semibold text-gray-900">
                                {field.field_label}
                              </h3>
                              <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded">
                                {getFieldTypeLabel(field.field_type)}
                              </span>
                              {field.validation.required && (
                                <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-700 rounded">
                                  Requis
                                </span>
                              )}
                              {field.is_system && (
                                <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded">
                                  Système
                                </span>
                              )}
                              {!field.is_active && (
                                <span className="px-2 py-1 text-xs font-medium bg-gray-200 text-gray-600 rounded">
                                  Inactif
                                </span>
                              )}
                            </div>

                            <div className="space-y-1 text-sm text-gray-600">
                              <p>
                                <span className="font-medium">Clé:</span>{' '}
                                <code className="bg-gray-100 px-2 py-0.5 rounded text-xs">
                                  {field.field_key}
                                </code>
                              </p>
                              {field.placeholder && (
                                <p>
                                  <span className="font-medium">Placeholder:</span> {field.placeholder}
                                </p>
                              )}
                              {field.help_text && (
                                <p>
                                  <span className="font-medium">Aide:</span> {field.help_text}
                                </p>
                              )}
                              <p>
                                <span className="font-medium">Visible pour:</span>{' '}
                                {field.visible_for_roles.join(', ')}
                              </p>
                              <p>
                                <span className="font-medium">Éditable par:</span>{' '}
                                {field.editable_for_roles.join(', ')}
                              </p>
                              {field.options && field.options.length > 0 && (
                                <p>
                                  <span className="font-medium">Options:</span>{' '}
                                  {field.options.map((o) => o.label).join(', ')}
                                </p>
                              )}
                            </div>
                          </div>

                          {/* Actions */}
                          <div className="flex items-center gap-2 ml-4">
                            <button
                              onClick={() => handleToggleActive(field)}
                              className={`p-2 rounded-lg transition-colors ${
                                field.is_active
                                  ? 'text-green-600 hover:bg-green-50'
                                  : 'text-gray-400 hover:bg-gray-100'
                              }`}
                              title={field.is_active ? 'Désactiver' : 'Activer'}
                            >
                              {field.is_active ? (
                                <EyeIcon className="h-5 w-5" />
                              ) : (
                                <EyeSlashIcon className="h-5 w-5" />
                              )}
                            </button>
                            <button
                              onClick={() => setEditingField(field)}
                              className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                              title="Modifier"
                            >
                              <PencilIcon className="h-5 w-5" />
                            </button>
                            {!field.is_system && (
                              <button
                                onClick={() => handleDelete(field.id, field.field_key)}
                                className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                title="Supprimer"
                              >
                                <TrashIcon className="h-5 w-5" />
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Modals */}
        <CreateFieldModal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          onSuccess={() => {
            setIsCreateModalOpen(false)
            refetch()
          }}
        />

        {editingField && (
          <EditFieldModal
            field={editingField}
            isOpen={true}
            onClose={() => setEditingField(null)}
            onSuccess={() => {
              setEditingField(null)
              refetch()
            }}
          />
        )}
      </div>
    </Layout>
  )
}
