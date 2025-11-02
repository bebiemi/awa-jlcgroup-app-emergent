import { useState } from 'react'
import Layout from '@/components/Layout'
import Card from '@/components/Card'
import {
  useGetGroupsQuery,
  useDeleteGroupMutation,
  type Group,
} from '../api/securityApi'
import {
  PlusIcon,
  PencilIcon,
  TrashIcon,
  UserGroupIcon,
  ShieldCheckIcon,
} from '@heroicons/react/24/outline'
import CreateGroupModal from '../components/CreateGroupModal'
import EditGroupModal from '../components/EditGroupModal'
import DeleteConfirmModal from '../components/DeleteConfirmModal'

export default function GroupsPage() {
  const { data: groups, isLoading } = useGetGroupsQuery()
  const [deleteGroup] = useDeleteGroupMutation()

  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingGroup, setEditingGroup] = useState<Group | null>(null)
  const [deletingGroup, setDeletingGroup] = useState<Group | null>(null)

  const handleDelete = async () => {
    if (deletingGroup) {
      try {
        await deleteGroup(deletingGroup.id).unwrap()
        setDeletingGroup(null)
      } catch (error) {
        console.error('Failed to delete group:', error)
      }
    }
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Gestion des Groupes</h1>
            <p className="mt-2 text-gray-600">
              Organisez les utilisateurs en groupes avec des profils de permissions
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 transition-colors"
          >
            <PlusIcon className="h-5 w-5" />
            Créer un groupe
          </button>
        </div>

        {/* Groups Grid */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
          </div>
        ) : groups && groups.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {groups.map((group) => (
              <Card key={group.id}>
                <div className="space-y-4">
                  {/* Header */}
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-3 bg-jlc-purple-100 rounded-lg">
                        <UserGroupIcon className="h-6 w-6 text-jlc-purple-600" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{group.name}</h3>
                        {group.description && (
                          <p className="text-sm text-gray-500 mt-1">{group.description}</p>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="flex items-center gap-4 pt-4 border-t border-gray-200">
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <UserGroupIcon className="h-4 w-4" />
                      <span>{group.member_ids.length} membre(s)</span>
                    </div>
                    {group.profile_id && (
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <ShieldCheckIcon className="h-4 w-4" />
                        <span>Profil assigné</span>
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 pt-4 border-t border-gray-200">
                    <button
                      onClick={() => setEditingGroup(group)}
                      className="flex-1 flex items-center justify-center gap-2 px-3 py-2 text-sm text-blue-600 border border-blue-300 rounded-lg hover:bg-blue-50 transition-colors"
                    >
                      <PencilIcon className="h-4 w-4" />
                      Modifier
                    </button>
                    <button
                      onClick={() => setDeletingGroup(group)}
                      className="flex-1 flex items-center justify-center gap-2 px-3 py-2 text-sm text-red-600 border border-red-300 rounded-lg hover:bg-red-50 transition-colors"
                    >
                      <TrashIcon className="h-4 w-4" />
                      Supprimer
                    </button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <Card>
            <div className="text-center py-12">
              <UserGroupIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">Aucun groupe</h3>
              <p className="mt-1 text-sm text-gray-500">
                Commencez par créer votre premier groupe
              </p>
              <div className="mt-6">
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-jlc-purple-600 hover:bg-jlc-purple-700"
                >
                  <PlusIcon className="h-5 w-5 mr-2" />
                  Créer un groupe
                </button>
              </div>
            </div>
          </Card>
        )}
      </div>

      {/* Modals */}
      <CreateGroupModal isOpen={showCreateModal} onClose={() => setShowCreateModal(false)} />
      {editingGroup && (
        <EditGroupModal
          group={editingGroup}
          isOpen={!!editingGroup}
          onClose={() => setEditingGroup(null)}
        />
      )}
      {deletingGroup && (
        <DeleteConfirmModal
          isOpen={!!deletingGroup}
          title="Supprimer le groupe"
          message={`Êtes-vous sûr de vouloir supprimer le groupe "${deletingGroup.name}" ? Cette action est irréversible.`}
          onConfirm={handleDelete}
          onClose={() => setDeletingGroup(null)}
        />
      )}
    </Layout>
  )
}
