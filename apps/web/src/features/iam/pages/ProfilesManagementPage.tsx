import React, { useState } from 'react'
import { 
  useListProfilesQuery, 
  useListPermissionsQuery,
  useCreateProfileMutation,
  useUpdateProfileMutation,
  useDeleteProfileMutation,
  Profile,
  Permission
} from '../api/iamApi'
import Modal from '@/components/Modal'
import { toast } from 'react-hot-toast'

const ProfilesManagementPage: React.FC = () => {
  const { data: profiles, isLoading: profilesLoading } = useListProfilesQuery()
  const { data: permissions, isLoading: permissionsLoading } = useListPermissionsQuery()
  const [createProfile] = useCreateProfileMutation()
  const [updateProfile] = useUpdateProfileMutation()
  const [deleteProfile] = useDeleteProfileMutation()

  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [selectedProfile, setSelectedProfile] = useState<Profile | null>(null)

  const [formData, setFormData] = useState({
    code: '',
    name: '',
    description: '',
    permission_ids: [] as string[],
    category: 'custom',
    color: '#6366F1',
    icon: 'shield'
  })

  const resetForm = () => {
    setFormData({
      code: '',
      name: '',
      description: '',
      permission_ids: [],
      category: 'custom',
      color: '#6366F1',
      icon: 'shield'
    })
  }

  const handleCreateClick = () => {
    resetForm()
    setShowCreateModal(true)
  }

  const handleEditClick = (profile: Profile) => {
    setSelectedProfile(profile)
    setFormData({
      code: profile.code,
      name: profile.name,
      description: profile.description || '',
      permission_ids: profile.permission_ids,
      category: profile.category,
      color: profile.color || '#6366F1',
      icon: profile.icon || 'shield'
    })
    setShowEditModal(true)
  }

  const handleDeleteClick = (profile: Profile) => {
    setSelectedProfile(profile)
    setShowDeleteModal(true)
  }

  const handleCreateSubmit = async () => {
    try {
      await createProfile(formData).unwrap()
      toast.success('Profil créé avec succès')
      setShowCreateModal(false)
      resetForm()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la création du profil')
    }
  }

  const handleEditSubmit = async () => {
    if (!selectedProfile) return
    
    try {
      await updateProfile({
        id: selectedProfile.id,
        data: {
          name: formData.name,
          description: formData.description,
          permission_ids: formData.permission_ids,
          color: formData.color,
          icon: formData.icon
        }
      }).unwrap()
      toast.success('Profil mis à jour avec succès')
      setShowEditModal(false)
      setSelectedProfile(null)
      resetForm()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la mise à jour du profil')
    }
  }

  const handleDeleteConfirm = async () => {
    if (!selectedProfile) return
    
    try {
      await deleteProfile(selectedProfile.id).unwrap()
      toast.success('Profil supprimé avec succès')
      setShowDeleteModal(false)
      setSelectedProfile(null)
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la suppression du profil')
    }
  }

  const togglePermission = (permissionId: string) => {
    setFormData(prev => ({
      ...prev,
      permission_ids: prev.permission_ids.includes(permissionId)
        ? prev.permission_ids.filter(id => id !== permissionId)
        : [...prev.permission_ids, permissionId]
    }))
  }

  // Group permissions by category
  const groupedPermissions = React.useMemo(() => {
    if (!permissions) return {}
    
    return permissions.reduce((acc, permission) => {
      const category = permission.category || 'other'
      if (!acc[category]) {
        acc[category] = []
      }
      acc[category].push(permission)
      return acc
    }, {} as Record<string, Permission[]>)
  }, [permissions])

  if (profilesLoading || permissionsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestion des Profils</h1>
          <p className="text-gray-600 mt-1">Gérer les profils et leurs permissions</p>
        </div>
        <button
          onClick={handleCreateClick}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
        >
          + Nouveau Profil
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {profiles?.map((profile) => (
          <div
            key={profile.id}
            className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center">
                <div 
                  className="w-12 h-12 rounded-lg flex items-center justify-center text-white font-bold text-xl"
                  style={{ backgroundColor: profile.color || '#6366F1' }}
                >
                  {profile.icon === 'shield' ? '🛡️' : '⭐'}
                </div>
                <div className="ml-3">
                  <h3 className="font-semibold text-gray-900">{profile.name}</h3>
                  <p className="text-sm text-gray-500">{profile.code}</p>
                </div>
              </div>
              {profile.is_system_role && (
                <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                  Système
                </span>
              )}
            </div>

            <p className="text-sm text-gray-600 mb-4 line-clamp-2">
              {profile.description || 'Aucune description'}
            </p>

            <div className="flex items-center justify-between mb-4">
              <span className="text-sm text-gray-500">
                {profile.permission_ids.length} permission(s)
              </span>
              <span className={`px-2 py-1 text-xs rounded-full ${
                profile.category === 'system' ? 'bg-purple-100 text-purple-800' :
                profile.category === 'department' ? 'bg-green-100 text-green-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {profile.category}
              </span>
            </div>

            {!profile.is_protected && (
              <div className="flex gap-2">
                <button
                  onClick={() => handleEditClick(profile)}
                  className="flex-1 px-3 py-2 bg-blue-50 text-blue-600 rounded hover:bg-blue-100 transition-colors text-sm"
                >
                  Modifier
                </button>
                <button
                  onClick={() => handleDeleteClick(profile)}
                  className="flex-1 px-3 py-2 bg-red-50 text-red-600 rounded hover:bg-red-100 transition-colors text-sm"
                >
                  Supprimer
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Create Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => {
          setShowCreateModal(false)
          resetForm()
        }}
        title="Créer un Profil"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Code *
            </label>
            <input
              type="text"
              value={formData.code}
              onChange={(e) => setFormData({ ...formData, code: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              placeholder="ex: manager_rh"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nom *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              placeholder="ex: Manager RH"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              rows={3}
              placeholder="Description du profil..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Couleur
              </label>
              <input
                type="color"
                value={formData.color}
                onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                className="w-full h-10 border border-gray-300 rounded-lg"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Catégorie
              </label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              >
                <option value="custom">Personnalisé</option>
                <option value="department">Département</option>
                <option value="project">Projet</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Permissions ({formData.permission_ids.length} sélectionnée(s))
            </label>
            <div className="max-h-64 overflow-y-auto border border-gray-300 rounded-lg p-3 space-y-3">
              {Object.entries(groupedPermissions).map(([category, perms]) => (
                <div key={category}>
                  <h4 className="font-medium text-gray-700 text-sm mb-2 capitalize">
                    {category}
                  </h4>
                  <div className="space-y-2 ml-2">
                    {perms.map((permission) => (
                      <label key={permission.id} className="flex items-start cursor-pointer">
                        <input
                          type="checkbox"
                          checked={formData.permission_ids.includes(permission.id)}
                          onChange={() => togglePermission(permission.id)}
                          className="mt-1 mr-2"
                        />
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {permission.name}
                          </div>
                          <div className="text-xs text-gray-500">
                            {permission.description}
                          </div>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              onClick={() => {
                setShowCreateModal(false)
                resetForm()
              }}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Annuler
            </button>
            <button
              onClick={handleCreateSubmit}
              disabled={!formData.code || !formData.name}
              className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
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
          setSelectedProfile(null)
          resetForm()
        }}
        title="Modifier le Profil"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Code
            </label>
            <input
              type="text"
              value={formData.code}
              disabled
              className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 cursor-not-allowed"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nom *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              rows={3}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Couleur
              </label>
              <input
                type="color"
                value={formData.color}
                onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                className="w-full h-10 border border-gray-300 rounded-lg"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Permissions ({formData.permission_ids.length} sélectionnée(s))
            </label>
            <div className="max-h-64 overflow-y-auto border border-gray-300 rounded-lg p-3 space-y-3">
              {Object.entries(groupedPermissions).map(([category, perms]) => (
                <div key={category}>
                  <h4 className="font-medium text-gray-700 text-sm mb-2 capitalize">
                    {category}
                  </h4>
                  <div className="space-y-2 ml-2">
                    {perms.map((permission) => (
                      <label key={permission.id} className="flex items-start cursor-pointer">
                        <input
                          type="checkbox"
                          checked={formData.permission_ids.includes(permission.id)}
                          onChange={() => togglePermission(permission.id)}
                          className="mt-1 mr-2"
                        />
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {permission.name}
                          </div>
                          <div className="text-xs text-gray-500">
                            {permission.description}
                          </div>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              onClick={() => {
                setShowEditModal(false)
                setSelectedProfile(null)
                resetForm()
              }}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Annuler
            </button>
            <button
              onClick={handleEditSubmit}
              disabled={!formData.name}
              className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              Mettre à jour
            </button>
          </div>
        </div>
      </Modal>

      {/* Delete Modal */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => {
          setShowDeleteModal(false)
          setSelectedProfile(null)
        }}
        title="Supprimer le Profil"
      >
        <div className="space-y-4">
          <p className="text-gray-700">
            Êtes-vous sûr de vouloir supprimer le profil{' '}
            <span className="font-semibold">{selectedProfile?.name}</span> ?
          </p>
          <p className="text-sm text-red-600">
            Cette action est irréversible et supprimera toutes les associations avec ce profil.
          </p>

          <div className="flex gap-3 pt-4">
            <button
              onClick={() => {
                setShowDeleteModal(false)
                setSelectedProfile(null)
              }}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Annuler
            </button>
            <button
              onClick={handleDeleteConfirm}
              className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              Supprimer
            </button>
          </div>
        </div>
      </Modal>
    </div>
  )
}

export default ProfilesManagementPage
