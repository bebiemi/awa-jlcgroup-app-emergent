import { useState } from 'react'
import Layout from '@/components/Layout'
import Card from '@/components/Card'
import Modal from '@/components/Modal'
import {
  useGetReferencesQuery,
  useCreateReferenceMutation,
  useUpdateReferenceMutation,
  useDeleteReferenceMutation,
} from '../api/configurationApi'
import { PlusIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/outline'

const categories = [
  { value: 'roles', label: 'Rôles Utilisateurs', icon: '👥' },
  { value: 'user_statuses', label: 'Statuts Utilisateurs', icon: '👤' },
  { value: 'mission_statuses', label: 'Statuts de Mission', icon: '💼' },
  { value: 'application_statuses', label: 'Statuts de Candidature', icon: '📋' },
  { value: 'validation_types', label: 'Types de Validation', icon: '✓' },
  { value: 'validation_statuses', label: 'Statuts de Validation', icon: '✅' },
  { value: 'contract_types', label: 'Types de Contrat', icon: '📝' },
  { value: 'document_types', label: 'Types de Documents', icon: '📄' },
  { value: 'experience_levels', label: 'Niveaux d\'Expérience', icon: '📊' },
  { value: 'education_levels', label: 'Niveaux d\'Éducation', icon: '🎓' },
  { value: 'skill_categories', label: 'Catégories de Compétences', icon: '🎯' },
  { value: 'skills', label: 'Compétences', icon: '⚡' },
  { value: 'work_schedules', label: 'Types d\'Horaires', icon: '🕐' },
  { value: 'salary_ranges', label: 'Fourchettes Salariales', icon: '💰' },
  { value: 'countries', label: 'Pays', icon: '🌍' },
  { value: 'medical_aptitudes', label: 'Aptitudes Médicales', icon: '🏥' },
]

export default function ReferencesManagementPage() {
  const [selectedCategory, setSelectedCategory] = useState('mission_statuses')
  const [showModal, setShowModal] = useState(false)
  const [editingRef, setEditingRef] = useState<any>(null)
  
  const { data, isLoading } = useGetReferencesQuery({
    category: selectedCategory,
    is_active: undefined,
  })
  
  const [createReference] = useCreateReferenceMutation()
  const [updateReference] = useUpdateReferenceMutation()
  const [deleteReference] = useDeleteReferenceMutation()
  
  const [formData, setFormData] = useState({
    code: '',
    label_fr: '',
    label_en: '',
    description: '',
    order: 0,
    is_active: true,
    metadata: {},
  })
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      if (editingRef) {
        await updateReference({
          id: editingRef.id,
          data: formData,
        }).unwrap()
      } else {
        await createReference({
          category: selectedCategory,
          ...formData,
        }).unwrap()
      }
      
      setShowModal(false)
      resetForm()
    } catch (error: any) {
      console.error('Erreur:', error)
      alert(error?.data?.detail || 'Une erreur est survenue')
    }
  }
  
  const resetForm = () => {
    setFormData({
      code: '',
      label_fr: '',
      label_en: '',
      description: '',
      order: 0,
      is_active: true,
      metadata: {},
    })
    setEditingRef(null)
  }
  
  const handleEdit = (ref: any) => {
    setEditingRef(ref)
    setFormData({
      code: ref.code,
      label_fr: ref.label_fr,
      label_en: ref.label_en || '',
      description: ref.description || '',
      order: ref.order,
      is_active: ref.is_active,
      metadata: ref.metadata || {},
    })
    setShowModal(true)
  }
  
  const handleDelete = async (id: string, isSystem: boolean) => {
    if (isSystem) {
      alert('Les référentiels système ne peuvent pas être supprimés')
      return
    }
    
    if (confirm('Êtes-vous sûr de vouloir supprimer ce référentiel ?')) {
      try {
        await deleteReference(id).unwrap()
      } catch (error: any) {
        console.error('Erreur:', error)
        alert(error?.data?.detail || 'Erreur lors de la suppression')
      }
    }
  }
  
  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Gestion des Référentiels
            </h1>
            <p className="text-gray-600">
              Gérez les valeurs configurables de l'application
            </p>
          </div>
          <button
            onClick={() => {
              resetForm()
              setShowModal(true)
            }}
            className="flex items-center gap-2 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700"
          >
            <PlusIcon className="h-5 w-5" />
            Nouveau
          </button>
        </div>
        
        {/* Sélecteur de catégorie */}
        <Card>
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Catégories</h3>
            <p className="text-sm text-gray-600">Sélectionnez une catégorie pour gérer ses références</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-2">
            {categories.map((cat) => (
              <button
                key={cat.value}
                onClick={() => setSelectedCategory(cat.value)}
                className={`px-3 py-2 rounded-lg transition-all text-sm font-medium ${
                  selectedCategory === cat.value
                    ? 'bg-jlc-purple-600 text-white shadow-lg scale-105'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200 hover:scale-102'
                }`}
              >
                <div className="text-lg mb-1">{cat.icon}</div>
                <div className="text-xs">{cat.label}</div>
              </button>
            ))}
          </div>
        </Card>
        
        {/* Liste des référentiels */}
        <Card>
          {isLoading ? (
            <p>Chargement...</p>
          ) : data?.references.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              Aucun référentiel dans cette catégorie
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Code
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Label FR
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Label EN
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Ordre
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Statut
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Système
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {data?.references.map((ref) => (
                    <tr key={ref.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {ref.code}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {ref.label_fr}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {ref.label_en || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {ref.order}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          ref.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {ref.is_active ? 'Actif' : 'Inactif'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {ref.is_system && (
                          <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                            Système
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleEdit(ref)}
                            className="text-blue-600 hover:text-blue-800"
                            title="Modifier"
                          >
                            <PencilIcon className="h-5 w-5" />
                          </button>
                          {!ref.is_system && (
                            <button
                              onClick={() => handleDelete(ref.id, ref.is_system)}
                              className="text-red-600 hover:text-red-800"
                              title="Supprimer"
                            >
                              <TrashIcon className="h-5 w-5" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>
      
      {/* Modal Création/Édition */}
      <Modal
        isOpen={showModal}
        onClose={() => {
          setShowModal(false)
          resetForm()
        }}
        title={editingRef ? 'Modifier le référentiel' : 'Nouveau référentiel'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Code *
            </label>
            <input
              type="text"
              value={formData.code}
              onChange={(e) => setFormData({ ...formData, code: e.target.value })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-jlc-purple-500 focus:ring-jlc-purple-500"
              required
              disabled={!!editingRef}
            />
            <p className="mt-1 text-xs text-gray-500">
              Identifiant unique (lettres, chiffres, tirets bas)
            </p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Label FR *
            </label>
            <input
              type="text"
              value={formData.label_fr}
              onChange={(e) => setFormData({ ...formData, label_fr: e.target.value })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-jlc-purple-500 focus:ring-jlc-purple-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Label EN
            </label>
            <input
              type="text"
              value={formData.label_en}
              onChange={(e) => setFormData({ ...formData, label_en: e.target.value })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-jlc-purple-500 focus:ring-jlc-purple-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-jlc-purple-500 focus:ring-jlc-purple-500"
              rows={3}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Ordre d'affichage
            </label>
            <input
              type="number"
              value={formData.order}
              onChange={(e) => setFormData({ ...formData, order: parseInt(e.target.value) || 0 })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-jlc-purple-500 focus:ring-jlc-purple-500"
            />
          </div>
          
          <div className="flex items-center">
            <input
              type="checkbox"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              className="h-4 w-4 text-jlc-purple-600 rounded focus:ring-jlc-purple-500"
            />
            <label className="ml-2 block text-sm text-gray-900">
              Actif
            </label>
          </div>
          
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={() => {
                setShowModal(false)
                resetForm()
              }}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              Annuler
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700"
            >
              {editingRef ? 'Modifier' : 'Créer'}
            </button>
          </div>
        </form>
      </Modal>
    </Layout>
  )
}
