import React, { useState } from 'react'
import { 
  useListGroupsQuery, 
  useDeleteGroupMutation,
  Group,
} from '../api/iamApi'
import Layout from '@/components/Layout'
import Card from '@/components/Card'
import Modal from '@/components/Modal'
import Tooltip from '@/components/Tooltip'
import { toast } from 'react-hot-toast'
import { PlusIcon, UsersIcon } from '@heroicons/react/24/outline'
import CreateGroupModal from '../components/CreateGroupModal'
import EditGroupModal from '../components/EditGroupModal'

const GroupsManagementPage: React.FC = () => {
  const { data: groups, isLoading: groupsLoading } = useListGroupsQuery()
  const [deleteGroup] = useDeleteGroupMutation()

  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [selectedGroup, setSelectedGroup] = useState<Group | null>(null)

  const handleCreateClick = () => {
    setShowCreateModal(true)
  }

  const handleEditClick = (group: Group) => {
    setSelectedGroup(group)
    setShowEditModal(true)
  }

  const handleDeleteClick = (group: Group) => {
    setSelectedGroup(group)
    setShowDeleteModal(true)
  }

  const handleDeleteConfirm = async () => {
    if (!selectedGroup) return
    
    try {
      await deleteGroup(selectedGroup.id).unwrap()
      toast.success('Groupe supprimé avec succès')
      setShowDeleteModal(false)
      setSelectedGroup(null)
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la suppression du groupe')
    }
  }

  if (groupsLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
        </div>
      </Layout>
    )
  }

  // Statistics
  const stats = {
    total: groups?.length || 0,
    system: groups?.filter(g => g.is_system_group === true).length || 0,
    withProfiles: groups?.filter(g => g.profile_ids?.length > 0).length || 0,
    withMembers: groups?.filter(g => g.user_ids?.length > 0).length || 0,
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Gestion des Groupes</h1>
            <p className="text-gray-600 mt-1">Gérer les groupes et leurs membres</p>
          </div>
          <button
            onClick={handleCreateClick}
            className="flex items-center gap-2 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 transition-colors shadow-md hover:shadow-lg"
          >
            <PlusIcon className="h-5 w-5" />
            Nouveau Groupe
          </button>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Tooltip content="Nombre total de groupes créés" position="top">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-base font-medium text-gray-600 mb-2">Total Groupes</p>
                  <p className="text-4xl font-bold text-gray-900">{stats.total}</p>
                </div>
                <div className="text-5xl">👥</div>
              </div>
            </Card>
          </Tooltip>
          <Tooltip content="Groupes système protégés" position="top">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-base font-medium text-gray-600 mb-2">Système</p>
                  <p className="text-4xl font-bold text-blue-600">{stats.system}</p>
                </div>
                <div className="text-5xl">🛡️</div>
              </div>
            </Card>
          </Tooltip>
          <Tooltip content="Groupes avec profils assignés" position="top">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-base font-medium text-gray-600 mb-2">Avec Profils</p>
                  <p className="text-4xl font-bold text-green-600">{stats.withProfiles}</p>
                </div>
                <div className="text-5xl">📋</div>
              </div>
            </Card>
          </Tooltip>
          <Tooltip content="Groupes avec membres" position="top">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-base font-medium text-gray-600 mb-2">Avec Membres</p>
                  <p className="text-4xl font-bold text-jlc-purple-600">{stats.withMembers}</p>
                </div>
                <div className="text-5xl">👤</div>
              </div>
            </Card>
          </Tooltip>
        </div>

        {/* Groups Grid */}
        <Card>
          {!groups || groups.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">👥</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Aucun groupe</h3>
              <p className="text-gray-500 mb-4">
                Créez votre premier groupe pour organiser les utilisateurs.
              </p>
              <button
                onClick={handleCreateClick}
                className="inline-flex items-center gap-2 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700"
              >
                <PlusIcon className="h-5 w-5" />
                Créer le premier groupe
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {groups.map((group) => (
                <div
                  key={group.id}
                  className="bg-gradient-to-br from-white to-gray-50 rounded-lg p-6 hover:shadow-xl transition-all duration-300 hover:scale-105 cursor-pointer border border-gray-200"
                  onClick={() => !group.is_protected && handleEditClick(group)}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-lg bg-jlc-purple-600 flex items-center justify-center text-white font-bold text-2xl shadow-md">
                        <UsersIcon className="h-6 w-6" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{group.name}</h3>
                        <p className="text-sm text-gray-500">{group.code}</p>
                      </div>
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
                      <span className="text-gray-500">Profils :</span>
                      <span className="font-medium text-gray-700">
                        {group.profile_ids?.length || 0}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-500">Membres :</span>
                      <span className="font-medium text-gray-700">
                        {group.user_ids?.length || 0}
                      </span>
                    </div>
                  </div>

                  {!group.is_protected && (
                    <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
                      <button
                        onClick={() => handleEditClick(group)}
                        className="flex-1 px-3 py-2 bg-blue-50 text-blue-600 rounded hover:bg-blue-100 transition-colors text-sm font-medium"
                      >
                        Modifier
                      </button>
                      <button
                        onClick={() => handleDeleteClick(group)}
                        className="flex-1 px-3 py-2 bg-red-50 text-red-600 rounded hover:bg-red-100 transition-colors text-sm font-medium"
                      >
                        Supprimer
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      {/* Create Modal */}
      <CreateGroupModal 
        isOpen={showCreateModal} 
        onClose={() => setShowCreateModal(false)} 
      />

      {/* Edit Modal */}
      {selectedGroup && (
        <EditGroupModal 
          group={selectedGroup}
          isOpen={showEditModal} 
          onClose={() => {
            setShowEditModal(false)
            setSelectedGroup(null)
          }} 
        />
      )}

      {/* Delete Modal */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => {
          setShowDeleteModal(false)
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
            Cette action est irréversible. Les membres du groupe ne seront pas supprimés mais
            n'appartiendront plus à ce groupe.
          </p>

          <div className="flex gap-3 pt-4">
            <button
              onClick={() => {
                setShowDeleteModal(false)
                setSelectedGroup(null)
              }}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Annuler
            </button>
            <button
              onClick={handleDeleteConfirm}
              className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Supprimer
            </button>
          </div>
        </div>
      </Modal>
    </Layout>
  )
}

export default GroupsManagementPage
