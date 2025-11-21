import { UserDetail } from '@/features/users/api/userDetailsApi'
import { USER_STATUS_CONFIG, BADGE_VARIANTS } from '@/constants/ui'
import { getRoleLabel, getRoleColor } from '@/constants/iamConstants'

interface UserInfoTabProps {
  userId: string
  userDetail: UserDetail
}

export default function UserInfoTab({ userDetail }: UserInfoTabProps) {
  return (
    <div className="space-y-6">
      {/* Informations Personnelles */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Informations Personnelles</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-gray-500">Nom complet</label>
            <p className="text-gray-900 mt-1">{userDetail.full_name || '-'}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Nom d'utilisateur</label>
            <p className="text-gray-900 mt-1">{userDetail.username}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Email</label>
            <p className="text-gray-900 mt-1">{userDetail.email}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Téléphone</label>
            <p className="text-gray-900 mt-1">{userDetail.phone || '-'}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Localisation</label>
            <p className="text-gray-900 mt-1">{userDetail.location_label || '-'}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Fournisseur</label>
            <p className="text-gray-900 mt-1">{userDetail.provider}</p>
          </div>
        </div>
      </div>

      {/* Statut du Compte */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Statut du Compte</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-gray-500">Statut</label>
            <div className="mt-1">
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${
                USER_STATUS_CONFIG[userDetail.status as keyof typeof USER_STATUS_CONFIG]?.color || BADGE_VARIANTS.neutral
              }`}>
                {USER_STATUS_CONFIG[userDetail.status as keyof typeof USER_STATUS_CONFIG]?.icon || '○'}
                <span className="ml-1">
                  {USER_STATUS_CONFIG[userDetail.status as keyof typeof USER_STATUS_CONFIG]?.label || userDetail.status}
                </span>
              </span>
            </div>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Rôles</label>
            <div className="mt-1 flex flex-wrap gap-2">
              {userDetail.roles.map((role) => (
                <span key={role} className={`px-2 py-1 rounded text-xs font-semibold ${getRoleColor(role)}`}>
                  {getRoleLabel(role)}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Sécurité */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Sécurité</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-gray-500">Authentification 2FA</label>
            <div className="mt-1">
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${
                userDetail.mfa_enabled ? BADGE_VARIANTS.success : BADGE_VARIANTS.neutral
              }`}>
                {userDetail.mfa_enabled ? '🔐 Activé' : '○ Désactivé'}
                {userDetail.mfa_method && ` (${userDetail.mfa_method})`}
              </span>
            </div>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Email vérifié</label>
            <div className="mt-1">
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${
                userDetail.is_verified ? BADGE_VARIANTS.success : BADGE_VARIANTS.warning
              }`}>
                {userDetail.is_verified ? '✓ Vérifié' : '⚠️ Non vérifié'}
              </span>
            </div>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Tentatives de connexion échouées</label>
            <p className="text-gray-900 mt-1">{userDetail.failed_login_attempts || 0}</p>
          </div>
        </div>
      </div>

      {/* Activité */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Activité</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-gray-500">Date de création</label>
            <p className="text-gray-900 mt-1">
              {new Date(userDetail.created_at).toLocaleString('fr-FR')}
            </p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Dernière mise à jour</label>
            <p className="text-gray-900 mt-1">
              {new Date(userDetail.updated_at).toLocaleString('fr-FR')}
            </p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Dernière connexion</label>
            <p className="text-gray-900 mt-1">
              {userDetail.last_login_at 
                ? new Date(userDetail.last_login_at).toLocaleString('fr-FR')
                : 'Jamais'}
            </p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Nombre de connexions</label>
            <p className="text-gray-900 mt-1">{userDetail.login_count || 0}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
