/**
 * Page Gestion Utilisateurs - Refactorisée avec EntityListTemplate
 * Configuration complète, zéro duplication
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import EntityListTemplate, { type EntityListConfig } from '@/templates/EntityListTemplate'
import { usePermissions } from '@/hooks/usePermission'
import {
  useGetUsersQuery,
  useDeleteUserMutation,
  type User,
} from '../api/usersApi'
import {
  UserGroupIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon,
  ShieldExclamationIcon,
} from '@heroicons/react/24/outline'
import { RoleLabels, RoleColors } from '@/constants/iamConstants'
import toast from 'react-hot-toast'

export default function UserManagementPageNew() {
  const navigate = useNavigate()
  const [page, setPage] = useState(1)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [roleFilter, setRoleFilter] = useState('')

  const { permissions } = usePermissions([
    'users.create',
    'users.read',
    'users.edit',
    'users.delete',
    'users.manage',
  ])

  const { data, isLoading, refetch } = useGetUsersQuery({
    page,
    page_size: 15,
    search: searchQuery || undefined,
    status: statusFilter || undefined,
    role: roleFilter || undefined,
  })

  const [deleteUser] = useDeleteUserMutation()

  const handleCreateUser = () => {
    navigate('/admin/users/create')
  }

  const handleViewUser = (user: User) => {
    navigate(`/admin/users/${user.id}`)
  }

  const handleEditUser = (user: User) => {
    navigate(`/admin/users/${user.id}/edit`)
  }

  const handleDeleteUser = async (user: User) => {
    if (!window.confirm(`Êtes-vous sûr de vouloir supprimer ${user.username} ?`)) {
      return
    }

    try {
      await deleteUser(user.id).unwrap()
      toast.success('Utilisateur supprimé avec succès')
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la suppression')
    }
  }

  const config: EntityListConfig = {
    entityName: 'Utilisateur',
    entityNamePlural: 'Utilisateurs',
    title: 'Gestion des Utilisateurs',
    subtitle: 'Gérez les utilisateurs de la plateforme',
    icon: UserGroupIcon,

    columns: [
      {
        key: 'username',
        label: 'Nom d\'utilisateur',
        sortable: true,
        render: (username: string, user: User) => (
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-full bg-gradient-to-r from-jlc-purple-600 to-indigo-600 flex items-center justify-center text-white text-sm font-semibold">
              {username[0]?.toUpperCase() || 'U'}
            </div>
            <div>
              <div className="font-medium text-gray-900">{username}</div>
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
            {roles?.map((role, idx) => (
              <span
                key={idx}
                className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                  RoleColors[role] || 'bg-gray-100 text-gray-700'
                }`}
              >
                {RoleLabels[role] || role}
              </span>
            ))}
          </div>
        ),
      },
      {
        key: 'status',
        label: 'Statut',
        render: (status: string) => {
          const statusConfig: Record<string, { label: string; color: string }> = {
            active: { label: 'Actif', color: 'bg-green-100 text-green-700' },
            inactive: { label: 'Inactif', color: 'bg-gray-100 text-gray-700' },
            blocked: { label: 'Bloqué', color: 'bg-red-100 text-red-700' },
            pending: { label: 'En attente', color: 'bg-yellow-100 text-yellow-700' },
          }
          const config = statusConfig[status] || statusConfig.inactive
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
          { value: 'inactive', label: 'Inactif' },
          { value: 'blocked', label: 'Bloqué' },
          { value: 'pending', label: 'En attente' },
        ],
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
      },
    ],

    actions: {
      create: {
        label: 'Créer un utilisateur',
        onClick: handleCreateUser,
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
          key: 'delete',
          label: 'Supprimer',
          icon: TrashIcon,
          onClick: handleDeleteUser,
          variant: 'danger',
          permission: 'users.delete',
          show: (user: User) => user.status !== 'active',
        },
      ],
    },

    data: data?.users || [],
    isLoading,

    pagination: data?.pagination
      ? {
          currentPage: page,
          totalPages: Math.ceil(data.pagination.total / 15),
          onPageChange: setPage,
        }
      : undefined,

    onSearch: setSearchQuery,
    searchPlaceholder: 'Rechercher par nom ou email...',

    emptyState: {
      message: 'Aucun utilisateur trouvé',
      action: {
        label: 'Créer le premier utilisateur',
        onClick: handleCreateUser,
      },
    },
  }

  return <EntityListTemplate config={config} permissions={permissions} />
}
