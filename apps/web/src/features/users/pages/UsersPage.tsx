/**
 * Page de Gestion des Utilisateurs
 * Utilise EntityListTemplate avec users.config.ts
 * Architecture Config-Driven
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { 
  UsersIcon,
  EyeIcon,
  PencilIcon,
  KeyIcon,
  ShieldCheckIcon,
  NoSymbolIcon,
  ArchiveBoxIcon,
  ArrowPathIcon,
  TrashIcon,
} from '@heroicons/react/24/outline'
import { UsersPageConfig } from '../config/users.config'
import EntityListTemplate from '@/templates/EntityListTemplate'
import { usePermissions } from '@/hooks/usePermission'
import type { EntityListConfig } from '@/templates/EntityListTemplate'
import { CloudArrowUpIcon, PlusIcon, ArrowDownTrayIcon } from '@heroicons/react/24/outline'
import { useRoles, useUserStatuses } from '@/hooks/useAppConfig'
import { getRoleLabel } from '@/constants/iamConstants'

export default function UsersPage() {
  const navigate = useNavigate()
  const { permissions: userPermissions } = usePermissions([
    'users.read',
    'users.manage',
    'users.create',
    'users.delete',
    'users.manage_status',
    'users.reset_mfa',
  ])

  const roles = useRoles()
  const userStatuses = useUserStatuses()
  
  // États locaux pour les filtres et recherche
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const [activeTab, setActiveTab] = useState<'all' | 'archived' | 'super_admin'>('all')

  // RTK Query pour récupérer les utilisateurs
  const { data, isLoading, error } = UsersPageConfig.api.list({
    page,
    page_size: 15,
    search: search || undefined,
    status: statusFilter || undefined,
    role: roleFilter || undefined,
  })

  // États pour les modales
  const [selectedUser, setSelectedUser] = useState<any>(null)
  const [activeModal, setActiveModal] = useState<string | null>(null)

  const roleOptions = Array.from(
    new Set(
      [
        roles.super_admin,
        roles.admin,
        roles.company,
        roles.interim,
        roles.agency,
        roles.commercial,
        roles.validator,
      ].filter(Boolean)
    )
  ).map((role) => ({
    value: role,
    label: getRoleLabel(role),
  }))

  const statusLabelMap: Record<string, string> = {
    [userStatuses.active]: 'Actif',
    [userStatuses.pending]: 'En attente',
    [userStatuses.suspended]: 'Suspendu',
    [userStatuses.deleted]: 'Archivé',
    [userStatuses.blocked]: 'Bloqué',
    [userStatuses.archived]: 'Archivé',
  }

  const statusOptions = Array.from(
    new Set(
      [
        userStatuses.active,
        userStatuses.pending,
        userStatuses.suspended,
        userStatuses.deleted,
        userStatuses.blocked,
        userStatuses.archived,
      ].filter(Boolean)
    )
  ).map((status) => ({
    value: status,
    label: statusLabelMap[status] || status,
  }))

  // Ouvrir une modale
  const openModal = (modalName: string, user: any) => {
    setSelectedUser(user)
    setActiveModal(modalName)
  }

  // Fermer toutes les modales
  const closeModal = () => {
    setActiveModal(null)
    setSelectedUser(null)
  }

  // Rendu des colonnes avec badges pour le statut
    const renderColumns = UsersPageConfig.columns.map((col) => ({
      ...col,
      render: col.key === 'status'
        ? (value: string) => {
            const statusColors: Record<string, string> = {
              [userStatuses.active]: 'bg-green-100 text-green-800',
              [userStatuses.pending]: 'bg-yellow-100 text-yellow-800',
              [userStatuses.suspended]: 'bg-red-100 text-red-800',
              [userStatuses.deleted]: 'bg-gray-100 text-gray-800',
              [userStatuses.blocked]: 'bg-orange-100 text-orange-800',
              [userStatuses.archived]: 'bg-gray-100 text-gray-800',
            }
            return (
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[value] || 'bg-gray-100 text-gray-800'}`}>
                {value}
              </span>
            )
          }
        : col.key === 'created_at'
      ? (value: string) => new Date(value).toLocaleDateString('fr-FR')
      : undefined
    }))

  // Configuration adaptée pour EntityListTemplate
  const templateConfig: EntityListConfig = {
    entityName: 'Utilisateur',
    entityNamePlural: 'Utilisateurs',
    title: UsersPageConfig.title,
    icon: UsersIcon,
    
    columns: renderColumns,
    
    data: data?.users || [],
    isLoading,
    error,
    
    pagination: data?.pagination ? {
      currentPage: data.pagination.page,
      totalPages: data.pagination.total_pages,
      onPageChange: setPage,
    } : undefined,
    
    onSearch: setSearch,
    searchPlaceholder: 'Rechercher par nom ou email...',
    
    filters: [
      {
        key: 'status',
        label: 'Statut',
        type: 'select',
        options: statusOptions,
      },
      {
        key: 'role',
        label: 'Rôle',
        type: 'select',
        options: roleOptions,
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
          onClick: (user) => openModal('details', user),
          variant: 'secondary' as const,
        },
        {
          key: 'edit',
          label: 'Modifier',
          icon: PencilIcon,
          onClick: (user) => openModal('edit', user),
          variant: 'primary' as const,
          permission: 'users.edit',
        },
        {
          key: 'resetPassword',
          label: 'Réinitialiser mot de passe',
          icon: KeyIcon,
          onClick: (user) => openModal('resetPassword', user),
          variant: 'secondary' as const,
          permission: 'users.edit',
        },
        {
          key: 'resetMfa',
          label: 'Réinitialiser MFA',
          icon: ShieldCheckIcon,
          onClick: (user) => openModal('resetMfa', user),
          variant: 'secondary' as const,
          permission: 'users.edit',
        },
        {
          key: 'block',
          label: 'Bloquer',
          icon: NoSymbolIcon,
          onClick: (user) => openModal('block', user),
          variant: 'danger' as const,
          permission: 'users.edit',
          show: (user) => user.status !== 'suspended',
        },
        {
          key: 'archive',
          label: 'Archiver',
          icon: ArchiveBoxIcon,
          onClick: (user) => openModal('archive', user),
          variant: 'danger' as const,
          permission: 'users.delete',
          show: (user) => user.status !== 'deleted',
        },
        {
          key: 'restore',
          label: 'Restaurer',
          icon: ArrowPathIcon,
          onClick: (user) => openModal('restore', user),
          variant: 'primary' as const,
          permission: 'users.edit',
          show: (user) => user.status === 'deleted',
        },
        {
          key: 'delete',
          label: 'Supprimer',
          icon: TrashIcon,
          onClick: (user) => openModal('delete', user),
          variant: 'danger' as const,
          permission: 'users.delete',
        },
      ],
      bulk: [
        {
          key: 'bulkBlock',
          label: 'Bloquer sélection',
          onClick: (users) => console.log('Bulk block', users),
          variant: 'danger' as const,
          permission: 'users.bulk',
        },
        {
          key: 'bulkArchive',
          label: 'Archiver sélection',
          onClick: (users) => console.log('Bulk archive', users),
          variant: 'danger' as const,
          permission: 'users.bulk',
        },
      ],
    },
    
    emptyState: {
      message: 'Aucun utilisateur trouvé',
      action: {
        label: 'Créer le premier utilisateur',
        onClick: () => navigate('/admin/users/new'),
      },
    },
  }

  // Permissions pour le template
  const permissions = userPermissions

  // Récupération des composants modaux depuis la config
  const EditModal = UsersPageConfig.actions.edit
  const DeleteModal = UsersPageConfig.actions.delete
  const BlockModal = UsersPageConfig.actions.block
  const ArchiveModal = UsersPageConfig.actions.archive
  const RestoreModal = UsersPageConfig.actions.restore
  const ResetMfaModal = UsersPageConfig.actions.resetMfa
  const ResetPasswordModal = UsersPageConfig.actions.resetPassword
  const DetailsModal = UsersPageConfig.details.component

  const filtersAndActions = (
    <div className="flex flex-wrap gap-2 items-center justify-between w-full">
      <div className="flex flex-wrap gap-2">
        {[
          { key: 'all', label: 'Tous' },
          { key: 'archived', label: 'Archivés' },
          { key: 'super_admin', label: 'Super Admins' },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => {
              setActiveTab(tab.key as typeof activeTab)
              if (tab.key === 'archived') {
                setStatusFilter('deleted')
              } else {
                setStatusFilter('')
              }
              if (tab.key === 'super_admin') {
                setRoleFilter('super_admin')
              } else if (tab.key !== 'archived') {
                setRoleFilter('')
              }
              setPage(1)
            }}
            className={[
              'px-3 py-2 rounded-lg text-sm font-medium transition-colors',
              activeTab === tab.key
                ? 'bg-jlc-purple-600 text-white'
                : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50',
            ].join(' ')}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div className="flex items-center gap-2 flex-wrap">
        <button
          type="button"
          onClick={() => navigate('/admin/users/import')}
          className="h-10 w-10 md:h-11 md:w-11 inline-flex items-center justify-center rounded-full text-white shadow-md transition-all"
          style={{ background: 'var(--sidebar-accent-secondary, #16a34a)' }}
          title="Importer des utilisateurs"
          aria-label="Importer des utilisateurs"
        >
          <CloudArrowUpIcon className="h-5 w-5" />
        </button>
        <button
          type="button"
          onClick={() => navigate('/admin/users/export')}
          className="h-10 w-10 md:h-11 md:w-11 inline-flex items-center justify-center rounded-full text-white shadow-md transition-all"
          style={{ background: 'var(--sidebar-accent, #4f46e5)' }}
          title="Exporter les utilisateurs"
          aria-label="Exporter les utilisateurs"
        >
          <ArrowDownTrayIcon className="h-5 w-5" />
        </button>
        <button
          type="button"
          onClick={() => navigate('/admin/users/new')}
          className="h-10 w-10 md:h-11 md:w-11 inline-flex items-center justify-center rounded-full text-white shadow-md transition-all"
          style={{ background: 'var(--sidebar-accent-gradient, linear-gradient(90deg,#6d28d9,#4f46e5))' }}
          title="Créer un utilisateur"
          aria-label="Créer un utilisateur"
        >
          <PlusIcon className="h-5 w-5" />
        </button>
      </div>
    </div>
  )

  return (
    <>
      <EntityListTemplate
        config={{
          ...templateConfig,
          extraFiltersSlot: filtersAndActions,
          inlineActionsSlot: undefined,
          showCreateInHeader: false,
        }}
        permissions={permissions}
      />
      
      {/* Modales conditionnelles */}
      {activeModal === 'details' && selectedUser && (
        <DetailsModal
          isOpen={true}
          onClose={closeModal}
          userId={selectedUser.id}
        />
      )}
      
      {activeModal === 'edit' && selectedUser && (
        <EditModal
          isOpen={true}
          onClose={closeModal}
          user={selectedUser}
        />
      )}
      
      {activeModal === 'delete' && selectedUser && (
        <DeleteModal
          user={selectedUser}
          isOpen={true}
          onClose={closeModal}
        />
      )}
      
      {activeModal === 'block' && selectedUser && (
        <BlockModal
          user={selectedUser}
          isOpen={true}
          onClose={closeModal}
        />
      )}
      
      {activeModal === 'archive' && selectedUser && (
        <ArchiveModal
          user={selectedUser}
          isOpen={true}
          onClose={closeModal}
        />
      )}
      
      {activeModal === 'restore' && selectedUser && (
        <RestoreModal
          user={selectedUser}
          isOpen={true}
          onClose={closeModal}
        />
      )}
      
      {activeModal === 'resetMfa' && selectedUser && (
        <ResetMfaModal
          user={selectedUser}
          isOpen={true}
          onClose={closeModal}
        />
      )}
      
      {activeModal === 'resetPassword' && selectedUser && (
        <ResetPasswordModal
          isOpen={true}
          onClose={closeModal}
          userId={selectedUser.id}
          username={selectedUser.username || selectedUser.email}
          onSuccess={closeModal}
        />
      )}
    </>
  )
}
