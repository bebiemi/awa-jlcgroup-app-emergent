/**
 * Configuration de la page de gestion des utilisateurs
 * Architecture Config-Driven - Zéro duplication
 */

import {
  useGetUsersQuery,
  useUpdateUserMutation,
  useDeleteUserMutation,
  useBulkBlockUsersMutation,
  useBulkUnblockUsersMutation,
  useBulkArchiveUsersMutation,
  useBulkDeleteUsersMutation,
  useExportUsersCSVMutation,
} from '@/features/admin/api/usersApi'

import EditUserModal from '@/features/admin/components/EditUserModal'
import DeleteUserModal from '@/features/admin/components/DeleteUserModal'
import BlockUserModal from '@/features/admin/components/BlockUserModal'
import RestoreUserModal from '@/features/admin/components/RestoreUserModal'
import ArchiveUserModal from '@/features/admin/components/ArchiveUserModal'
import UserDetailModal from '@/features/admin/components/UserDetailModal'
import ResetMfaModal from '@/features/admin/components/ResetMfaModal'
import AdminUpdatePasswordModal from '@/features/admin/components/AdminUpdatePasswordModal'

export const UsersPageConfig = {
  /** ------------------------------
   *   TITRE ⟶ affiché dans le header
   *  ------------------------------ */
  title: "Gestion des utilisateurs",

  /** ------------------------------
   *  APIs génériques du template
   *  ------------------------------ */
  api: {
    list: useGetUsersQuery,
    update: useUpdateUserMutation,
    delete: useDeleteUserMutation,
    bulkBlock: useBulkBlockUsersMutation,
    bulkUnblock: useBulkUnblockUsersMutation,
    bulkArchive: useBulkArchiveUsersMutation,
    bulkDelete: useBulkDeleteUsersMutation,
    export: useExportUsersCSVMutation,
  },

  /** ------------------------------
   *   Permissions IAM
   *   (utilisées par EntityListTemplate)
   *  ------------------------------ */
  permissions: {
    view: "users.view",
    edit: "users.edit",
    delete: "users.delete",
    bulk: "users.bulk",
    export: "users.export",
  },

  /** ------------------------------
   *   Colonnes du tableau
   *  ------------------------------ */
  columns: [
    { key: "full_name", label: "Nom", sortable: true },
    { key: "email", label: "Email", sortable: true },
    { key: "status", label: "Statut", badge: true },
    { key: "created_at", label: "Date d'inscription", sortable: true },
  ],

  /** ------------------------------
   *   Modale de Détails
   *  ------------------------------ */
  details: {
    component: UserDetailModal,
  },

  /** ------------------------------
   *   Modales Actions (Edit/Delete/etc)
   *  ------------------------------ */
  actions: {
    edit: EditUserModal,
    block: BlockUserModal,
    archive: ArchiveUserModal,
    delete: DeleteUserModal,
    restore: RestoreUserModal,
    resetMfa: ResetMfaModal,
    resetPassword: AdminUpdatePasswordModal,
  },
}
