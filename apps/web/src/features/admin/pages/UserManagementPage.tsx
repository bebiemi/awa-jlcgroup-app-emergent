import { useState } from 'react'
import Layout from '@/components/Layout'
import Card from '@/components/Card'
import {
  useGetUsersQuery,
  useUpdateUserStatusMutation,
  useUpdateUserMutation,
  useDeleteUserMutation,
  type User,
} from '../api/usersApi'
import {
  MagnifyingGlassIcon,
  PencilIcon,
  TrashIcon,
  NoSymbolIcon,
  CheckCircleIcon,
  FunnelIcon,
  PlusIcon,
  UserPlusIcon,
  ShieldExclamationIcon,
} from '@heroicons/react/24/outline'
import { Link } from 'react-router-dom'
import EditUserModal from '../components/EditUserModal'
import DeleteUserModal from '../components/DeleteUserModal'
import BlockUserModal from '../components/BlockUserModal'
import QuickAddUserModal from '../components/QuickAddUserModal'
import ResetMfaModal from '../components/ResetMfaModal'
import { UserRoles, RoleLabels, RoleColors } from '@/constants/iamConstants'

export default function UserManagementPage() {
  const [page, setPage] = useState(1)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [roleFilter, setRoleFilter] = useState<string>('')
  const [showFilters, setShowFilters] = useState(false)

  // Modal states
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [showBlockModal, setShowBlockModal] = useState(false)
  const [showQuickAddModal, setShowQuickAddModal] = useState(false)
  const [showResetMfaModal, setShowResetMfaModal] = useState(false)

  // Fetch users with filters
  const { data, isLoading, isFetching } = useGetUsersQuery({
    page,
    page_size: 15,
    search: searchQuery || undefined,
    status: statusFilter || undefined,
    role: roleFilter || undefined,
  })

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1) // Reset to first page on search
  }

  const handleEdit = (user: User) => {
    setSelectedUser(user)
    setShowEditModal(true)
  }

  const handleDelete = (user: User) => {
    setSelectedUser(user)
    setShowDeleteModal(true)
  }

  const handleBlock = (user: User) => {
    setSelectedUser(user)
    setShowBlockModal(true)
  }

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      active: {
        color: 'bg-green-100 text-green-800',
        icon: <CheckCircleIcon className="h-4 w-4" />,
        label: 'Actif',
      },
      pending: {
        color: 'bg-yellow-100 text-yellow-800',
        icon: <FunnelIcon className="h-4 w-4" />,
        label: 'En attente',
      },
      suspended: {
        color: 'bg-red-100 text-red-800',
        icon: <NoSymbolIcon className="h-4 w-4" />,
        label: 'Suspendu',
      },
      deleted: {
        color: 'bg-gray-100 text-gray-800',
        icon: <TrashIcon className="h-4 w-4" />,
        label: 'Supprimé',
      },
    }

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.pending

    return (
      <span
        className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}
      >
        {config.icon}
        {config.label}
      </span>
    )
  }

  const getRoleBadge = (roles: string[]) => {
    const roleColors: Record<string, string> = {
      admin: 'bg-purple-100 text-purple-800',
      super_admin: 'bg-red-100 text-red-800',
      candidat: 'bg-blue-100 text-blue-800',
      interim: 'bg-teal-100 text-teal-800',
      company: 'bg-indigo-100 text-indigo-800',
      collaborateur: 'bg-green-100 text-green-800',
    }

    return (
      <div className="flex flex-wrap gap-1">
        {roles.map((role) => (
          <span
            key={role}
            className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
              roleColors[role] || 'bg-gray-100 text-gray-800'
            }`}
          >
            {role === 'candidat' ? 'Candidat' : 
             role === 'interim' ? 'Intérimaire' :
             role === 'company' ? 'Entreprise' :
             role === 'collaborateur' ? 'Collaborateur' :
             role === 'super_admin' ? 'Super Admin' :
             role}
          </span>
        ))}
      </div>
    )
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Gestion des Utilisateurs</h1>
            <p className="mt-2 text-gray-600">
              {data?.pagination.total || 0} utilisateur(s) enregistré(s)
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setShowQuickAddModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-white border-2 border-jlc-purple-600 text-jlc-purple-600 rounded-lg hover:bg-jlc-purple-50 transition-colors"
            >
              <UserPlusIcon className="h-5 w-5" />
              Ajout rapide
            </button>
            <Link
              to="/admin/users/new"
              className="flex items-center gap-2 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 transition-colors"
            >
              <PlusIcon className="h-5 w-5" />
              Création détaillée
            </Link>
          </div>
        </div>

        {/* Search and Filters */}
        <Card>
          <form onSubmit={handleSearch} className="space-y-4">
            <div className="flex gap-4">
              <div className="flex-1 relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Rechercher par nom, email ou nom d'utilisateur..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
                />
              </div>
              <button
                type="button"
                onClick={() => setShowFilters(!showFilters)}
                className={`px-4 py-2 border rounded-lg flex items-center gap-2 transition-colors ${
                  showFilters
                    ? 'bg-jlc-purple-50 border-jlc-purple-300 text-jlc-purple-700'
                    : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                <FunnelIcon className="h-5 w-5" />
                Filtres
              </button>
              <button
                type="submit"
                className="px-6 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 transition-colors"
              >
                Rechercher
              </button>
            </div>

            {/* Advanced Filters */}
            {showFilters && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-gray-200">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Statut
                  </label>
                  <select
                    value={statusFilter}
                    onChange={(e) => {
                      setStatusFilter(e.target.value)
                      setPage(1)
                    }}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
                  >
                    <option value="">Tous les statuts</option>
                    <option value="active">Actif</option>
                    <option value="pending">En attente</option>
                    <option value="suspended">Suspendu</option>
                    <option value="deleted">Supprimé</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Rôle</label>
                  <select
                    value={roleFilter}
                    onChange={(e) => {
                      setRoleFilter(e.target.value)
                      setPage(1)
                    }}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
                  >
                    <option value="">Tous les rôles</option>
                    <option value="admin">Admin</option>
                    <option value="super_admin">Super Admin</option>
                    <option value="candidat">Candidat</option>
                    <option value="interim">Intérimaire</option>
                    <option value="company">Entreprise</option>
                    <option value="collaborateur">Collaborateur</option>
                  </select>
                </div>
              </div>
            )}
          </form>
        </Card>

        {/* Users Table */}
        <Card>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
            </div>
          ) : data?.users && data.users.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Utilisateur
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Rôle(s)
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Statut
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Inscription
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {data.users.map((user) => (
                    <tr key={user.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full bg-gradient-to-br from-jlc-purple-400 to-jlc-purple-600 flex items-center justify-center text-white font-semibold">
                              {user.full_name
                                ? user.full_name.charAt(0).toUpperCase()
                                : user.username.charAt(0).toUpperCase()}
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {user.full_name || user.username}
                            </div>
                            <div className="text-sm text-gray-500">@{user.username}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{user.email}</div>
                        <div className="text-xs text-gray-500">{user.provider}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">{getRoleBadge(user.roles)}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusBadge(user.status)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(user.created_at).toLocaleDateString('fr-FR', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                        })}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex justify-end gap-2">
                          <button
                            onClick={() => handleEdit(user)}
                            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="Modifier"
                          >
                            <PencilIcon className="h-5 w-5" />
                          </button>
                          <button
                            onClick={() => handleBlock(user)}
                            className={`p-2 rounded-lg transition-colors ${
                              user.status === 'suspended'
                                ? 'text-green-600 hover:bg-green-50'
                                : 'text-orange-600 hover:bg-orange-50'
                            }`}
                            title={user.status === 'suspended' ? 'Débloquer' : 'Bloquer'}
                          >
                            <NoSymbolIcon className="h-5 w-5" />
                          </button>
                          <button
                            onClick={() => {
                              setSelectedUser(user)
                              setShowResetMfaModal(true)
                            }}
                            className="p-2 text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
                            title="Réinitialiser MFA"
                          >
                            <ShieldExclamationIcon className="h-5 w-5" />
                          </button>
                          <button
                            onClick={() => handleDelete(user)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Supprimer"
                          >
                            <TrashIcon className="h-5 w-5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500">Aucun utilisateur trouvé</p>
            </div>
          )}

          {/* Pagination */}
          {data?.pagination && data.pagination.total_pages > 1 && (
            <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
              <div className="flex-1 flex justify-between sm:hidden">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={!data.pagination.has_prev || isFetching}
                  className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Précédent
                </button>
                <button
                  onClick={() => setPage((p) => p + 1)}
                  disabled={!data.pagination.has_next || isFetching}
                  className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Suivant
                </button>
              </div>
              <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm text-gray-700">
                    Affichage de{' '}
                    <span className="font-medium">
                      {(data.pagination.page - 1) * data.pagination.page_size + 1}
                    </span>{' '}
                    à{' '}
                    <span className="font-medium">
                      {Math.min(
                        data.pagination.page * data.pagination.page_size,
                        data.pagination.total
                      )}
                    </span>{' '}
                    sur <span className="font-medium">{data.pagination.total}</span> résultats
                  </p>
                </div>
                <div>
                  <nav
                    className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px"
                    aria-label="Pagination"
                  >
                    <button
                      onClick={() => setPage((p) => Math.max(1, p - 1))}
                      disabled={!data.pagination.has_prev || isFetching}
                      className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      ←
                    </button>
                    {Array.from({ length: data.pagination.total_pages }, (_, i) => i + 1)
                      .filter(
                        (pageNum) =>
                          pageNum === 1 ||
                          pageNum === data.pagination.total_pages ||
                          Math.abs(pageNum - page) <= 2
                      )
                      .map((pageNum, idx, arr) => {
                        // Show ellipsis
                        if (idx > 0 && pageNum - arr[idx - 1] > 1) {
                          return [
                            <span
                              key={`ellipsis-${pageNum}`}
                              className="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700"
                            >
                              ...
                            </span>,
                            <button
                              key={pageNum}
                              onClick={() => setPage(pageNum)}
                              disabled={isFetching}
                              className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                                page === pageNum
                                  ? 'z-10 bg-jlc-purple-50 border-jlc-purple-500 text-jlc-purple-600'
                                  : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                              } disabled:opacity-50 disabled:cursor-not-allowed`}
                            >
                              {pageNum}
                            </button>,
                          ]
                        }
                        return (
                          <button
                            key={pageNum}
                            onClick={() => setPage(pageNum)}
                            disabled={isFetching}
                            className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                              page === pageNum
                                ? 'z-10 bg-jlc-purple-50 border-jlc-purple-500 text-jlc-purple-600'
                                : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                            } disabled:opacity-50 disabled:cursor-not-allowed`}
                          >
                            {pageNum}
                          </button>
                        )
                      })}
                    <button
                      onClick={() => setPage((p) => p + 1)}
                      disabled={!data.pagination.has_next || isFetching}
                      className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      →
                    </button>
                  </nav>
                </div>
              </div>
            </div>
          )}
        </Card>
      </div>

      {/* Modals */}
      {selectedUser && (
        <>
          <EditUserModal
            user={selectedUser}
            isOpen={showEditModal}
            onClose={() => {
              setShowEditModal(false)
              setSelectedUser(null)
            }}
          />
          <DeleteUserModal
            user={selectedUser}
            isOpen={showDeleteModal}
            onClose={() => {
              setShowDeleteModal(false)
              setSelectedUser(null)
            }}
          />
          <BlockUserModal
            user={selectedUser}
            isOpen={showBlockModal}
            onClose={() => {
              setShowBlockModal(false)
              setSelectedUser(null)
            }}
          />
          <ResetMfaModal
            user={selectedUser}
            isOpen={showResetMfaModal}
            onClose={() => {
              setShowResetMfaModal(false)
              setSelectedUser(null)
            }}
          />
        </>
      )}
      <QuickAddUserModal isOpen={showQuickAddModal} onClose={() => setShowQuickAddModal(false)} />
    </Layout>
  )
}
