/**
 * Module Users - Exports
 * Architecture Config-Driven
 */

// Page principale
export { default as UsersPage } from './pages/UsersPage'

// Configuration
export { UsersPageConfig } from './config/users.config'

// API
export * from './api/usersApi'

// Composants (si besoin d'être réutilisés ailleurs)
export { default as EditUserModal } from './components/EditUserModal'
export { default as DeleteUserModal } from './components/DeleteUserModal'
export { default as BlockUserModal } from './components/BlockUserModal'
export { default as ArchiveUserModal } from './components/ArchiveUserModal'
export { default as RestoreUserModal } from './components/RestoreUserModal'
export { default as UserDetailModal } from './components/UserDetailModal'
export { default as ResetMfaModal } from './components/ResetMfaModal'
export { default as AdminUpdatePasswordModal } from './components/AdminUpdatePasswordModal'
