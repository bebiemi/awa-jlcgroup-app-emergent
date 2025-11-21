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
import { UsersPageConfig } from './users.config'
import EntityListTemplate from '@/templates/EntityListTemplate'
import { usePermissions } from '@/hooks/usePermission'
import type { EntityListConfig } from '@/templates/EntityListTemplate'

export default function UsersPage() {
  const navigate = useNavigate()
  const { permissions: userPermissions } = usePermissions([
    'users.view',
    'users.edit',
    'users.create',
    'users.delete',
    'users.bulk',
    'users.export',
  ])
  
  // États locaux pour les filtres et recherche
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [roleFilter, setRoleFilter] = useState('')

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
            active: 'bg-green-100 text-green-800',
            pending: 'bg-yellow-100 text-yellow-800',
            suspended: 'bg-red-100 text-red-800',
            deleted: 'bg-gray-100 text-gray-800',
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
        options: [
          { value: 'active', label: 'Actif' },
          { value: 'pending', label: 'En attente' },
          { value: 'suspended', label: 'Suspendu' },
          { value: 'deleted', label: 'Supprimé' },
        ],
      },
      {
        key: 'role',
        label: 'Rôle',
        type: 'select',
        options: [
          { value: 'admin', label: 'Admin' },
          { value: 'company', label: 'Entreprise' },
          { value: 'candidat', label: 'Candidat' },
          { value: 'interim', label: 'Intérimaire' },
        ],
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
          icon: require('@heroicons/react/24/outline').EyeIcon,
          onClick: (user) => openModal('details', user),
          variant: 'secondary',
        },
        {
          key: 'edit',
          label: 'Modifier',
          icon: require('@heroicons/react/24/outline').PencilIcon,
          onClick: (user) => openModal('edit', user),
          variant: 'primary',
          permission: 'users.edit',
        },
        {
          key: 'resetPassword',
          label: 'Réinitialiser mot de passe',
          icon: require('@heroicons/react/24/outline').KeyIcon,
          onClick: (user) => openModal('resetPassword', user),
          variant: 'secondary',
          permission: 'users.edit',
        },
        {
          key: 'resetMfa',
          label: 'Réinitialiser MFA',
          icon: require('@heroicons/react/24/outline').ShieldCheckIcon,
          onClick: (user) => openModal('resetMfa', user),
          variant: 'secondary',
          permission: 'users.edit',
        },
        {
          key: 'block',
          label: 'Bloquer',
          icon: require('@heroicons/react/24/outline').NoSymbolIcon,
          onClick: (user) => openModal('block', user),
          variant: 'danger',
          permission: 'users.edit',
          show: (user) => user.status !== 'suspended',
        },
        {
          key: 'archive',
          label: 'Archiver',
          icon: require('@heroicons/react/24/outline').ArchiveBoxIcon,
          onClick: (user) => openModal('archive', user),
          variant: 'danger',
          permission: 'users.delete',
          show: (user) => user.status !== 'deleted',
        },
        {
          key: 'restore',
          label: 'Restaurer',
          icon: require('@heroicons/react/24/outline').ArrowPathIcon,
          onClick: (user) => openModal('restore', user),
          variant: 'primary',
          permission: 'users.edit',
          show: (user) => user.status === 'deleted',
        },
        {
          key: 'delete',
          label: 'Supprimer',
          icon: require('@heroicons/react/24/outline').TrashIcon,
          onClick: (user) => openModal('delete', user),
          variant: 'danger',
          permission: 'users.delete',
        },
      ],
      bulk: [
        {
          key: 'bulkBlock',
          label: 'Bloquer sélection',
          onClick: (users) => console.log('Bulk block', users),
          variant: 'danger',
          permission: 'users.bulk',
        },
        {
          key: 'bulkArchive',
          label: 'Archiver sélection',
          onClick: (users) => console.log('Bulk archive', users),
          variant: 'danger',
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
  const permissions = {
    'users.view': hasPermission('users.view'),
    'users.edit': hasPermission('users.edit'),
    'users.create': hasPermission('users.create'),
    'users.delete': hasPermission('users.delete'),
    'users.bulk': hasPermission('users.bulk'),
    'users.export': hasPermission('users.export'),
  }

  // Récupération des composants modaux depuis la config
  const EditModal = UsersPageConfig.actions.edit
  const DeleteModal = UsersPageConfig.actions.delete
  const BlockModal = UsersPageConfig.actions.block
  const ArchiveModal = UsersPageConfig.actions.archive
  const RestoreModal = UsersPageConfig.actions.restore
  const ResetMfaModal = UsersPageConfig.actions.resetMfa
  const ResetPasswordModal = UsersPageConfig.actions.resetPassword
  const DetailsModal = UsersPageConfig.details.component

  return (
    <>
      <EntityListTemplate config={templateConfig} permissions={permissions} />
      
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
          isOpen={true}
          onClose={closeModal}
          userId={selectedUser.id}
        />
      )}
      
      {activeModal === 'block' && selectedUser && (
        <BlockModal
          isOpen={true}
          onClose={closeModal}
          userId={selectedUser.id}
        />
      )}
      
      {activeModal === 'archive' && selectedUser && (
        <ArchiveModal
          isOpen={true}
          onClose={closeModal}
          userId={selectedUser.id}
        />
      )}
      
      {activeModal === 'restore' && selectedUser && (
        <RestoreModal
          isOpen={true}
          onClose={closeModal}
          userId={selectedUser.id}
        />
      )}
      
      {activeModal === 'resetMfa' && selectedUser && (
        <ResetMfaModal
          isOpen={true}
          onClose={closeModal}
          userId={selectedUser.id}
        />
      )}
      
      {activeModal === 'resetPassword' && selectedUser && (
        <ResetPasswordModal
          isOpen={true}
          onClose={closeModal}
          userId={selectedUser.id}
        />
      )}
    </>
  )
}
