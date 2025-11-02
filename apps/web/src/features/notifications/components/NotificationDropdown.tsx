import { useGetNotificationsQuery, useMarkNotificationsReadMutation } from '../api/notificationApi'
import { BellIcon, CheckIcon } from '@heroicons/react/24/outline'
import { formatDistanceToNow } from 'date-fns'
import { fr } from 'date-fns/locale'
import clsx from 'clsx'

interface NotificationDropdownProps {
  onClose: () => void
}

export default function NotificationDropdown({ onClose }: NotificationDropdownProps) {
  const { data, isLoading } = useGetNotificationsQuery({ page: 1, page_size: 10 })
  const [markAsRead] = useMarkNotificationsReadMutation()

  const handleMarkAsRead = async (notificationId: string) => {
    try {
      await markAsRead({ notification_ids: [notificationId] }).unwrap()
    } catch (error) {
      console.error('Failed to mark as read:', error)
    }
  }

  const handleMarkAllAsRead = async () => {
    if (!data?.items) return
    const unreadIds = data.items.filter(n => !n.is_read).map(n => n.id)
    if (unreadIds.length > 0) {
      try {
        await markAsRead({ notification_ids: unreadIds }).unwrap()
      } catch (error) {
        console.error('Failed to mark all as read:', error)
      }
    }
  }

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40"
        onClick={onClose}
      />

      {/* Dropdown */}
      <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-xl z-50 max-h-[600px] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-4 py-3 border-b border-gray-200 flex justify-between items-center bg-gray-50">
          <h3 className="text-lg font-semibold text-gray-900">Notifications</h3>
          {data && data.unread_count > 0 && (
            <button
              onClick={handleMarkAllAsRead}
              className="text-sm text-jlc-purple-600 hover:text-jlc-purple-700 font-medium"
            >
              Tout marquer comme lu
            </button>
          )}
        </div>

        {/* Notifications list */}
        <div className="overflow-y-auto flex-1">
          {isLoading && (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-jlc-purple-600"></div>
            </div>
          )}

          {data && data.items.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 text-gray-500">
              <BellIcon className="h-12 w-12 mb-3" />
              <p>Aucune notification</p>
            </div>
          )}

          {data?.items.map((notification) => (
            <div
              key={notification.id}
              className={clsx(
                'px-4 py-3 border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors',
                !notification.is_read && 'bg-blue-50'
              )}
              onClick={() => !notification.is_read && handleMarkAsRead(notification.id)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">
                    {notification.title}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    {notification.body}
                  </p>
                  <p className="text-xs text-gray-400 mt-2">
                    {formatDistanceToNow(new Date(notification.created_at), {
                      addSuffix: true,
                      locale: fr,
                    })}
                  </p>
                </div>
                {!notification.is_read && (
                  <div className="ml-3 flex-shrink-0">
                    <div className="h-2 w-2 rounded-full bg-jlc-accent-yellow"></div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        {data && data.items.length > 0 && (
          <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
            <p className="text-xs text-center text-gray-500">
              {data.total} notification(s) au total
            </p>
          </div>
        )}
      </div>
    </>
  )
}
