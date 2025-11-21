import { useState } from 'react'
import Layout from '@/components/Layout'
import { usePermission } from '@/hooks/usePermission'
import { useGetUsersQuery } from '@/features/users/api/usersApi'
import { useListProfilesQuery, useListGroupsQuery } from '@/features/iam/api/iamApi'
import { 
  UserGroupIcon, 
  ShieldCheckIcon,
  ExclamationCircleIcon,
  MagnifyingGlassIcon,
  UserPlusIcon,
  PencilIcon
} from '@heroicons/react/24/outline'
import { toast } from 'react-hot-toast'
import AssignTeamMemberModal from '../components/AssignTeamMemberModal'

export default function MyTeamSettingsPage() {
  const { hasPermission: canAssignProfiles } = usePermission('rbac.assign_profiles')
  const { hasPermission: canAssignGroups } = usePermission('rbac.assign_groups')
  
  // Fetch data
  const { data: usersData, isLoading: usersLoading } = useGetUsersQuery({ page: 1, page_size: 1000 })
  const { data: profiles = [], isLoading: profilesLoading } = useListProfilesQuery()
  const { data: groups = [], isLoading: groupsLoading } = useListGroupsQuery()
  
  // Local state
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedRole, setSelectedRole] = useState<string>('all')
  const [showAssignModal, setShowAssignModal] = useState(false)
  const [selectedUser, setSelectedUser] = useState<any>(null)

  if (!canAssignProfiles && !canAssignGroups) {
    return (
      <Layout>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <div className="flex items-start gap-3">
              <ExclamationCircleIcon className="h-6 w-6 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-yellow-900 mb-2">
                  Permissions insuffisantes
                </h3>
                <p className="text-sm text-yellow-800">
                  Vous n'avez pas les permissions nécessaires pour gérer une équipe.
                  Contactez votre administrateur pour obtenir les permissions <code className="px-2 py-1 bg-yellow-100 rounded">rbac.assign_profiles</code> ou <code className="px-2 py-1 bg-yellow-100 rounded">rbac.assign_groups</code>.
                </p>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <UserGroupIcon className="h-8 w-8 text-jlc-purple-600" />
            <h1 className="text-3xl font-bold text-gray-900">Mon Équipe</h1>
          </div>
          <p className="text-gray-600">
            Gérez les profils et groupes de vos collaborateurs
          </p>
        </div>

        {/* Info Banner */}
        <div className="mb-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-start gap-3">
            <ShieldCheckIcon className="h-6 w-6 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-blue-900 mb-2">
                Gestion simplifiée de votre équipe
              </h3>
              <p className="text-sm text-blue-800">
                Vous pouvez attribuer des <strong>profils métier</strong> et des <strong>groupes organisationnels</strong> à vos collaborateurs.
                Les rôles IAM techniques sont réservés aux administrateurs.
              </p>
            </div>
          </div>
        </div>

        {/* Permissions actives */}
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Vos permissions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {canAssignProfiles && (
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center gap-2 mb-1">
                  <div className="h-2 w-2 bg-green-500 rounded-full" />
                  <span className="font-medium text-green-900">Assigner des profils</span>
                </div>
                <p className="text-sm text-green-700">
                  Vous pouvez attribuer des profils métier à vos collaborateurs
                </p>
              </div>
            )}
            
            {canAssignGroups && (
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center gap-2 mb-1">
                  <div className="h-2 w-2 bg-green-500 rounded-full" />
                  <span className="font-medium text-green-900">Assigner des groupes</span>
                </div>
                <p className="text-sm text-green-700">
                  Vous pouvez ajouter vos collaborateurs à des groupes organisationnels
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Filters and Search */}
        <div className="mb-6 bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Rechercher un collaborateur..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              />
            </div>
            
            {/* Role Filter */}
            <div className="md:w-64">
              <select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              >
                <option value="all">Tous les rôles</option>
                <option value="interim">Intérimaire</option>
                <option value="company">Entreprise</option>
                <option value="admin">Administrateur</option>
                <option value="commercial">Commercial</option>
              </select>
            </div>
            
            {/* Add Button */}
            <button
              onClick={() => toast('Fonctionnalité à venir : Inviter un nouveau collaborateur')}
              className="flex items-center gap-2 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 transition-colors whitespace-nowrap"
            >
              <UserPlusIcon className="h-5 w-5" />
              <span>Inviter</span>
            </button>
          </div>
        </div>

        {/* Team Members List */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          {usersLoading || profilesLoading || groupsLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-jlc-purple-600"></div>
            </div>
          ) : !usersData?.users || usersData.users.length === 0 ? (
            <div className="text-center py-12">
              <UserGroupIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Aucun collaborateur
              </h3>
              <p className="text-gray-600">
                Commencez par inviter des membres à votre équipe.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Collaborateur
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Rôles
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Profils
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Groupes
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Statut
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {usersData.users
                    .filter((user: any) => {
                      const matchesSearch = 
                        searchTerm === '' ||
                        user.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                        user.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                        user.username?.toLowerCase().includes(searchTerm.toLowerCase())
                      
                      const matchesRole = 
                        selectedRole === 'all' ||
                        user.roles?.includes(selectedRole)
                      
                      return matchesSearch && matchesRole
                    })
                    .map((user: any) => (
                      <tr key={user.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="flex-shrink-0 h-10 w-10">
                              <div className="h-10 w-10 rounded-full bg-jlc-purple-100 flex items-center justify-center">
                                <span className="text-jlc-purple-600 font-medium text-sm">
                                  {user.full_name?.charAt(0)?.toUpperCase() || user.username?.charAt(0)?.toUpperCase() || 'U'}
                                </span>
                              </div>
                            </div>
                            <div className="ml-4">
                              <div className="text-sm font-medium text-gray-900">
                                {user.full_name || user.username}
                              </div>
                              <div className="text-sm text-gray-500">{user.email}</div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex flex-wrap gap-1">
                            {user.roles?.slice(0, 2).map((role: string) => (
                              <span
                                key={role}
                                className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                              >
                                {role}
                              </span>
                            ))}
                            {user.roles?.length > 2 && (
                              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                                +{user.roles.length - 2}
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-900">
                            {user.profile_ids?.length || 0} profil(s)
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-900">
                            {user.group_ids?.length || 0} groupe(s)
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span
                            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              user.status === 'active'
                                ? 'bg-green-100 text-green-800'
                                : user.status === 'pending'
                                ? 'bg-yellow-100 text-yellow-800'
                                : 'bg-red-100 text-red-800'
                            }`}
                          >
                            {user.status === 'active' ? 'Actif' : user.status === 'pending' ? 'En attente' : 'Suspendu'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button
                            onClick={() => {
                              setSelectedUser(user)
                              setShowAssignModal(true)
                            }}
                            className="inline-flex items-center gap-1 text-jlc-purple-600 hover:text-jlc-purple-900"
                          >
                            <PencilIcon className="h-4 w-4" />
                            Gérer
                          </button>
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
        
        {/* Assignment Modal */}
        {selectedUser && (
          <AssignTeamMemberModal
            user={selectedUser}
            isOpen={showAssignModal}
            onClose={() => {
              setShowAssignModal(false)
              setSelectedUser(null)
            }}
            canAssignProfiles={canAssignProfiles}
            canAssignGroups={canAssignGroups}
          />
        )}

        {/* Help Section */}
        <div className="mt-8 p-4 bg-gray-50 border border-gray-200 rounded-lg">
          <h3 className="font-semibold text-gray-900 mb-2">Besoin d'aide ?</h3>
          <p className="text-sm text-gray-600">
            Pour gérer votre équipe de manière avancée, utilisez la <a href="/admin/users" className="text-jlc-purple-600 hover:underline">page de gestion des utilisateurs</a> où vous pouvez :
          </p>
          <ul className="mt-2 text-sm text-gray-600 space-y-1 ml-4">
            <li>• Voir tous vos collaborateurs</li>
            <li>• Modifier leurs profils et groupes</li>
            <li>• Consulter leurs permissions effectives</li>
          </ul>
        </div>
      </div>
    </Layout>
  )
}
