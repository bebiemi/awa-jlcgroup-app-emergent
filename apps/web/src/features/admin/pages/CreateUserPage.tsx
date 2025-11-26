import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout from '@/components/Layout'
import Card from '@/components/Card'
import {
  useCreateUserMutation,
  useGetGroupsQuery,
  useGetProfilesQuery,
} from '../api/securityApi'
import {
  UserPlusIcon,
  KeyIcon,
  ShieldCheckIcon,
  UserGroupIcon,
  ArrowLeftIcon,
  EyeIcon,
  EyeSlashIcon,
} from '@heroicons/react/24/outline'
import { Link } from 'react-router-dom'
import { useRoles } from '@/hooks/useAppConfig'

export default function CreateUserPage() {
  const navigate = useNavigate()
  const [createUser, { isLoading }] = useCreateUserMutation()
  const { data: groups } = useGetGroupsQuery()
  const { data: profiles } = useGetProfilesQuery()
  const roles = useRoles()

  const [formData, setFormData] = useState({
    email: '',
    username: '',
    full_name: '',
    password: '',
    useGeneratedPassword: true,
    roles: [] as string[],
    group_ids: [] as string[],
    profile_id: '',
    send_invitation: true,
  })
  const [showPassword, setShowPassword] = useState(false)
  const [generatedPassword, setGeneratedPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  const generatePassword = () => {
    const length = 12
    const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*'
    let password = ''
    for (let i = 0; i < length; i++) {
      password += charset.charAt(Math.floor(Math.random() * charset.length))
    }
    setGeneratedPassword(password)
    setFormData({ ...formData, password: password })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!formData.email.trim()) {
      setError('L\'email est requis')
      return
    }

    if (!formData.useGeneratedPassword && !formData.password.trim()) {
      setError('Le mot de passe est requis')
      return
    }

    try {
      const userData = {
        email: formData.email,
        username: formData.username || undefined,
        full_name: formData.full_name || undefined,
        password: formData.useGeneratedPassword ? undefined : formData.password,
        roles: formData.roles,
        group_ids: formData.group_ids,
        profile_id: formData.profile_id || undefined,
        send_invitation: formData.send_invitation,
      }

      await createUser(userData).unwrap()
      setSuccess(true)

      setTimeout(() => {
        navigate('/admin/users')
      }, 2000)
    } catch (err: any) {
      setError(err?.data?.detail || 'Erreur lors de la création de l\'utilisateur')
    }
  }

  const toggleRole = (role: string) => {
    setFormData((prev) => ({
      ...prev,
      roles: prev.roles.includes(role) ? prev.roles.filter((r) => r !== role) : [...prev.roles, role],
    }))
  }

  const toggleGroup = (groupId: string) => {
    setFormData((prev) => ({
      ...prev,
      group_ids: prev.group_ids.includes(groupId)
        ? prev.group_ids.filter((id) => id !== groupId)
        : [...prev.group_ids, groupId],
    }))
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Link
            to="/admin/users"
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeftIcon className="h-5 w-5 text-gray-600" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Créer un utilisateur</h1>
            <p className="mt-2 text-gray-600">Remplissez tous les détails pour créer un compte complet</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <Card>
            <div className="flex items-center gap-3 mb-4">
              <UserPlusIcon className="h-6 w-6 text-jlc-purple-600" />
              <h2 className="text-xl font-semibold text-gray-900">Informations de base</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Email */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email *
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
                  placeholder="utilisateur@example.com"
                  required
                />
              </div>

              {/* Full Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nom complet
                </label>
                <input
                  type="text"
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
                  placeholder="Prénom Nom"
                />
              </div>

              {/* Username */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nom d'utilisateur
                </label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
                  placeholder="Auto-généré depuis l'email si vide"
                />
                <p className="text-xs text-gray-500 mt-1">Laissez vide pour générer automatiquement</p>
              </div>
            </div>
          </Card>

          {/* Authentication */}
          <Card>
            <div className="flex items-center gap-3 mb-4">
              <KeyIcon className="h-6 w-6 text-jlc-purple-600" />
              <h2 className="text-xl font-semibold text-gray-900">Authentification</h2>
            </div>

            <div className="space-y-4">
              {/* Password Options */}
              <div className="flex items-center gap-4">
                <label className="flex items-center cursor-pointer">
                  <input
                    type="radio"
                    checked={formData.useGeneratedPassword}
                    onChange={() => {
                      setFormData({ ...formData, useGeneratedPassword: true, password: '' })
                      setGeneratedPassword('')
                    }}
                    className="h-4 w-4 text-jlc-purple-600 focus:ring-jlc-purple-500 border-gray-300"
                  />
                  <span className="ml-2 text-sm text-gray-700">Générer automatiquement</span>
                </label>
                <label className="flex items-center cursor-pointer">
                  <input
                    type="radio"
                    checked={!formData.useGeneratedPassword}
                    onChange={() => setFormData({ ...formData, useGeneratedPassword: false })}
                    className="h-4 w-4 text-jlc-purple-600 focus:ring-jlc-purple-500 border-gray-300"
                  />
                  <span className="ml-2 text-sm text-gray-700">Définir manuellement</span>
                </label>
              </div>

              {/* Manual Password */}
              {!formData.useGeneratedPassword && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Mot de passe *
                  </label>
                  <div className="relative">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={formData.password}
                      onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                      className="w-full px-4 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
                      placeholder="Minimum 8 caractères"
                      minLength={8}
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      {showPassword ? (
                        <EyeSlashIcon className="h-5 w-5" />
                      ) : (
                        <EyeIcon className="h-5 w-5" />
                      )}
                    </button>
                  </div>
                </div>
              )}

              {/* Send Invitation */}
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.send_invitation}
                  onChange={(e) => setFormData({ ...formData, send_invitation: e.target.checked })}
                  className="h-4 w-4 text-jlc-purple-600 focus:ring-jlc-purple-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-700">
                  Envoyer un email d'invitation avec les identifiants
                </span>
              </label>
            </div>
          </Card>

          {/* Roles */}
          <Card>
            <div className="flex items-center gap-3 mb-4">
              <ShieldCheckIcon className="h-6 w-6 text-jlc-purple-600" />
              <h2 className="text-xl font-semibold text-gray-900">Rôles directs</h2>
            </div>

            <div className="space-y-2">
              {[roles.admin, roles.super_admin, roles.interim, roles.company, roles.agency]
                .filter(Boolean)
                .map((role) => (
                  <label key={role} className="flex items-center cursor-pointer hover:bg-gray-50 p-2 rounded">
                    <input
                      type="checkbox"
                      checked={formData.roles.includes(role)}
                      onChange={() => toggleRole(role)}
                      className="h-4 w-4 text-jlc-purple-600 focus:ring-jlc-purple-500 border-gray-300 rounded"
                    />
                    <span className="ml-3 text-sm text-gray-700 capitalize">{role}</span>
                  </label>
                ))}
            </div>
          </Card>

          {/* Groups */}
          <Card>
            <div className="flex items-center gap-3 mb-4">
              <UserGroupIcon className="h-6 w-6 text-jlc-purple-600" />
              <h2 className="text-xl font-semibold text-gray-900">Groupes</h2>
            </div>

            {groups && groups.length > 0 ? (
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {groups.map((group) => (
                  <label
                    key={group.id}
                    className="flex items-start cursor-pointer hover:bg-gray-50 p-3 rounded border border-gray-200"
                  >
                    <input
                      type="checkbox"
                      checked={formData.group_ids.includes(group.id)}
                      onChange={() => toggleGroup(group.id)}
                      className="h-4 w-4 text-jlc-purple-600 focus:ring-jlc-purple-500 border-gray-300 rounded mt-0.5"
                    />
                    <div className="ml-3">
                      <span className="text-sm font-medium text-gray-900">{group.name}</span>
                      {group.description && (
                        <p className="text-xs text-gray-500 mt-0.5">{group.description}</p>
                      )}
                      <p className="text-xs text-gray-500 mt-1">
                        {group.member_ids.length} membre(s)
                      </p>
                    </div>
                  </label>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">Aucun groupe disponible</p>
            )}
          </Card>

          {/* Direct Profile Assignment */}
          <Card>
            <div className="flex items-center gap-3 mb-4">
              <ShieldCheckIcon className="h-6 w-6 text-jlc-purple-600" />
              <h2 className="text-xl font-semibold text-gray-900">Profil de permissions (optionnel)</h2>
            </div>

            <p className="text-sm text-gray-600 mb-4">
              Assignez un profil directement à cet utilisateur en plus des permissions héritées des groupes
            </p>

            {profiles && profiles.length > 0 ? (
              <select
                value={formData.profile_id}
                onChange={(e) => setFormData({ ...formData, profile_id: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              >
                <option value="">Aucun profil direct</option>
                {profiles.map((profile) => (
                  <option key={profile.id} value={profile.id}>
                    {profile.name} {profile.is_system ? '(Système)' : ''} - {profile.permissions.length} permission(s)
                  </option>
                ))}
              </select>
            ) : (
              <p className="text-sm text-gray-500">Aucun profil disponible</p>
            )}
          </Card>

          {/* Error/Success Messages */}
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {success && (
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-sm text-green-600">
                ✓ Utilisateur créé avec succès ! Redirection en cours...
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-4 pt-4">
            <Link
              to="/admin/users"
              className="flex-1 px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-center font-medium"
            >
              Annuler
            </Link>
            <button
              type="submit"
              disabled={isLoading || success}
              className="flex-1 px-6 py-3 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {isLoading ? 'Création en cours...' : 'Créer l\'utilisateur'}
            </button>
          </div>
        </form>
      </div>
    </Layout>
  )
}
