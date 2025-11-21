/**
 * User Management Page - Version Complète avec EntityListTemplate
 * Migration complète conservant TOUTES les fonctionnalités de l'ancienne page
 */

import { useState, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import EntityListTemplate, { type EntityListConfig } from '@/templates/EntityListTemplate'
import { usePermissions } from '@/hooks/usePermission'
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
  UserIcon,
  PencilIcon,
  TrashIcon,
  NoSymbolIcon,
  CheckCircleIcon,
  EyeIcon,
  KeyIcon,
  ArrowPathIcon,
  ArchiveBoxIcon,
  ShieldExclamationIcon,
  CloudArrowUpIcon,
  UserPlusIcon,
} from '@heroicons/react/24/outline'
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
import NewBadge from '@/components/NewBadge'
import { useListProfilesQuery, useListGroupsQuery } from '@/features/iam/api/iamApi'

export default function UserManagementPageComplete() {
  const navigate = useNavigate()
  
  // États de pagination et filtres
  const [page, setPage] = useState(1)
  const [searchQuery, setSearchQuery] = useState('')
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [roleFilter, setRoleFilter] = useState<string>('')
  const [viewMode, setViewMode] = useState<'active' | 'archived'>('active')
  
  // Tri
  const [sortBy, setSortBy] = useState<'username' | 'email' | 'roles' | 'status' | 'created_at'>('username')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')
  
  // Sélection en masse
  const [selectedUserIds, setSelectedUserIds] = useState<string[]>([])
  
  // États des modaux
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

  // Permissions
  const { permissions } = usePermissions([
    'users.create',
    'users.read',
    'users.edit',
    'users.delete',
    'users.manage',
  ])

  // Debounce search
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setDebouncedSearchQuery(searchQuery)
    }, 500)
    return () => clearTimeout(timeoutId)
  }, [searchQuery])

  // Fetch data
  const { data, isLoading, refetch } = useGetUsersQuery({
    page,
    page_size: 15,
    search: debouncedSearchQuery || undefined,
    status: viewMode === 'archived' ? 'archived' : (statusFilter || undefined),
    role: roleFilter || undefined,
    sort_by: sortBy,
    sort_order: sortOrder,
  })

  // Fetch profiles and groups pour les modaux
  const { data: profiles = [] } = useListProfilesQuery()
  const { data: groups = [] } = useListGroupsQuery()

  // Mutations
  const [updateUserStatus] = useUpdateUserStatusMutation()
  const [markUserAsViewed] = useMarkUserAsViewedMutation()
  const [bulkBlock] = useBulkBlockUsersMutation()
  const [bulkUnblock] = useBulkUnblockUsersMutation()
  const [bulkArchive] = useBulkArchiveUsersMutation()
  const [bulkDelete] = useBulkDeleteUsersMutation()
  const [exportUsers] = useExportUsersCSVMutation()

  // Handlers pour les actions
  const handleViewUser = (user: User) => {
    setSelectedUser(user)
    setShowDetailModal(true)
    if (user.new_user) {
      markUserAsViewed(user.id)
    }
  }

  const handleEditUser = (user: User) => {
    setSelectedUser(user)
    setShowEditModal(true)
  }

  const handleDeleteUser = (user: User) => {
    setSelectedUser(user)
    setShowDeleteModal(true)
  }

  const handleBlockUser = (user: User) => {
    setSelectedUser(user)
    setShowBlockModal(true)
  }

  const handleArchiveUser = (user: User) => {
    setSelectedUser(user)
    setShowArchiveModal(true)
  }

  const handleRestoreUser = (user: User) => {
    setSelectedUser(user)
    setShowRestoreModal(true)
  }

  const handleResetPassword = (user: User) => {
    setSelectedUser(user)
    setShowPasswordModal(true)
  }

  const handleResetMfa = (user: User) => {
    setSelectedUser(user)
    setShowResetMfaModal(true)
  }

  const handleActivateUser = async (user: User) => {
    try {
      await updateUserStatus({ id: user.id, status: 'active' }).unwrap()
      toast.success('Utilisateur activé')
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de l\'activation')
    }
  }

  // Bulk actions
  const handleBulkBlock = async () => {
    if (selectedUserIds.length === 0) {
      toast.error('Aucun utilisateur sélectionné')
      return
    }
    try {
      await bulkBlock({ user_ids: selectedUserIds }).unwrap()
      toast.success(`${selectedUserIds.length} utilisateur(s) bloqué(s)`)
      setSelectedUserIds([])
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors du blocage')
    }
  }

  const handleBulkUnblock = async () => {
    if (selectedUserIds.length === 0) {
      toast.error('Aucun utilisateur sélectionné')
      return
    }
    try {
      await bulkUnblock({ user_ids: selectedUserIds }).unwrap()
      toast.success(`${selectedUserIds.length} utilisateur(s) débloqué(s)`)
      setSelectedUserIds([])
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors du déblocage')
    }
  }

  const handleBulkArchive = async () => {
    if (selectedUserIds.length === 0) {
      toast.error('Aucun utilisateur sélectionné')
      return
    }
    if (!window.confirm(`Archiver ${selectedUserIds.length} utilisateur(s) ?`)) return
    
    try {
      await bulkArchive({ user_ids: selectedUserIds }).unwrap()
      toast.success(`${selectedUserIds.length} utilisateur(s) archivé(s)`)
      setSelectedUserIds([])
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de l\'archivage')
    }
  }

  const handleBulkDelete = async () => {
    if (selectedUserIds.length === 0) {
      toast.error('Aucun utilisateur sélectionné')
      return
    }
    if (!window.confirm(`Supprimer définitivement ${selectedUserIds.length} utilisateur(s) ?`)) return
    
    try {
      await bulkDelete({ user_ids: selectedUserIds }).unwrap()
      toast.success(`${selectedUserIds.length} utilisateur(s) supprimé(s)`)
      setSelectedUserIds([])
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la suppression')
    }
  }

  const handleExportCSV = async () => {
    try {
      const result = await exportUsers({
        status: viewMode === 'archived' ? 'archived' : (statusFilter || undefined),
        role: roleFilter || undefined,
      }).unwrap()
      
      // Create download link
      const blob = new Blob([result], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `users_export_${new Date().toISOString()}.csv`
      a.click()
      window.URL.revokeObjectURL(url)
      
      toast.success('Export réussi')
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de l\'export')
    }
  }

  // Configuration du template
  const config: EntityListConfig = {
    entityName: 'Utilisateur',
    entityNamePlural: 'Utilisateurs',
    title: viewMode === 'active' ? 'Gestion des Utilisateurs' : 'Utilisateurs Archivés',
    subtitle: viewMode === 'active' 
      ? 'Gérez les comptes utilisateurs de la plateforme'
      : 'Liste des utilisateurs archivés',
    icon: UserIcon,

    columns: [
      {
        key: 'username',
        label: 'Nom d\'utilisateur',
        sortable: true,
        render: (username: string, user: User) => (
          <div className="flex items-center gap-2">
            <div className="h-10 w-10 rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 flex items-center justify-center text-white text-sm font-semibold">
              {username[0]?.toUpperCase() || 'U'}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-medium text-gray-900">{username}</span>
                {user.new_user && <NewBadge />}
              </div>
              <div className="text-sm text-gray-500">{user.email}</div>
            </div>
          </div>
        ),
      },
      {
        key: 'roles',
        label: 'Rôles',
        render: (roles: string[]) => (
          <div className="flex flex-wrap gap-1">
            {roles.map((role) => {
              const color = RoleColors[role as keyof typeof RoleColors] || 'gray'
              return (
                <span
                  key={role}
                  className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-${color}-100 text-${color}-800`}
                >
                  {RoleLabels[role as keyof typeof RoleLabels] || role}
                </span>
              )
            })}
          </div>
        ),
      },
      {
        key: 'status',
        label: 'Statut',
        render: (status: string) => {
          const statusConfig: Record<string, { label: string; color: string }> = {
            active: { label: 'Actif', color: 'bg-green-100 text-green-700' },
            pending: { label: 'En attente', color: 'bg-yellow-100 text-yellow-700' },
            blocked: { label: 'Bloqué', color: 'bg-red-100 text-red-700' },
            archived: { label: 'Archivé', color: 'bg-gray-100 text-gray-700' },
          }
          const config = statusConfig[status] || statusConfig.pending
          return (
            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
              {config.label}
            </span>
          )
        },
      },
      {
        key: 'created_at',
        label: 'Créé le',
        sortable: true,
        render: (date: string) => new Date(date).toLocaleDateString('fr-FR'),
      },
    ],

    filters: [
      {
        key: 'status',
        label: 'Filtrer par statut',
        type: 'select',
        options: [
          { value: '', label: 'Tous les statuts' },
          { value: 'active', label: 'Actif' },
          { value: 'pending', label: 'En attente' },
          { value: 'blocked', label: 'Bloqué' },
        ],
        value: statusFilter,
        onChange: setStatusFilter,
      },
      {
        key: 'role',
        label: 'Filtrer par rôle',
        type: 'select',
        options: [
          { value: '', label: 'Tous les rôles' },
          { value: 'admin', label: 'Admin' },
          { value: 'commercial', label: 'Commercial' },
          { value: 'company', label: 'Entreprise' },
          { value: 'candidat', label: 'Candidat' },
        ],
        value: roleFilter,
        onChange: setRoleFilter,
      },
    ],

    actions: {
      create: {
        label: 'Créer un utilisateur',
        onClick: () => navigate('/admin/users/new'),
        permission: 'users.create',
      },
      row: [
        {
          key: 'view',
          label: 'Voir les détails',
          icon: EyeIcon,
          onClick: handleViewUser,
          variant: 'secondary',
          permission: 'users.read',
        },
        {
          key: 'edit',
          label: 'Modifier',
          icon: PencilIcon,
          onClick: handleEditUser,
          variant: 'primary',
          permission: 'users.edit',
        },
        {
          key: 'password',
          label: 'Modifier le mot de passe',
          icon: KeyIcon,
          onClick: handleResetPassword,
          variant: 'secondary',
          permission: 'users.manage',
          show: (user: User) => viewMode === 'active',
        },
        {
          key: 'reset_mfa',
          label: 'Réinitialiser MFA',
          icon: ShieldExclamationIcon,
          onClick: handleResetMfa,
          variant: 'secondary',
          permission: 'users.manage',
          show: (user: User) => viewMode === 'active' && user.mfa_enabled,
        },
        {
          key: 'activate',
          label: 'Activer',
          icon: CheckCircleIcon,
          onClick: handleActivateUser,
          variant: 'primary',
          permission: 'users.manage',
          show: (user: User) => user.status === 'blocked' || user.status === 'pending',
        },
        {
          key: 'block',
          label: 'Bloquer',
          icon: NoSymbolIcon,
          onClick: handleBlockUser,
          variant: 'danger',
          permission: 'users.manage',
          show: (user: User) => user.status === 'active' && viewMode === 'active',
        },
        {
          key: 'archive',
          label: 'Archiver',
          icon: ArchiveBoxIcon,
          onClick: handleArchiveUser,
          variant: 'secondary',
          permission: 'users.delete',
          show: (user: User) => viewMode === 'active',
        },
        {
          key: 'restore',
          label: 'Restaurer',
          icon: ArrowPathIcon,
          onClick: handleRestoreUser,
          variant: 'primary',
          permission: 'users.manage',
          show: (user: User) => viewMode === 'archived',
        },
        {
          key: 'delete',
          label: 'Supprimer',
          icon: TrashIcon,
          onClick: handleDeleteUser,
          variant: 'danger',
          permission: 'users.delete',
        },
      ],
      bulk: [
        {
          key: 'block',
          label: 'Bloquer',
          icon: NoSymbolIcon,
          onClick: handleBulkBlock,
          variant: 'danger',
          permission: 'users.manage',
        },
        {
          key: 'unblock',
          label: 'Débloquer',
          icon: CheckCircleIcon,
          onClick: handleBulkUnblock,
          variant: 'primary',
          permission: 'users.manage',
        },
        {
          key: 'archive',
          label: 'Archiver',
          icon: ArchiveBoxIcon,
          onClick: handleBulkArchive,
          variant: 'secondary',
          permission: 'users.delete',
        },
        {
          key: 'delete',
          label: 'Supprimer',
          icon: TrashIcon,
          onClick: handleBulkDelete,
          variant: 'danger',
          permission: 'users.delete',
        },
      ],
      custom: [
        {
          key: 'quick_add',
          label: 'Ajout Rapide',
          icon: UserPlusIcon,
          onClick: () => setShowQuickAddModal(true),
          variant: 'secondary',
          permission: 'users.create',
        },
        {
          key: 'bulk_import',
          label: 'Import CSV',
          icon: CloudArrowUpIcon,
          onClick: () => setShowBulkImportModal(true),
          variant: 'secondary',
          permission: 'users.create',
        },
        {
          key: 'export',
          label: 'Export CSV',
          icon: CloudArrowUpIcon,
          onClick: handleExportCSV,
          variant: 'secondary',
          permission: 'users.read',
        },
        {
          key: 'toggle_view',
          label: viewMode === 'active' ? 'Voir Archivés' : 'Voir Actifs',
          icon: viewMode === 'active' ? ArchiveBoxIcon : ArrowPathIcon,
          onClick: () => setViewMode(viewMode === 'active' ? 'archived' : 'active'),
          variant: 'secondary',
          permission: 'users.read',
        },
      ],
    },

    data: data?.users || [],
    isLoading,

    pagination: data?.pagination ? {
      currentPage: page,
      totalPages: Math.ceil(data.pagination.total / 15),
      onPageChange: setPage,
    } : undefined,

    onSearch: (query: string) => {
      setSearchQuery(query)
      setPage(1)
    },
    searchPlaceholder: 'Rechercher par nom, email...',

    selectedIds: selectedUserIds,
    onSelectionChange: setSelectedUserIds,

    emptyState: {
      message: viewMode === 'active' 
        ? 'Aucun utilisateur trouvé' 
        : 'Aucun utilisateur archivé',
      action: viewMode === 'active' ? {
        label: 'Créer le premier utilisateur',
        onClick: () => navigate('/admin/users/new'),
      } : undefined,
    },
  }

  return (
    <>
      <EntityListTemplate config={config} permissions={permissions} />

      {/* Modaux */}
      {selectedUser && (
        <>
          <EditUserModal
            isOpen={showEditModal}
            onClose={() => {
              setShowEditModal(false)
              setSelectedUser(null)
            }}
            user={selectedUser}
            onSuccess={refetch}
            profiles={profiles}
            groups={groups}
          />
          <DeleteUserModal
            isOpen={showDeleteModal}
            onClose={() => {
              setShowDeleteModal(false)
              setSelectedUser(null)
            }}
            user={selectedUser}
            onSuccess={refetch}
          />
          <BlockUserModal
            isOpen={showBlockModal}
            onClose={() => {
              setShowBlockModal(false)
              setSelectedUser(null)
            }}
            user={selectedUser}
            onSuccess={refetch}
          />
          <ResetMfaModal
            isOpen={showResetMfaModal}
            onClose={() => {
              setShowResetMfaModal(false)
              setSelectedUser(null)
            }}
            user={selectedUser}
            onSuccess={refetch}
          />
          <UserDetailModal
            isOpen={showDetailModal}
            onClose={() => {
              setShowDetailModal(false)
              setSelectedUser(null)
            }}
            user={selectedUser}
          />
          <ArchiveUserModal
            isOpen={showArchiveModal}
            onClose={() => {
              setShowArchiveModal(false)
              setSelectedUser(null)
            }}
            user={selectedUser}
            onSuccess={refetch}
          />
          <RestoreUserModal
            isOpen={showRestoreModal}
            onClose={() => {
              setShowRestoreModal(false)
              setSelectedUser(null)
            }}
            user={selectedUser}
            onSuccess={refetch}
          />
          <AdminUpdatePasswordModal
            isOpen={showPasswordModal}
            onClose={() => {
              setShowPasswordModal(false)
              setSelectedUser(null)
            }}
            user={selectedUser}
            onSuccess={refetch}
          />
        </>
      )}

      <QuickAddUserModal
        isOpen={showQuickAddModal}
        onClose={() => setShowQuickAddModal(false)}
        onSuccess={refetch}
      />

      <BulkImportUsersModal
        isOpen={showBulkImportModal}
        onClose={() => setShowBulkImportModal(false)}
        onSuccess={refetch}
      />
    </>
  )
}
