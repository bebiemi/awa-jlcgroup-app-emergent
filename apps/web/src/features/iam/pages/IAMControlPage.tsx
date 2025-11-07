import React, { useState } from 'react'
import {
  useListGroupsQuery,
  useListProfilesQuery,
  useListPermissionsQuery,
  useCreateGroupMutation,
  useUpdateGroupMutation,
  useDeleteGroupMutation,
  Group,
  Profile,
  Permission
} from '../api/iamApi'
import Modal from '@/components/Modal'
import { toast } from 'react-hot-toast'

type TabType = 'groups' | 'permissions'

const IAMControlPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('groups')
  
  const { data: groups, isLoading: groupsLoading } = useListGroupsQuery()
  const { data: profiles, isLoading: profilesLoading } = useListProfilesQuery()
  const { data: permissions, isLoading: permissionsLoading } = useListPermissionsQuery()
  
  const [createGroup] = useCreateGroupMutation()
  const [updateGroup] = useUpdateGroupMutation()
  const [deleteGroup] = useDeleteGroupMutation()

  const [showCreateGroupModal, setShowCreateGroupModal] = useState(false)
  const [showEditGroupModal, setShowEditGroupModal] = useState(false)
  const [showDeleteGroupModal, setShowDeleteGroupModal] = useState(false)
  const [selectedGroup, setSelectedGroup] = useState<Group | null>(null)

  const [groupFormData, setGroupFormData] = useState({
    code: '',
    name: '',
    description: '',
    profile_ids: [] as string[],
    parent_group_id: ''
  })

  const resetGroupForm = () => {
    setGroupFormData({
      code: '',
      name: '',
      description: '',
      profile_ids: [],
      parent_group_id: ''
    })
  }

  const handleCreateGroupClick = () => {
    resetGroupForm()
    setShowCreateGroupModal(true)
  }

  const handleEditGroupClick = (group: Group) => {
    setSelectedGroup(group)
    setGroupFormData({
      code: group.code,
      name: group.name,
      description: group.description || '',
      profile_ids: group.profile_ids,
      parent_group_id: group.parent_group_id || ''
    })
    setShowEditGroupModal(true)
  }

  const handleDeleteGroupClick = (group: Group) => {
    setSelectedGroup(group)
    setShowDeleteGroupModal(true)
  }

  const handleCreateGroupSubmit = async () => {
    try {
      await createGroup({
        code: groupFormData.code,
        name: groupFormData.name,
        description: groupFormData.description || undefined,
        profile_ids: groupFormData.profile_ids,
        parent_group_id: groupFormData.parent_group_id || undefined
      }).unwrap()
      toast.success('Groupe créé avec succès')
      setShowCreateGroupModal(false)
      resetGroupForm()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la création du groupe')
    }
  }

  const handleEditGroupSubmit = async () => {
    if (!selectedGroup) return
    
    try {
      await updateGroup({
        id: selectedGroup.id,
        data: {
          name: groupFormData.name,
          description: groupFormData.description || undefined,
          profile_ids: groupFormData.profile_ids,
          parent_group_id: groupFormData.parent_group_id || undefined
        }
      }).unwrap()
      toast.success('Groupe mis à jour avec succès')
      setShowEditGroupModal(false)
      setSelectedGroup(null)
      resetGroupForm()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la mise à jour du groupe')
    }
  }

  const handleDeleteGroupConfirm = async () => {
    if (!selectedGroup) return
    
    try {
      await deleteGroup(selectedGroup.id).unwrap()
      toast.success('Groupe supprimé avec succès')
      setShowDeleteGroupModal(false)
      setSelectedGroup(null)
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la suppression du groupe')
    }
  }

  const toggleProfile = (profileId: string) => {
    setGroupFormData(prev => ({
      ...prev,
      profile_ids: prev.profile_ids.includes(profileId)
        ? prev.profile_ids.filter(id => id !== profileId)
        : [...prev.profile_ids, profileId]
    }))
  }

  const getProfileName = (profileId: string) => {
    return profiles?.find(p => p.id === profileId)?.name || profileId
  }

  const getGroupName = (groupId: string) => {
    return groups?.find(g => g.id === groupId)?.name || groupId
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

  const isLoading = groupsLoading || profilesLoading || permissionsLoading

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Contrôle d'Accès (IAM)</h1>
        <p className="text-gray-600 mt-1">Gérer les groupes et permissions du système</p>
      </div>

      {/* Tabs */}
      <div className="mb-6 border-b border-gray-200">
        <nav className="flex space-x-8">
          <button
            onClick={() => setActiveTab('groups')}
            className={`pb-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'groups'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Groupes ({groups?.length || 0})
          </button>
          <button
            onClick={() => setActiveTab('permissions')}
            className={`pb-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'permissions'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Permissions ({permissions?.length || 0})
          </button>
        </nav>
      </div>

      {/* Groups Tab */}
      {activeTab === 'groups' && (
        <>
          <div className="mb-4 flex justify-end">
            <button
              onClick={handleCreateGroupClick}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              + Nouveau Groupe
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {groups?.map((group) => (
              <div
                key={group.id}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="font-semibold text-gray-900 text-lg">{group.name}</h3>
                    <p className="text-sm text-gray-500">{group.code}</p>
                  </div>
                  {group.is_system_group && (
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                      Système
                    </span>
                  )}
                </div>

                <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                  {group.description || 'Aucune description'}
                </p>

                <div className="space-y-2 mb-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Profils:</span>
                    <span className="font-medium text-gray-900">
                      {group.profile_ids.length}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Utilisateurs:</span>
                    <span className="font-medium text-gray-900">
                      {group.user_ids.length}
                    </span>
                  </div>
                  {group.parent_group_id && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-500">Groupe parent:</span>
                      <span className="font-medium text-gray-900 text-xs truncate">
                        {getGroupName(group.parent_group_id)}
                      </span>
                    </div>
                  )}
                </div>

                {/* Profile badges */}
                {group.profile_ids.length > 0 && (
                  <div className="mb-4">
                    <div className="flex flex-wrap gap-1">
                      {group.profile_ids.slice(0, 3).map((profileId) => (
                        <span
                          key={profileId}
                          className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full"
                        >
                          {getProfileName(profileId)}
                        </span>
                      ))}
                      {group.profile_ids.length > 3 && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                          +{group.profile_ids.length - 3}
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {!group.is_protected && (
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleEditGroupClick(group)}
                      className="flex-1 px-3 py-2 bg-blue-50 text-blue-600 rounded hover:bg-blue-100 transition-colors text-sm"
                    >
                      Modifier
                    </button>
                    <button
                      onClick={() => handleDeleteGroupClick(group)}
                      className="flex-1 px-3 py-2 bg-red-50 text-red-600 rounded hover:bg-red-100 transition-colors text-sm"
                    >
                      Supprimer
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </>
      )}

      {/* Permissions Tab */}
      {activeTab === 'permissions' && (
        <div className="space-y-6">
          {Object.entries(groupedPermissions).map(([category, perms]) => (
            <div key={category} className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 capitalize">
                {category} ({perms.length})
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {perms.map((permission) => (
                  <div
                    key={permission.id}
                    className="border border-gray-200 rounded-lg p-4 hover:border-indigo-300 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="font-medium text-gray-900 text-sm">
                        {permission.name}
                      </div>
                      {permission.is_system && (
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                          Système
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-gray-600 mb-3">
                      {permission.description}
                    </div>
                    <div className="flex flex-wrap gap-1">
                      <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                        {permission.resource}
                      </span>
                      <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                        {permission.action}
                      </span>
                      <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded">
                        {permission.scope}
                      </span>
                    </div>
                    <div className="mt-2 text-xs text-gray-500">
                      Code: <code className="bg-gray-100 px-1 rounded">{permission.code}</code>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Group Modal */}
      <Modal
        isOpen={showCreateGroupModal}
        onClose={() => {
          setShowCreateGroupModal(false)
          resetGroupForm()
        }}
        title="Créer un Groupe"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Code *
            </label>
            <input
              type="text"
              value={groupFormData.code}
              onChange={(e) => setGroupFormData({ ...groupFormData, code: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              placeholder="ex: equipe_rh"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nom *
            </label>
            <input
              type="text"
              value={groupFormData.name}
              onChange={(e) => setGroupFormData({ ...groupFormData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              placeholder="ex: Équipe RH"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={groupFormData.description}
              onChange={(e) => setGroupFormData({ ...groupFormData, description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              rows={3}
              placeholder="Description du groupe..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Groupe Parent (optionnel)
            </label>
            <select
              value={groupFormData.parent_group_id}
              onChange={(e) => setGroupFormData({ ...groupFormData, parent_group_id: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">Aucun</option>
              {groups?.filter(g => !g.is_protected).map((group) => (
                <option key={group.id} value={group.id}>
                  {group.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Profils ({groupFormData.profile_ids.length} sélectionné(s))
            </label>
            <div className="max-h-64 overflow-y-auto border border-gray-300 rounded-lg p-3 space-y-2">
              {profiles?.map((profile) => (
                <label key={profile.id} className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={groupFormData.profile_ids.includes(profile.id)}
                    onChange={() => toggleProfile(profile.id)}
                    className="mr-2"
                  />
                  <div className="flex items-center">
                    <div
                      className="w-6 h-6 rounded flex items-center justify-center text-white text-xs mr-2"
                      style={{ backgroundColor: profile.color || '#6366F1' }}
                    >
                      {profile.icon === 'shield' ? '🛡️' : '⭐'}
                    </div>
                    <span className="text-sm text-gray-900">{profile.name}</span>
                    {profile.is_system_role && (
                      <span className="ml-2 px-2 py-0.5 bg-blue-100 text-blue-800 text-xs rounded-full">
                        Système
                      </span>
                    )}
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              onClick={() => {
                setShowCreateGroupModal(false)
                resetGroupForm()
              }}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Annuler
            </button>
            <button
              onClick={handleCreateGroupSubmit}
              disabled={!groupFormData.code || !groupFormData.name}
              className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              Créer
            </button>
          </div>
        </div>
      </Modal>

      {/* Edit Group Modal */}
      <Modal
        isOpen={showEditGroupModal}
        onClose={() => {
          setShowEditGroupModal(false)
          setSelectedGroup(null)
          resetGroupForm()
        }}
        title="Modifier le Groupe"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Code
            </label>
            <input
              type="text"
              value={groupFormData.code}
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
              value={groupFormData.name}
              onChange={(e) => setGroupFormData({ ...groupFormData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={groupFormData.description}
              onChange={(e) => setGroupFormData({ ...groupFormData, description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              rows={3}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Groupe Parent (optionnel)
            </label>
            <select
              value={groupFormData.parent_group_id}
              onChange={(e) => setGroupFormData({ ...groupFormData, parent_group_id: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">Aucun</option>
              {groups?.filter(g => !g.is_protected && g.id !== selectedGroup?.id).map((group) => (
                <option key={group.id} value={group.id}>
                  {group.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Profils ({groupFormData.profile_ids.length} sélectionné(s))
            </label>
            <div className="max-h-64 overflow-y-auto border border-gray-300 rounded-lg p-3 space-y-2">
              {profiles?.map((profile) => (
                <label key={profile.id} className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={groupFormData.profile_ids.includes(profile.id)}
                    onChange={() => toggleProfile(profile.id)}
                    className="mr-2"
                  />
                  <div className="flex items-center">
                    <div
                      className="w-6 h-6 rounded flex items-center justify-center text-white text-xs mr-2"
                      style={{ backgroundColor: profile.color || '#6366F1' }}
                    >
                      {profile.icon === 'shield' ? '🛡️' : '⭐'}
                    </div>
                    <span className="text-sm text-gray-900">{profile.name}</span>
                    {profile.is_system_role && (
                      <span className="ml-2 px-2 py-0.5 bg-blue-100 text-blue-800 text-xs rounded-full">
                        Système
                      </span>
                    )}
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              onClick={() => {
                setShowEditGroupModal(false)
                setSelectedGroup(null)
                resetGroupForm()
              }}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Annuler
            </button>
            <button
              onClick={handleEditGroupSubmit}
              disabled={!groupFormData.name}
              className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              Mettre à jour
            </button>
          </div>
        </div>
      </Modal>

      {/* Delete Group Modal */}
      <Modal
        isOpen={showDeleteGroupModal}
        onClose={() => {
          setShowDeleteGroupModal(false)
          setSelectedGroup(null)
        }}
        title="Supprimer le Groupe"
      >
        <div className="space-y-4">
          <p className="text-gray-700">
            Êtes-vous sûr de vouloir supprimer le groupe{' '}
            <span className="font-semibold">{selectedGroup?.name}</span> ?
          </p>
          <p className="text-sm text-red-600">
            Cette action est irréversible et supprimera toutes les associations avec ce groupe.
          </p>

          <div className="flex gap-3 pt-4">
            <button
              onClick={() => {
                setShowDeleteGroupModal(false)
                setSelectedGroup(null)
              }}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Annuler
            </button>
            <button
              onClick={handleDeleteGroupConfirm}
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

export default IAMControlPage
