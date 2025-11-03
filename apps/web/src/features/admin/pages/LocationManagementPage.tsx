import { useState } from 'react'
import Layout from '@/components/Layout'
import Modal from '@/components/Modal'
import ActionButton, { ActionButtonGroup } from '@/components/ActionButton'
import {
  useGetLocationsQuery,
  useGetLocationTreeQuery,
  useCreateLocationMutation,
  useUpdateLocationMutation,
  useDeleteLocationMutation,
  useToggleLocationVisibilityMutation,
  type Location,
  type LocationCreate,
  type LocationType,
} from '../api/locationApi'
import {
  GlobeAltIcon,
  MapIcon,
  BuildingOfficeIcon,
  HomeIcon,
  PlusIcon,
  EyeIcon,
  EyeSlashIcon,
  ChevronRightIcon,
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

const LOCATION_TYPES: { value: LocationType; label: string; icon: any }[] = [
  { value: 'country', label: 'Pays', icon: GlobeAltIcon },
  { value: 'province', label: 'Province/État', icon: MapIcon },
  { value: 'city', label: 'Ville', icon: BuildingOfficeIcon },
  { value: 'district', label: 'District/Commune', icon: BuildingOfficeIcon },
  { value: 'neighborhood', label: 'Quartier', icon: HomeIcon },
]

export default function LocationManagementPage() {
  const [selectedType, setSelectedType] = useState<LocationType>('country')
  const [selectedParent, setSelectedParent] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [editingLocation, setEditingLocation] = useState<Location | null>(null)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [deletingLocation, setDeletingLocation] = useState<Location | null>(null)

  const { data: locations = [], isLoading, refetch } = useGetLocationsQuery({
    type: selectedType,
    parent_id: selectedParent,
    search: searchQuery || undefined,
  })

  const { data: locationTree = [] } = useGetLocationTreeQuery()

  const [createLocation] = useCreateLocationMutation()
  const [updateLocation] = useUpdateLocationMutation()
  const [deleteLocation] = useDeleteLocationMutation()
  const [toggleVisibility] = useToggleLocationVisibilityMutation()

  // Form state
  const [formData, setFormData] = useState<LocationCreate>({
    name: '',
    type: 'country',
    parent_id: null,
    is_visible: true,
    phone_code: '',
  })

  const resetForm = () => {
    setFormData({
      name: '',
      type: 'country',
      parent_id: null,
      is_visible: true,
      phone_code: '',
    })
  }

  const handleCreate = async () => {
    if (!formData.name.trim()) {
      toast.error('Le nom est requis')
      return
    }

    try {
      await createLocation(formData).unwrap()
      toast.success('Location créée avec succès')
      setShowCreateModal(false)
      resetForm()
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la création')
    }
  }

  const handleEdit = async () => {
    if (!editingLocation) return

    try {
      await updateLocation({
        id: editingLocation.id,
        data: {
          name: formData.name,
          phone_code: formData.phone_code,
          is_visible: formData.is_visible,
        },
      }).unwrap()
      toast.success('Location mise à jour avec succès')
      setShowEditModal(false)
      setEditingLocation(null)
      resetForm()
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la mise à jour')
    }
  }

  const handleDelete = async () => {
    if (!deletingLocation) return

    try {
      await deleteLocation(deletingLocation.id).unwrap()
      toast.success('Location supprimée avec succès')
      setShowDeleteConfirm(false)
      setDeletingLocation(null)
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la suppression')
    }
  }

  const handleToggleVisibility = async (location: Location) => {
    try {
      await toggleVisibility({
        id: location.id,
        is_visible: !location.is_visible,
      }).unwrap()
      toast.success(
        location.is_visible
          ? 'Location masquée'
          : 'Location visible'
      )
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur')
    }
  }

  const openEditModal = (location: Location) => {
    setEditingLocation(location)
    setFormData({
      name: location.name,
      type: location.type,
      parent_id: location.parent_id,
      is_visible: location.is_visible,
      phone_code: location.phone_code || '',
    })
    setShowEditModal(true)
  }

  const openDeleteConfirm = (location: Location) => {
    setDeletingLocation(location)
    setShowDeleteConfirm(true)
  }

  // Get parent locations based on selected type
  const getParentLocations = () => {
    const typeOrder: LocationType[] = ['country', 'province', 'city', 'district', 'neighborhood']
    const currentIndex = typeOrder.indexOf(formData.type)
    
    if (currentIndex === 0) return [] // Countries have no parent
    
    const parentType = typeOrder[currentIndex - 1]
    return locations.filter(loc => loc.type === parentType)
  }

  if (isLoading) {
    return (
      <Layout>
        <div className="flex justify-center items-center py-12">
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
            <h1 className="text-3xl font-bold text-gray-900">Gestion des Localisations</h1>
            <p className="text-gray-600 mt-2">
              Gérez les pays, provinces, villes, districts et quartiers
            </p>
          </div>
          <button
            onClick={() => {
              resetForm()
              setFormData({ ...formData, type: selectedType })
              setShowCreateModal(true)
            }}
            className="flex items-center px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 transition"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Nouvelle Location
          </button>
        </div>

        {/* Type Filter Tabs */}
        <div className="bg-white rounded-lg shadow">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
              {LOCATION_TYPES.map((type) => {
                const Icon = type.icon
                return (
                  <button
                    key={type.value}
                    onClick={() => {
                      setSelectedType(type.value)
                      setSelectedParent(null)
                    }}
                    className={`group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm ${
                      selectedType === type.value
                        ? 'border-jlc-purple-600 text-jlc-purple-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <Icon
                      className={`-ml-0.5 mr-2 h-5 w-5 ${
                        selectedType === type.value
                          ? 'text-jlc-purple-600'
                          : 'text-gray-400 group-hover:text-gray-500'
                      }`}
                    />
                    {type.label}
                  </button>
                )
              })}
            </nav>
          </div>

          {/* Search */}
          <div className="p-4 border-b border-gray-200">
            <input
              type="text"
              placeholder="Rechercher..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
            />
          </div>

          {/* Locations List */}
          <div className="divide-y divide-gray-200">
            {locations.length === 0 ? (
              <div className="text-center py-12">
                <GlobeAltIcon className="mx-auto h-12 w-12 text-gray-400" />
                <p className="mt-2 text-gray-600">
                  Aucune location trouvée
                </p>
              </div>
            ) : (
              locations.map((location) => (
                <div
                  key={location.id}
                  className="p-4 hover:bg-gray-50 transition flex items-center justify-between"
                >
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {location.name}
                      </h3>
                      {location.dial_code && (
                        <span className="text-sm text-gray-500">
                          ({location.dial_code})
                        </span>
                      )}
                      {!location.is_visible && (
                        <span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800">
                          <EyeSlashIcon className="h-3 w-3 mr-1" />
                          Masqué
                        </span>
                      )}
                      {location.is_required && (
                        <span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                          Requis
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-500 mt-1">
                      Type: {LOCATION_TYPES.find(t => t.value === location.type)?.label}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      Créé le {new Date(location.created_at).toLocaleDateString('fr-FR')}
                    </p>
                  </div>

                  <ActionButtonGroup>
                    <ActionButton
                      type="custom"
                      onClick={() => handleToggleVisibility(location)}
                      icon={location.is_visible ? EyeSlashIcon : EyeIcon}
                      label={location.is_visible ? 'Masquer' : 'Afficher'}
                    />
                    <ActionButton
                      type="edit"
                      onClick={() => openEditModal(location)}
                    />
                    <ActionButton
                      type="delete"
                      onClick={() => openDeleteConfirm(location)}
                    />
                  </ActionButtonGroup>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Create Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => {
          setShowCreateModal(false)
          resetForm()
        }}
      >
        <div className="p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">
            Créer une Nouvelle Location
          </h3>

          <div className="space-y-4">
            {/* Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Type *
              </label>
              <select
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value as LocationType })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
              >
                {LOCATION_TYPES.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Parent (if not country) */}
            {formData.type !== 'country' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Parent
                </label>
                <select
                  value={formData.parent_id || ''}
                  onChange={(e) => setFormData({ ...formData, parent_id: e.target.value || null })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                >
                  <option value="">-- Sélectionner --</option>
                  {getParentLocations().map((loc) => (
                    <option key={loc.id} value={loc.id}>
                      {loc.name}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nom *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                placeholder="Ex: Gabon, Libreville, etc."
              />
            </div>

            {/* Dial Code (for countries only) */}
            {formData.type === 'country' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Code téléphonique
                </label>
                <input
                  type="text"
                  value={formData.dial_code}
                  onChange={(e) => setFormData({ ...formData, dial_code: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                  placeholder="Ex: +241"
                />
              </div>
            )}

            {/* Visibility */}
            <div className="flex items-center">
              <input
                type="checkbox"
                id="is_visible"
                checked={formData.is_visible}
                onChange={(e) => setFormData({ ...formData, is_visible: e.target.checked })}
                className="h-4 w-4 text-jlc-purple-600 focus:ring-jlc-purple-500 border-gray-300 rounded"
              />
              <label htmlFor="is_visible" className="ml-2 block text-sm text-gray-900">
                Visible pour les utilisateurs
              </label>
            </div>
          </div>

          <div className="flex space-x-3 mt-6">
            <button
              onClick={() => {
                setShowCreateModal(false)
                resetForm()
              }}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
            >
              Annuler
            </button>
            <button
              onClick={handleCreate}
              className="flex-1 bg-jlc-purple-600 text-white px-4 py-2 rounded-lg hover:bg-jlc-purple-700 transition"
            >
              Créer
            </button>
          </div>
        </div>
      </Modal>

      {/* Edit Modal */}
      <Modal
        isOpen={showEditModal}
        onClose={() => {
          setShowEditModal(false)
          setEditingLocation(null)
          resetForm()
        }}
      >
        <div className="p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">
            Modifier la Location
          </h3>

          <div className="space-y-4">
            {/* Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nom *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
              />
            </div>

            {/* Dial Code (for countries only) */}
            {editingLocation?.type === 'country' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Code téléphonique
                </label>
                <input
                  type="text"
                  value={formData.dial_code}
                  onChange={(e) => setFormData({ ...formData, dial_code: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                  placeholder="Ex: +241"
                />
              </div>
            )}

            {/* Visibility */}
            <div className="flex items-center">
              <input
                type="checkbox"
                id="edit_is_visible"
                checked={formData.is_visible}
                onChange={(e) => setFormData({ ...formData, is_visible: e.target.checked })}
                className="h-4 w-4 text-jlc-purple-600 focus:ring-jlc-purple-500 border-gray-300 rounded"
              />
              <label htmlFor="edit_is_visible" className="ml-2 block text-sm text-gray-900">
                Visible pour les utilisateurs
              </label>
            </div>
          </div>

          <div className="flex space-x-3 mt-6">
            <button
              onClick={() => {
                setShowEditModal(false)
                setEditingLocation(null)
                resetForm()
              }}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
            >
              Annuler
            </button>
            <button
              onClick={handleEdit}
              className="flex-1 bg-jlc-purple-600 text-white px-4 py-2 rounded-lg hover:bg-jlc-purple-700 transition"
            >
              Mettre à jour
            </button>
          </div>
        </div>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={showDeleteConfirm}
        onClose={() => {
          setShowDeleteConfirm(false)
          setDeletingLocation(null)
        }}
      >
        <div className="p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">
            Confirmer la Suppression
          </h3>
          <p className="text-gray-600 mb-4">
            Êtes-vous sûr de vouloir supprimer <strong>{deletingLocation?.name}</strong> ?
          </p>
          <p className="text-sm text-orange-600 mb-4">
            ⚠️ Cette action est irréversible. Assurez-vous qu'aucune location enfant n'existe.
          </p>

          <div className="flex space-x-3">
            <button
              onClick={() => {
                setShowDeleteConfirm(false)
                setDeletingLocation(null)
              }}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
            >
              Annuler
            </button>
            <button
              onClick={handleDelete}
              className="flex-1 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition"
            >
              Supprimer
            </button>
          </div>
        </div>
      </Modal>
    </Layout>
  )
}
