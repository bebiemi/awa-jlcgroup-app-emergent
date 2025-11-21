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
} from '../api/usersApi'

import EditUserModal from '../components/EditUserModal'
import DeleteUserModal from '../components/DeleteUserModal'
import BlockUserModal from '../components/BlockUserModal'
import RestoreUserModal from '../components/RestoreUserModal'
import ArchiveUserModal from '../components/ArchiveUserModal'
import UserDetailModal from '../components/UserDetailModal'
import ResetMfaModal from '../components/ResetMfaModal'
import AdminUpdatePasswordModal from '../components/AdminUpdatePasswordModal'

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
