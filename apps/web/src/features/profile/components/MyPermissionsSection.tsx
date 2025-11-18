import { useGetUserPermissionsQuery } from '@/features/iam/api/iamApi'
import { useAppSelector } from '@/store/hooks'
import { 
  ShieldCheckIcon, 
  UserGroupIcon, 
  BriefcaseIcon,
  LockClosedIcon 
} from '@heroicons/react/24/outline'

export default function MyPermissionsSection() {
  const currentUser = useAppSelector((state) => state.auth.user)
  const { data: permissionsData, isLoading, error } = useGetUserPermissionsQuery(
    currentUser?.id || '',
    { skip: !currentUser?.id }
  )

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-jlc-purple-600"></div>
      </div>
    )
  }

  if (error || !permissionsData) {
    return (
      <div className="text-center py-12">
        <ShieldCheckIcon className="h-12 w-12 text-gray-400 mx-auto mb-3" />
        <p className="text-gray-500">Impossible de charger vos permissions</p>
      </div>
    )
  }

  const { direct_profiles, group_profiles, all_permissions, groups } = permissionsData

  // Grouper les permissions par catégorie
  const permissionsByCategory = all_permissions.reduce((acc, perm) => {
    const category = perm.category || 'Autres'
    if (!acc[category]) {
      acc[category] = []
    }
    acc[category].push(perm)
    return acc
  }, {} as Record<string, typeof all_permissions>)

  return (
    <div className="space-y-6">
      {/* Introduction */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <ShieldCheckIcon className="h-5 w-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
          <div>
            <h3 className="text-sm font-semibold text-blue-900 mb-1">
              Vos permissions héritées
            </h3>
            <p className="text-sm text-blue-700">
              Cette page affiche toutes les permissions dont vous disposez via vos profils métiers et groupes. 
              Ces permissions sont en lecture seule et définies par votre administrateur.
            </p>
          </div>
        </div>
      </div>

      {/* Profils directs */}
      {direct_profiles.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-5">
          <div className="flex items-center mb-4">
            <BriefcaseIcon className="h-5 w-5 text-purple-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">
              Profils métiers attribués ({direct_profiles.length})
            </h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {direct_profiles.map((profile) => (
              <div 
                key={profile.id} 
                className="flex items-center p-3 bg-purple-50 border border-purple-200 rounded-lg"
              >
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{profile.name}</p>
                  {profile.description && (
                    <p className="text-sm text-gray-600 mt-1">{profile.description}</p>
                  )}
                  <p className="text-xs text-gray-500 mt-1">
                    {profile.permission_ids.length} permission(s)
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Groupes */}
      {groups.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-5">
          <div className="flex items-center mb-4">
            <UserGroupIcon className="h-5 w-5 text-blue-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">
              Groupes ({groups.length})
            </h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {groups.map((group) => (
              <div 
                key={group.id} 
                className="flex items-center p-3 bg-blue-50 border border-blue-200 rounded-lg"
              >
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{group.name}</p>
                  {group.description && (
                    <p className="text-sm text-gray-600 mt-1">{group.description}</p>
                  )}
                  <p className="text-xs text-gray-500 mt-1">
                    {group.profile_ids.length} profil(s) métier(s)
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Profils via groupes */}
      {group_profiles.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-5">
          <div className="flex items-center mb-4">
            <BriefcaseIcon className="h-5 w-5 text-indigo-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">
              Profils métiers hérités via les groupes ({group_profiles.length})
            </h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {group_profiles.map((profile) => (
              <div 
                key={profile.id} 
                className="flex items-center p-3 bg-indigo-50 border border-indigo-200 rounded-lg"
              >
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{profile.name}</p>
                  {profile.description && (
                    <p className="text-sm text-gray-600 mt-1">{profile.description}</p>
                  )}
                  <p className="text-xs text-gray-500 mt-1">
                    {profile.permission_ids.length} permission(s)
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Toutes les permissions par catégorie */}
      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <div className="flex items-center mb-4">
          <LockClosedIcon className="h-5 w-5 text-green-600 mr-2" />
          <h3 className="text-lg font-semibold text-gray-900">
            Détail des permissions ({all_permissions.length})
          </h3>
        </div>

        {Object.keys(permissionsByCategory).length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-8">
            Aucune permission n'est actuellement attribuée à votre compte.
          </p>
        ) : (
          <div className="space-y-6">
            {Object.entries(permissionsByCategory).map(([category, perms]) => (
              <div key={category}>
                <h4 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wide">
                  {category}
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                  {perms.map((perm) => (
                    <div
                      key={perm.id}
                      className="flex items-start p-2 bg-gray-50 border border-gray-200 rounded text-sm"
                    >
                      <LockClosedIcon className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-900 truncate">
                          {perm.name}
                        </p>
                        {perm.description && (
                          <p className="text-xs text-gray-600 mt-0.5 line-clamp-2">
                            {perm.description}
                          </p>
                        )}
                        <p className="text-xs text-gray-500 mt-1 font-mono">
                          {perm.code}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Message si aucune permission */}
      {all_permissions.length === 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start">
            <ShieldCheckIcon className="h-5 w-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" />
            <div>
              <h3 className="text-sm font-semibold text-yellow-900 mb-1">
                Aucune permission
              </h3>
              <p className="text-sm text-yellow-700">
                Votre compte n'a actuellement aucune permission attribuée. 
                Contactez votre administrateur si vous pensez qu'il s'agit d'une erreur.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
