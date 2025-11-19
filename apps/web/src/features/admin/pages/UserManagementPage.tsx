import { useState, useEffect } from 'react'
import Layout from '@/components/Layout'
import Card from '@/components/Card'
import {
  useGetUsersQuery,
  useUpdateUserStatusMutation,
  useUpdateUserMutation,
  useDeleteUserMutation,
  useMarkUserAsViewedMutation,
  useBulkBlockUsersMutation,
  useBulkUnblockUsersMutation,
  useBulkArchiveUsersMutation,
  useBulkDeleteUsersMutation,
  useExportUsersCSVMutation,
  type User,
} from '../api/usersApi'
import toast from 'react-hot-toast'
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
  EyeIcon,
  CloudArrowUpIcon,
  ChevronUpIcon,
  ChevronDownIcon,
} from '@heroicons/react/24/outline'
import { Link } from 'react-router-dom'
import EditUserModal from '../components/EditUserModal'
import DeleteUserModal from '../components/DeleteUserModal'
import BlockUserModal from '../components/BlockUserModal'
import QuickAddUserModal from '../components/QuickAddUserModal'
import ResetMfaModal from '../components/ResetMfaModal'
import UserDetailModal from '../components/UserDetailModal'
import BulkImportUsersModal from '../components/BulkImportUsersModal'
import ArchiveUserModal from '../components/ArchiveUserModal'
import RestoreUserModal from '../components/RestoreUserModal'
import AdminUpdatePasswordModal from '../components/AdminUpdatePasswordModal'
import { UserRoles, RoleLabels, RoleColors } from '@/constants/iamConstants'
import { ArrowPathIcon, ArchiveBoxIcon } from '@heroicons/react/24/outline'
import NewBadge from '@/components/NewBadge'
import { useListProfilesQuery, useListGroupsQuery } from '@/features/iam/api/iamApi'

export default function UserManagementPage() {
  const [page, setPage] = useState(1)
  const [searchQuery, setSearchQuery] = useState('')
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('')
  
  // Debounce search query pour éviter trop de requêtes
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setDebouncedSearchQuery(searchQuery)
    }, 500) // 500ms de délai
    
    return () => clearTimeout(timeoutId)
  }, [searchQuery])
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [roleFilter, setRoleFilter] = useState<string>('')
  const [showFilters, setShowFilters] = useState(false)
  const [viewMode, setViewMode] = useState<'active' | 'archived'>('active')
  
  // Sorting states
  const [sortBy, setSortBy] = useState<'username' | 'email' | 'roles' | 'status' | 'created_at'>('username')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')

  // Bulk selection states
  const [selectedUserIds, setSelectedUserIds] = useState<string[]>([])
  const [selectAll, setSelectAll] = useState(false)

  // Modal states
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [selectedUserId, setSelectedUserId] = useState<string>('')
  const [showEditModal, setShowEditModal] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [showBlockModal, setShowBlockModal] = useState(false)
  const [showQuickAddModal, setShowQuickAddModal] = useState(false)
  const [showResetMfaModal, setShowResetMfaModal] = useState(false)
  const [showDetailModal, setShowDetailModal] = useState(false)
  const [showArchiveModal, setShowArchiveModal] = useState(false)
  const [showRestoreModal, setShowRestoreModal] = useState(false)
  const [showBulkImportModal, setShowBulkImportModal] = useState(false)
  const [showPasswordModal, setShowPasswordModal] = useState(false)

  // Fetch users with filters
  const { data, isLoading, isFetching, refetch } = useGetUsersQuery({
    page,
    page_size: 15,
    search: debouncedSearchQuery || undefined,
    status: viewMode === 'archived' ? 'archived' : (statusFilter || undefined),
    role: roleFilter || undefined,
    sort_by: sortBy,
    sort_order: sortOrder,
  })

  // Fetch profiles and groups for mapping
  const { data: profiles = [] } = useListProfilesQuery()
  const { data: groups = [] } = useListGroupsQuery()

  // Create maps for quick lookup
  const profilesMap = profiles.reduce((acc, profile) => {
    acc[profile.id] = profile.name
    return acc
  }, {} as Record<string, string>)

  const groupsMap = groups.reduce((acc, group) => {
    acc[group.id] = group.name
    return acc
  }, {} as Record<string, string>)

  // Mark user as viewed mutation
  const [markUserAsViewed] = useMarkUserAsViewedMutation()
  
  // Sorting function
  const handleSort = (field: typeof sortBy) => {
    if (sortBy === field) {
      // Toggle order if same field
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      // New field, default to ascending
      setSortBy(field)
      setSortOrder('asc')
    }
  }

  // Bulk operation mutations
  const [bulkBlockUsers] = useBulkBlockUsersMutation()
  const [bulkUnblockUsers] = useBulkUnblockUsersMutation()
  const [bulkArchiveUsers] = useBulkArchiveUsersMutation()
  const [bulkDeleteUsers] = useBulkDeleteUsersMutation()
  const [exportUsersCSV] = useExportUsersCSVMutation()

  // Manual email verification toggle
  const handleToggleEmailVerification = async (user: User) => {
    const newStatus = !user.is_verified
    const action = newStatus ? 'vérifier' : 'dévérifier'
    
    if (!confirm(`Êtes-vous sûr de vouloir ${action} l'email de ${user.username} ?`)) {
      return
    }

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/admin/email-verification/manual-verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          user_id: user.id,
          is_verified: newStatus,
          reason: `Manuel ${action}ication par admin pour tests`
        }),
      })

      const data = await response.json()

      if (response.ok) {
        toast.success(`Email ${newStatus ? 'vérifié' : 'dévérifié'} avec succès`)
        refetch()
      } else {
        toast.error(data.detail || 'Erreur lors de la modification')
      }
    } catch (error) {
      toast.error('Erreur de connexion')
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1) // Reset to first page on search
  }

  const handleViewDetails = async (user: User) => {
    setSelectedUserId(user.id)
    setShowDetailModal(true)
    
    // Mark user as viewed to remove "New" badge
    try {
      await markUserAsViewed(user.id).unwrap()
    } catch (error) {
      console.error('Failed to mark user as viewed:', error)
    }
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

  const handleArchive = (user: User) => {
    setSelectedUser(user)
    setShowArchiveModal(true)
  }

  const handleRestore = (user: User) => {
    setSelectedUser(user)
    setShowRestoreModal(true)
  }

  const handleModalSuccess = () => {
    refetch()
  }

  // Bulk selection handlers
  const handleSelectAll = () => {
    if (selectAll) {
      setSelectedUserIds([])
      setSelectAll(false)
    } else {
      const allIds = data?.users.map(user => user.id) || []
      setSelectedUserIds(allIds)
      setSelectAll(true)
    }
  }

  const handleSelectUser = (userId: string) => {
    setSelectedUserIds(prev => {
      if (prev.includes(userId)) {
        return prev.filter(id => id !== userId)
      } else {
        return [...prev, userId]
      }
    })
  }

  // Reset selection when data changes
  useEffect(() => {
    setSelectedUserIds([])
    setSelectAll(false)
  }, [data])

  // Bulk operation handlers
  const handleBulkBlock = async () => {
    if (!confirm(`Êtes-vous sûr de vouloir bloquer ${selectedUserIds.length} utilisateur(s) ?`)) return
    
    try {
      const result = await bulkBlockUsers({ user_ids: selectedUserIds, reason: 'Blocage en masse par admin' }).unwrap()
      toast.success(`${result.succeeded} utilisateur(s) bloqué(s)${result.failed > 0 ? `, ${result.failed} échec(s)` : ''}`)
      setSelectedUserIds([])
      setSelectAll(false)
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors du blocage')
    }
  }

  const handleBulkUnblock = async () => {
    if (!confirm(`Êtes-vous sûr de vouloir débloquer ${selectedUserIds.length} utilisateur(s) ?`)) return
    
    try {
      const result = await bulkUnblockUsers({ user_ids: selectedUserIds, reason: 'Déblocage en masse par admin' }).unwrap()
      toast.success(`${result.succeeded} utilisateur(s) débloqué(s)${result.failed > 0 ? `, ${result.failed} échec(s)` : ''}`)
      setSelectedUserIds([])
      setSelectAll(false)
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors du déblocage')
    }
  }

  const handleBulkArchive = async () => {
    if (!confirm(`Êtes-vous sûr de vouloir archiver ${selectedUserIds.length} utilisateur(s) ?`)) return
    
    try {
      const result = await bulkArchiveUsers({ user_ids: selectedUserIds, reason: 'Archivage en masse par admin' }).unwrap()
      toast.success(`${result.succeeded} utilisateur(s) archivé(s)${result.failed > 0 ? `, ${result.failed} échec(s)` : ''}`)
      setSelectedUserIds([])
      setSelectAll(false)
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de l\'archivage')
    }
  }

  const handleBulkDelete = async () => {
    if (!confirm(`⚠️ ATTENTION : Êtes-vous sûr de vouloir supprimer définitivement ${selectedUserIds.length} utilisateur(s) ?\n\nCette action est irréversible.`)) return
    
    try {
      const result = await bulkDeleteUsers({ user_ids: selectedUserIds, permanent: false, reason: 'Suppression en masse par admin' }).unwrap()
      toast.success(`${result.succeeded} utilisateur(s) supprimé(s)${result.failed > 0 ? `, ${result.failed} échec(s)` : ''}`)
      setSelectedUserIds([])
      setSelectAll(false)
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la suppression')
    }
  }

  const handleExportCSV = async () => {
    try {
      const blob = await exportUsersCSV({ user_ids: selectedUserIds }).unwrap()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `users_export_${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      toast.success(`${selectedUserIds.length} utilisateur(s) exporté(s)`)
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de l\'export')
    }
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
      archived: {
        color: 'bg-orange-100 text-orange-800',
        icon: <ArchiveBoxIcon className="h-4 w-4" />,
        label: 'Archivé',
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
    return (
      <div className="flex flex-wrap gap-1">
        {roles.map((role) => (
          <span
            key={role}
            className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
              RoleColors[role] || 'bg-gray-100 text-gray-800'
            }`}
          >
            {RoleLabels[role] || role}
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
              {data?.pagination.total || 0} utilisateur(s) {viewMode === 'archived' ? 'archivé(s)' : 'enregistré(s)'}
            </p>
            {/* Tabs */}
            <div className="mt-4 flex gap-2">
              <button
                onClick={() => {
                  setViewMode('active')
                  setStatusFilter('')
                  setPage(1)
                }}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  viewMode === 'active'
                    ? 'bg-jlc-purple-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Actifs
              </button>
              <button
                onClick={() => {
                  setViewMode('archived')
                  setStatusFilter('')
                  setPage(1)
                }}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  viewMode === 'archived'
                    ? 'bg-orange-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <ArchiveBoxIcon className="h-5 w-5 inline mr-2" />
                Archives
              </button>
            </div>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setShowBulkImportModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              title="Importer plusieurs utilisateurs via CSV"
            >
              <CloudArrowUpIcon className="h-5 w-5" />
              Importer CSV
            </button>
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
                    <option value="archived">Archivé</option>
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
                    <option value={UserRoles.ADMIN}>Administrateur</option>
                    <option value={UserRoles.SUPER_ADMIN}>Super Admin</option>
                    <option value={UserRoles.CANDIDAT}>Candidat</option>
                    <option value={UserRoles.INTERIM}>Intérimaire</option>
                    <option value={UserRoles.COMPANY}>Entreprise</option>
                    <option value={UserRoles.COLLABORATEUR}>Collaborateur</option>
                  </select>
                </div>
              </div>
            )}
          </form>
        </Card>

        {/* Bulk Actions Bar */}
        {selectedUserIds.length > 0 && (
          <div className="fixed bottom-8 left-1/2 transform -translate-x-1/2 z-50">
            <div className="bg-jlc-purple-600 text-white px-6 py-4 rounded-lg shadow-2xl flex items-center gap-6">
              <span className="font-medium">
                {selectedUserIds.length} utilisateur(s) sélectionné(s)
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleBulkBlock}
                  className="px-4 py-2 bg-white text-jlc-purple-600 rounded hover:bg-gray-100 transition-colors text-sm font-medium"
                  title="Bloquer les utilisateurs sélectionnés"
                >
                  Bloquer
                </button>
                <button
                  onClick={handleBulkUnblock}
                  className="px-4 py-2 bg-white text-jlc-purple-600 rounded hover:bg-gray-100 transition-colors text-sm font-medium"
                  title="Débloquer les utilisateurs sélectionnés"
                >
                  Débloquer
                </button>
                <button
                  onClick={handleBulkArchive}
                  className="px-4 py-2 bg-white text-jlc-purple-600 rounded hover:bg-gray-100 transition-colors text-sm font-medium"
                  title="Archiver les utilisateurs sélectionnés"
                >
                  Archiver
                </button>
                <button
                  onClick={handleBulkDelete}
                  className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors text-sm font-medium"
                  title="Supprimer les utilisateurs sélectionnés"
                >
                  Supprimer
                </button>
                <button
                  onClick={handleExportCSV}
                  className="px-4 py-2 bg-white text-jlc-purple-600 rounded hover:bg-gray-100 transition-colors text-sm font-medium"
                  title="Exporter en CSV"
                >
                  Exporter CSV
                </button>
                <button
                  onClick={() => {
                    setSelectedUserIds([])
                    setSelectAll(false)
                  }}
                  className="px-4 py-2 bg-white/20 text-white rounded hover:bg-white/30 transition-colors text-sm font-medium"
                >
                  Annuler
                </button>
              </div>
            </div>
          </div>
        )}

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
                    <th className="px-4 py-3 text-left">
                      <input
                        type="checkbox"
                        checked={selectAll}
                        onChange={handleSelectAll}
                        className="h-4 w-4 text-jlc-purple-600 focus:ring-jlc-purple-500 border-gray-300 rounded cursor-pointer"
                      />
                    </th>
                    <th 
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition select-none"
                      onClick={() => handleSort('username')}
                    >
                      <div className="flex items-center gap-1">
                        Utilisateur
                        {sortBy === 'username' && (
                          sortOrder === 'asc' ? <ChevronUpIcon className="h-4 w-4" /> : <ChevronDownIcon className="h-4 w-4" />
                        )}
                      </div>
                    </th>
                    <th 
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition select-none"
                      onClick={() => handleSort('email')}
                    >
                      <div className="flex items-center gap-1">
                        Email
                        {sortBy === 'email' && (
                          sortOrder === 'asc' ? <ChevronUpIcon className="h-4 w-4" /> : <ChevronDownIcon className="h-4 w-4" />
                        )}
                      </div>
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Profils
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Groupes
                    </th>
                    <th 
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition select-none"
                      onClick={() => handleSort('status')}
                    >
                      <div className="flex items-center gap-1">
                        Statut
                        {sortBy === 'status' && (
                          sortOrder === 'asc' ? <ChevronUpIcon className="h-4 w-4" /> : <ChevronDownIcon className="h-4 w-4" />
                        )}
                      </div>
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Email Vérifié
                    </th>
                    <th 
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition select-none"
                      onClick={() => handleSort('created_at')}
                    >
                      <div className="flex items-center gap-1">
                        Inscription
                        {sortBy === 'created_at' && (
                          sortOrder === 'asc' ? <ChevronUpIcon className="h-4 w-4" /> : <ChevronDownIcon className="h-4 w-4" />
                        )}
                      </div>
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {data.users.map((user) => (
                    <tr 
                      key={user.id} 
                      onClick={() => handleViewDetails(user)}
                      className="hover:bg-gray-50 transition-colors cursor-pointer"
                    >
                      <td className="px-4 py-4 whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                        <input
                          type="checkbox"
                          checked={selectedUserIds.includes(user.id)}
                          onChange={() => handleSelectUser(user.id)}
                          className="h-4 w-4 text-jlc-purple-600 focus:ring-jlc-purple-500 border-gray-300 rounded cursor-pointer"
                        />
                      </td>
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
                            <div className="text-sm font-medium text-gray-900 flex items-center gap-2">
                              {user.full_name || user.username}
                              <NewBadge 
                                createdAt={user.created_at} 
                                firstProfileViewAt={user.first_profile_view_at}
                              />
                            </div>
                            <div className="text-sm text-gray-500">@{user.username}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{user.email}</div>
                        <div className="text-xs text-gray-500">{user.provider}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-wrap gap-1">
                          {user.profile_ids && user.profile_ids.length > 0 ? (
                            user.profile_ids.slice(0, 2).map((profileId: string) => (
                              <span
                                key={profileId}
                                className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800"
                                title={profilesMap[profileId] || profileId}
                              >
                                {profilesMap[profileId] || 'Profil inconnu'}
                              </span>
                            ))
                          ) : (
                            <span className="text-xs text-gray-400">Aucun</span>
                          )}
                          {user.profile_ids && user.profile_ids.length > 2 && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                              +{user.profile_ids.length - 2}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-wrap gap-1">
                          {user.group_ids && user.group_ids.length > 0 ? (
                            user.group_ids.slice(0, 2).map((groupId: string) => (
                              <span
                                key={groupId}
                                className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                                title={groupsMap[groupId] || groupId}
                              >
                                {groupsMap[groupId] || 'Groupe inconnu'}
                              </span>
                            ))
                          ) : (
                            <span className="text-xs text-gray-400">Aucun</span>
                          )}
                          {user.group_ids && user.group_ids.length > 2 && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                              +{user.group_ids.length - 2}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusBadge(user.status)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleToggleEmailVerification(user)
                          }}
                          className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium transition-colors ${
                            user.is_verified
                              ? 'bg-green-100 text-green-800 hover:bg-green-200'
                              : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                          }`}
                          title={user.is_verified ? 'Cliquez pour dévérifier (tests)' : 'Cliquez pour vérifier manuellement'}
                        >
                          {user.is_verified ? '✓ Vérifié' : '✗ Non vérifié'}
                        </button>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(user.created_at).toLocaleDateString('fr-FR', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                        })}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex justify-end gap-2" onClick={(e) => e.stopPropagation()}>
                          <button
                            onClick={() => handleViewDetails(user)}
                            className="p-2 text-jlc-purple-600 hover:bg-jlc-purple-50 rounded-lg transition-colors"
                            title="Voir détails"
                          >
                            <EyeIcon className="h-5 w-5" />
                          </button>
                          {viewMode === 'active' && (
                            <>
                              <button
                                onClick={() => handleEdit(user)}
                                disabled={user.status === 'archived'}
                                className={`p-2 rounded-lg transition-colors ${
                                  user.status === 'archived'
                                    ? 'text-gray-400 cursor-not-allowed'
                                    : 'text-blue-600 hover:bg-blue-50'
                                }`}
                                title={user.status === 'archived' ? 'Compte archivé (non modifiable)' : 'Modifier'}
                              >
                                <PencilIcon className="h-5 w-5" />
                              </button>
                              <button
                                onClick={() => handleBlock(user)}
                                disabled={user.status === 'archived'}
                                className={`p-2 rounded-lg transition-colors ${
                                  user.status === 'archived'
                                    ? 'text-gray-400 cursor-not-allowed'
                                    : user.status === 'suspended'
                                    ? 'text-green-600 hover:bg-green-50'
                                    : 'text-orange-600 hover:bg-orange-50'
                                }`}
                                title={
                                  user.status === 'archived'
                                    ? 'Compte archivé (action impossible)'
                                    : user.status === 'suspended'
                                    ? 'Débloquer'
                                    : 'Bloquer'
                                }
                              >
                                <NoSymbolIcon className="h-5 w-5" />
                              </button>
                              <button
                                onClick={() => {
                                  setSelectedUser(user)
                                  setShowResetMfaModal(true)
                                }}
                                disabled={user.status === 'archived'}
                                className={`p-2 rounded-lg transition-colors ${
                                  user.status === 'archived'
                                    ? 'text-gray-400 cursor-not-allowed'
                                    : 'text-purple-600 hover:bg-purple-50'
                                }`}
                                title={
                                  user.status === 'archived'
                                    ? 'Compte archivé (action impossible)'
                                    : 'Réinitialiser MFA'
                                }
                              >
                                <ShieldExclamationIcon className="h-5 w-5" />
                              </button>
                              <button
                                onClick={() => handleArchive(user)}
                                disabled={user.status === 'archived'}
                                className={`p-2 rounded-lg transition-colors ${
                                  user.status === 'archived'
                                    ? 'text-gray-400 cursor-not-allowed'
                                    : 'text-orange-600 hover:bg-orange-50'
                                }`}
                                title={user.status === 'archived' ? 'Déjà archivé' : 'Archiver'}
                              >
                                <ArchiveBoxIcon className="h-5 w-5" />
                              </button>
                            </>
                          )}
                          {viewMode === 'archived' && (
                            <button
                              onClick={() => handleRestore(user)}
                              className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                              title="Restaurer"
                            >
                              <ArrowPathIcon className="h-5 w-5" />
                            </button>
                          )}
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
      {selectedUserId && (
        <UserDetailModal
          isOpen={showDetailModal}
          onClose={() => {
            setShowDetailModal(false)
            setSelectedUserId('')
          }}
          userId={selectedUserId}
        />
      )}
      
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
          <ArchiveUserModal
            user={selectedUser}
            isOpen={showArchiveModal}
            onClose={() => {
              setShowArchiveModal(false)
              setSelectedUser(null)
            }}
            onSuccess={handleModalSuccess}
          />
          <RestoreUserModal
            user={selectedUser}
            isOpen={showRestoreModal}
            onClose={() => {
              setShowRestoreModal(false)
              setSelectedUser(null)
            }}
            onSuccess={handleModalSuccess}
          />
        </>
      )}
      <QuickAddUserModal isOpen={showQuickAddModal} onClose={() => setShowQuickAddModal(false)} />
      <BulkImportUsersModal 
        isOpen={showBulkImportModal} 
        onClose={() => setShowBulkImportModal(false)}
        onSuccess={handleModalSuccess}
      />
    </Layout>
  )
}
