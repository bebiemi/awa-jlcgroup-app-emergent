import { useListPermissionsQuery } from '../api/iamApi'
import { useCanReadPermissions } from '../useCanReadPermissions'
import { LockClosedIcon } from '@heroicons/react/24/outline'

interface ProfilePermissionsDisplayProps {
  permissionIds: string[]
  profileName: string
}

export default function ProfilePermissionsDisplay({ permissionIds, profileName }: ProfilePermissionsDisplayProps) {
  const { canReadPermissions } = useCanReadPermissions()
  const { data: allPermissions = [], isLoading } = useListPermissionsQuery(undefined, {
    skip: !canReadPermissions,
  })

  if (isLoading) {
    return (
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="animate-pulse space-y-2">
          <div className="h-4 bg-gray-200 rounded w-1/3"></div>
          <div className="h-3 bg-gray-200 rounded w-1/2"></div>
          <div className="h-3 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    )
  }

  // Filtrer les permissions du profil
  const profilePermissions = allPermissions.filter((perm: any) => 
    permissionIds.includes(perm.id)
  )

  // Grouper par catégorie
  const permissionsByCategory = profilePermissions.reduce((acc: any, perm: any) => {
    const category = perm.category || 'Autres'
    if (!acc[category]) {
      acc[category] = []
    }
    acc[category].push(perm)
    return acc
  }, {})

  if (profilePermissions.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg p-4 border-2 border-dashed border-gray-300">
        <p className="text-sm text-gray-500 text-center">
          Aucune permission directe pour ce profil
        </p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h4 className="text-base font-semibold text-gray-900">
            Permissions du profil
          </h4>
          <p className="text-sm text-gray-500 mt-1">
            {profilePermissions.length} permission(s) directe(s) pour <span className="font-medium">{profileName}</span>
          </p>
        </div>
        <span className="px-3 py-1 text-sm font-bold bg-green-100 text-green-700 rounded-full">
          {profilePermissions.length}
        </span>
      </div>

      {Object.keys(permissionsByCategory).length > 0 && (
        <div className="space-y-4">
          {Object.entries(permissionsByCategory).map(([category, perms]: [string, any]) => (
            <div key={category}>
              <h5 className="text-xs font-semibold text-gray-700 uppercase tracking-wide mb-2 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-green-500"></span>
                {category}
              </h5>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {perms.map((perm: any) => (
                  <div
                    key={perm.id}
                    className="flex items-start p-3 bg-green-50 border border-green-200 rounded-lg hover:shadow-sm transition-shadow"
                  >
                    <LockClosedIcon className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900">
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
  )
}
