/**
 * Recent Notifications Widget
 * Shows recent notifications
 */
import React from 'react'
import Card from '@/components/Card'
import { Link } from 'react-router-dom'
import { BellIcon, CheckCircleIcon, ExclamationCircleIcon, InformationCircleIcon } from '@heroicons/react/24/outline'
import { useDashboardWidgets } from '@/features/config/api/appConfigApi'

// Mock notifications for now (will be replaced with real API)
const mockNotifications = [
  {
    id: '1',
    type: 'success',
    title: 'Candidature acceptée',
    message: 'Votre candidature pour la mission "Développeur Web" a été acceptée',
    time: '2h',
    read: false,
  },
  {
    id: '2',
    type: 'warning',
    title: 'Document expirant',
    message: 'Votre certificat médical expire dans 15 jours',
    time: '5h',
    read: false,
  },
  {
    id: '3',
    type: 'info',
    title: 'Nouvelle mission disponible',
    message: 'Une mission correspondant à votre profil est disponible',
    time: '1j',
    read: true,
  },
]

export default function RecentNotificationsWidget() {
  const { data: widgetsConfig } = useDashboardWidgets()
  
  // Get max items from config (default 5)
  const maxItems = widgetsConfig?.recent_notifications?.max_items || 5
  const notifications = mockNotifications.slice(0, maxItems)

  const unreadCount = notifications.filter((n) => !n.read).length

  const getIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />
      case 'warning':
        return <ExclamationCircleIcon className="h-5 w-5 text-orange-500" />
      case 'error':
        return <ExclamationCircleIcon className="h-5 w-5 text-red-500" />
      default:
        return <InformationCircleIcon className="h-5 w-5 text-blue-500" />
    }
  }

  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <BellIcon className="h-6 w-6 text-gray-700" />
          <h3 className="text-lg font-semibold text-gray-900">Notifications</h3>
        </div>
        {unreadCount > 0 && (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
            {unreadCount} non lu{unreadCount > 1 ? 's' : ''}
          </span>
        )}
      </div>

      {notifications.length === 0 ? (
        <div className="text-center py-8">
          <BellIcon className="h-12 w-12 text-gray-300 mx-auto mb-3" />
          <p className="text-sm text-gray-500">Aucune notification</p>
        </div>
      ) : (
        <div className="space-y-3">
          {notifications.map((notif) => (
            <div
              key={notif.id}
              className={`flex items-start gap-3 p-3 rounded-lg transition-colors cursor-pointer ${
                notif.read
                  ? 'bg-gray-50 hover:bg-gray-100'
                  : 'bg-blue-50 hover:bg-blue-100 border border-blue-200'
              }`}
            >
              <div className="flex-shrink-0 mt-0.5">{getIcon(notif.type)}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between">
                  <p className={`text-sm font-medium ${notif.read ? 'text-gray-900' : 'text-gray-900 font-semibold'}`}>
                    {notif.title}
                  </p>
                  <span className="text-xs text-gray-500 ml-2 flex-shrink-0">{notif.time}</span>
                </div>
                <p className="text-xs text-gray-600 mt-1">{notif.message}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="mt-4 pt-4 border-t border-gray-200">
        <Link
          to="/notifications"
          className="block w-full text-center px-4 py-2 text-sm font-medium text-jlc-purple-600 hover:text-jlc-purple-700 hover:bg-jlc-purple-50 rounded-lg transition-colors"
        >
          Voir toutes les notifications
        </Link>
      </div>
    </Card>
  )
}
