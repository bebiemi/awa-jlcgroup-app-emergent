import { useState } from 'react'
import { UserDetail, useGetUserActivityQuery } from '@/features/users/api/userDetailsApi'
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline'
import { usePermissions } from '@/hooks/usePermission'

interface UserActivityTabProps {
  userId: string
  userDetail: UserDetail
}

export default function UserActivityTab({ userId }: UserActivityTabProps) {
  const [page, setPage] = useState(1)
  const { data, isLoading } = useGetUserActivityQuery({ userId, page, page_size: 20 })
  const { permissions } = usePermissions(['users.read', 'users.manage', 'audit.read'])

  const activities = data?.activities || []
  const total = data?.total || 0

  const getActionIcon = (action: string) => {
    const icons: Record<string, string> = {
      login: '🔐',
      logout: '🚪',
      create: '➕',
      update: '✏️',
      delete: '🗑️',
      view: '👁️',
      upload: '📤',
      download: '📥',
    }
    return icons[action] || '•'
  }

  const getActionColor = (action: string) => {
    const colors: Record<string, string> = {
      login: 'text-green-600',
      logout: 'text-gray-600',
      create: 'text-blue-600',
      update: 'text-yellow-600',
      delete: 'text-red-600',
      view: 'text-purple-600',
      upload: 'text-indigo-600',
      download: 'text-teal-600',
    }
    return colors[action] || 'text-gray-600'
  }

  const canReadActivity = permissions['users.read'] || permissions['users.manage'] || permissions['audit.read']
  if (!canReadActivity) return null

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-4">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="h-20 bg-gray-200 rounded-lg"></div>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {activities.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-gray-500">Aucune activité enregistrée</p>
        </div>
      ) : (
        <>
          <div className="bg-white rounded-lg shadow">
            <div className="divide-y divide-gray-200">
              {activities.map((activity, index) => (
                <div key={activity.id} className="p-4 hover:bg-gray-50 transition">
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0">
                      <span className={`text-2xl ${getActionColor(activity.action)}`}>
                        {getActionIcon(activity.action)}
                      </span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-gray-900">
                          {activity.action}
                          {activity.resource_type && (
                            <span className="ml-2 text-gray-500">
                              sur {activity.resource_type}
                            </span>
                          )}
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(activity.created_at).toLocaleString('fr-FR')}
                        </p>
                      </div>
                      {activity.ip_address && (
                        <p className="text-xs text-gray-500 mt-1">
                          IP: {activity.ip_address}
                        </p>
                      )}
                      {activity.metadata && Object.keys(activity.metadata).length > 0 && (
                        <details className="mt-2">
                          <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-700">
                            Détails
                          </summary>
                          <pre className="text-xs bg-gray-100 p-2 rounded mt-1 overflow-auto">
                            {JSON.stringify(activity.metadata, null, 2)}
                          </pre>
                        </details>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Pagination */}
          {total > 20 && (
            <div className="flex items-center justify-between bg-white rounded-lg shadow px-4 py-3">
              <p className="text-sm text-gray-700">
                Affichage de {(page - 1) * 20 + 1} à {Math.min(page * 20, total)} sur {total} activités
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-3 py-1 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronLeftIcon className="h-5 w-5" />
                </button>
                <span className="px-4 py-1 text-sm text-gray-700">
                  Page {page} / {Math.ceil(total / 20)}
                </span>
                <button
                  onClick={() => setPage(p => p + 1)}
                  disabled={page * 20 >= total}
                  className="px-3 py-1 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronRightIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
