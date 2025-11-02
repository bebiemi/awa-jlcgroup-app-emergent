import { useState } from 'react'
import Layout from '@/components/Layout'
import Card from '@/components/Card'
import {
  useGetProfilesQuery,
  useDeleteProfileMutation,
  type Profile,
} from '../api/securityApi'
import {
  PlusIcon,
  PencilIcon,
  TrashIcon,
  ShieldCheckIcon,
  LockClosedIcon,
} from '@heroicons/react/24/outline'
import CreateProfileModal from '../components/CreateProfileModal'
import EditProfileModal from '../components/EditProfileModal'
import DeleteConfirmModal from '../components/DeleteConfirmModal'

export default function ProfilesPage() {
  const { data: profiles, isLoading } = useGetProfilesQuery()
  const [deleteProfile] = useDeleteProfileMutation()

  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingProfile, setEditingProfile] = useState<Profile | null>(null)
  const [deletingProfile, setDeletingProfile] = useState<Profile | null>(null)

  const handleDelete = async () => {
    if (deletingProfile) {
      try {
        await deleteProfile(deletingProfile.id).unwrap()
        setDeletingProfile(null)
      } catch (error: any) {
        console.error('Failed to delete profile:', error)
        alert(error?.data?.detail || 'Erreur lors de la suppression')
      }
    }
  }

  const systemProfiles = profiles?.filter((p) => p.is_system) || []
  const customProfiles = profiles?.filter((p) => !p.is_system) || []

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Profils & Permissions</h1>
            <p className="mt-2 text-gray-600">
              Gérez les profils de permissions pour contrôler l'accès aux fonctionnalités
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 transition-colors"
          >
            <PlusIcon className="h-5 w-5" />
            Créer un profil
          </button>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
          </div>
        ) : (
          <>
            {/* System Profiles */}
            {systemProfiles.length > 0 && (
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <LockClosedIcon className="h-5 w-5 text-gray-500" />
                  Profils Système
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {systemProfiles.map((profile) => (
                    <Card key={profile.id}>
                      <div className="space-y-4">
                        {/* Header */}
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-3">
                            <div className="p-3 bg-indigo-100 rounded-lg">
                              <ShieldCheckIcon className="h-6 w-6 text-indigo-600" />
                            </div>
                            <div>
                              <div className="flex items-center gap-2">
                                <h3 className="text-lg font-semibold text-gray-900">
                                  {profile.name}
                                </h3>
                                <span className="px-2 py-0.5 bg-indigo-100 text-indigo-700 text-xs font-medium rounded">
                                  Système
                                </span>
                              </div>
                              {profile.description && (
                                <p className="text-sm text-gray-500 mt-1">{profile.description}</p>
                              )}
                            </div>
                          </div>
                        </div>

                        {/* Stats */}
                        <div className="flex items-center gap-2 pt-4 border-t border-gray-200 text-sm text-gray-600">
                          <ShieldCheckIcon className="h-4 w-4" />
                          <span>{profile.permissions.length} permission(s)</span>
                        </div>

                        {/* Actions */}
                        <div className="pt-4 border-t border-gray-200">
                          <button
                            onClick={() => setEditingProfile(profile)}
                            className="w-full flex items-center justify-center gap-2 px-3 py-2 text-sm text-blue-600 border border-blue-300 rounded-lg hover:bg-blue-50 transition-colors"
                          >
                            <PencilIcon className="h-4 w-4" />
                            Voir les détails
                          </button>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {/* Custom Profiles */}
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Profils Personnalisés
              </h2>
              {customProfiles.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {customProfiles.map((profile) => (
                    <Card key={profile.id}>
                      <div className="space-y-4">
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-3">
                            <div className="p-3 bg-jlc-purple-100 rounded-lg">
                              <ShieldCheckIcon className="h-6 w-6 text-jlc-purple-600" />
                            </div>
                            <div>
                              <h3 className="text-lg font-semibold text-gray-900">
                                {profile.name}
                              </h3>
                              {profile.description && (
                                <p className="text-sm text-gray-500 mt-1">{profile.description}</p>
                              )}
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center gap-2 pt-4 border-t border-gray-200 text-sm text-gray-600">
                          <ShieldCheckIcon className="h-4 w-4" />
                          <span>{profile.permissions.length} permission(s)</span>
                        </div>

                        <div className="flex gap-2 pt-4 border-t border-gray-200">
                          <button
                            onClick={() => setEditingProfile(profile)}
                            className="flex-1 flex items-center justify-center gap-2 px-3 py-2 text-sm text-blue-600 border border-blue-300 rounded-lg hover:bg-blue-50 transition-colors"
                          >
                            <PencilIcon className="h-4 w-4" />
                            Modifier
                          </button>
                          <button
                            onClick={() => setDeletingProfile(profile)}
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
                    <ShieldCheckIcon className="mx-auto h-12 w-12 text-gray-400" />
                    <h3 className="mt-2 text-sm font-medium text-gray-900">
                      Aucun profil personnalisé
                    </h3>
                    <p className="mt-1 text-sm text-gray-500">
                      Créez des profils sur mesure pour vos besoins spécifiques
                    </p>
                    <div className="mt-6">
                      <button
                        onClick={() => setShowCreateModal(true)}
                        className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-jlc-purple-600 hover:bg-jlc-purple-700"
                      >
                        <PlusIcon className="h-5 w-5 mr-2" />
                        Créer un profil
                      </button>
                    </div>
                  </div>
                </Card>
              )}
            </div>
          </>
        )}
      </div>

      {/* Modals */}
      <CreateProfileModal isOpen={showCreateModal} onClose={() => setShowCreateModal(false)} />
      {editingProfile && (
        <EditProfileModal
          profile={editingProfile}
          isOpen={!!editingProfile}
          onClose={() => setEditingProfile(null)}
        />
      )}
      {deletingProfile && (
        <DeleteConfirmModal
          isOpen={!!deletingProfile}
          title="Supprimer le profil"
          message={`Êtes-vous sûr de vouloir supprimer le profil "${deletingProfile.name}" ? Les groupes utilisant ce profil perdront leurs permissions.`}
          onConfirm={handleDelete}
          onClose={() => setDeletingProfile(null)}
        />
      )}
    </Layout>
  )
}
