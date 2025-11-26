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
import { usePermissions } from '@/hooks/usePermission'

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
  const { permissions } = usePermissions(['references.read', 'references.manage'])
  const canRead = permissions['references.read'] || permissions['references.manage']
  const canManage = permissions['references.manage']
  
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
    
    if (!canManage) return
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
  
  if (!canRead) return null

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
          {canManage && (
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
          )}
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
                disabled={!canRead}
              >
                <div className="text-lg mb-1">{cat.icon}</div>
                <div className="text-xs">{cat.label}</div>
              </button>
            ))}
          </div>
        </Card>
        
        {/* Statistiques */}
        {!isLoading && data && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total</p>
                  <p className="text-2xl font-bold text-gray-900">{data.references.length}</p>
                </div>
                <div className="text-3xl">📊</div>
              </div>
            </Card>
            <Card>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Actifs</p>
                  <p className="text-2xl font-bold text-green-600">
                    {data.references.filter((r: any) => r.is_active).length}
                  </p>
                </div>
                <div className="text-3xl">✅</div>
              </div>
            </Card>
            <Card>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Inactifs</p>
                  <p className="text-2xl font-bold text-red-600">
                    {data.references.filter((r: any) => !r.is_active).length}
                  </p>
                </div>
                <div className="text-3xl">❌</div>
              </div>
            </Card>
            <Card>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Système</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {data.references.filter((r: any) => r.is_system).length}
                  </p>
                </div>
                <div className="text-3xl">🔒</div>
              </div>
            </Card>
          </div>
        )}
        
        {/* Liste des référentiels */}
        <Card>
          {isLoading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
              <p className="mt-4 text-gray-600">Chargement...</p>
            </div>
          ) : data?.references.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📭</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Aucun référentiel</h3>
              <p className="text-gray-500 mb-4">
                Cette catégorie ne contient aucun référentiel pour le moment.
              </p>
              <button
                onClick={() => {
                  resetForm()
                  setShowModal(true)
                }}
                className="inline-flex items-center gap-2 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700"
              >
                <PlusIcon className="h-5 w-5" />
                Créer le premier référentiel
              </button>
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
                      Description
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Ordre
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Métadonnées
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Statut
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {data?.references.map((ref) => (
                    <tr key={ref.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <code className="text-sm font-mono font-medium text-gray-900 bg-gray-100 px-2 py-1 rounded">
                            {ref.code}
                          </code>
                          {ref.is_system && (
                            <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                              Système
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">
                        {ref.label_fr}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {ref.label_en || '-'}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate" title={ref.description}>
                        {ref.description || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-gray-100 font-medium">
                          {ref.order}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm">
                        {ref.metadata && Object.keys(ref.metadata).length > 0 ? (
                          <div className="flex flex-wrap gap-1">
                            {ref.metadata.color && (
                              <span 
                                className="inline-block w-6 h-6 rounded-full border-2 border-gray-200" 
                                style={{ backgroundColor: ref.metadata.color }}
                                title={`Couleur: ${ref.metadata.color}`}
                              />
                            )}
                            {ref.metadata.icon && (
                              <span className="px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded">
                                🎨 {ref.metadata.icon}
                              </span>
                            )}
                            {ref.metadata.years && (
                              <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded">
                                📅 {ref.metadata.years}
                              </span>
                            )}
                            {ref.metadata.hours && (
                              <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                                🕐 {ref.metadata.hours}
                              </span>
                            )}
                          </div>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-3 py-1 text-xs font-medium rounded-full ${
                          ref.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {ref.is_active ? '✓ Actif' : '✗ Inactif'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleEdit(ref)}
                            className="p-2 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors"
                            title="Modifier"
                          >
                            <PencilIcon className="h-5 w-5" />
                          </button>
                          {!ref.is_system && (
                            <button
                              onClick={() => handleDelete(ref.id, ref.is_system)}
                              className="p-2 text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg transition-colors"
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
