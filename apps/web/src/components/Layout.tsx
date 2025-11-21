import { useAppSelector } from '@/store/hooks'
import { useSidebar } from '@/contexts/SidebarContext'
import { BellIcon } from '@heroicons/react/24/outline'
import { useGetNotificationsQuery } from '@/features/notifications/api/notificationApi'
import { useGetMyPresenceQuery } from '@/features/presence/api/presenceApi'
import { useState } from 'react'
import NotificationDropdown from '@/features/notifications/components/NotificationDropdown'
import UserStatusIndicator from './UserStatusIndicator'
import SidebarNew from './SidebarNew'
import Breadcrumb from './Breadcrumb'
import EmailVerificationBanner from './EmailVerificationBanner'
import AnimatedGradientBar from './AnimatedGradientBar'

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const { user, isAuthenticated } = useAppSelector((state) => state.auth)
  const { isCollapsed } = useSidebar()
  const [showNotifications, setShowNotifications] = useState(false)
  
  // Fetch presence status ONLY if authenticated and user exists
  const shouldFetchPresence = isAuthenticated && user && localStorage.getItem('access_token')
  
  const { data: presence } = useGetMyPresenceQuery(undefined, { 
    skip: !shouldFetchPresence, // CRITICAL: Skip if not authenticated or no token
    pollingInterval: 300000, // Poll every 5 minutes only
    refetchOnMountOrArgChange: false, // Don't refetch on mount/arg change
    refetchOnFocus: false, // Don't refetch on window focus
    refetchOnReconnect: false, // Don't refetch on reconnect
  })

  const { data: notificationsData } = useGetNotificationsQuery(
    {
      page: 1,
      page_size: 10,
    },
    { skip: !isAuthenticated }
  )

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar - Only shown for authenticated users */}
      {isAuthenticated && <SidebarNew isOpen={!isCollapsed} onClose={() => {}} />}

      {/* Main content with proper spacing for sidebar */}
      <div 
        className={`min-h-screen flex flex-col transition-all duration-300 ${
          isAuthenticated ? (isCollapsed ? 'lg:pl-20' : 'lg:pl-64') : ''
        }`}
      >
        {/* Top Header Bar - Only for authenticated users */}
        {isAuthenticated && (
          <header className="bg-white sticky top-0 z-20 shadow-sm">
            <div className="px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between items-center h-16">
                {/* Left side - could add page title or search */}
                <div className="flex-1">
                  {/* Space for future enhancements */}
                </div>

                {/* Right side - User Info & Notifications */}
                <div className="flex items-center space-x-4">
                  {/* User Avatar with Status Indicator */}
                  <div className="flex items-center space-x-3">
                    <div className="relative">
                      <div className="h-10 w-10 rounded-full bg-gradient-to-br from-jlc-accent-yellow to-yellow-500 flex items-center justify-center text-jlc-purple-900 font-semibold">
                        {user?.full_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
                      </div>
                      {/* Status indicator badge - Only show circle */}
                      {presence && (
                        <div className="absolute -bottom-0.5 -right-0.5">
                          <UserStatusIndicator 
                            status={presence.presence_status} 
                            size="md"
                            showTooltip={true}
                          />
                        </div>
                      )}
                    </div>
                    <div className="hidden md:block">
                      <p className="text-sm font-medium text-gray-900">
                        {user?.full_name || user?.username}
                      </p>
                    </div>
                  </div>

                  {/* Notifications */}
                  <div className="relative">
                    <button
                      onClick={() => setShowNotifications(!showNotifications)}
                      className="relative p-2 text-gray-600 hover:text-jlc-purple-600 transition-colors rounded-lg hover:bg-gray-100"
                    >
                      <BellIcon className="h-6 w-6" />
                      {notificationsData && notificationsData.unread_count > 0 && (
                        <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-500 rounded-full">
                          {notificationsData.unread_count}
                        </span>
                      )}
                    </button>
                    {showNotifications && (
                      <NotificationDropdown onClose={() => setShowNotifications(false)} />
                    )}
                  </div>
                </div>
              </div>
            </div>
          </header>
        )}

        {/* Email Verification Banner */}
        {isAuthenticated && <EmailVerificationBanner />}

        {/* Breadcrumb - Sticky just below header */}
        {isAuthenticated && (
          <div className="sticky top-16 z-10 bg-white relative">
            <div className="px-4 sm:px-6 lg:px-8 py-3">
              <Breadcrumb />
            </div>
            {/* Barre de chargement animée synchronisée au scroll */}
            <AnimatedGradientBar />
          </div>
        )}

        {/* Main content */}
        <main className="flex-1 px-4 sm:px-6 lg:px-8 py-8">
          {/* Page content */}
          {children}
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 mt-auto">
          <div className="px-4 sm:px-6 lg:px-8 py-6">
            <p className="text-center text-sm text-gray-500">
              © {new Date().getFullYear()}{' '}
              <a 
                href="https://jlcgroup.org" 
                target="_blank" 
                rel="noopener noreferrer"
                className="hover:text-jlc-purple-600 transition-colors font-medium"
              >
                JLC Group
              </a>
              {' '}- Plateforme de Gestion d'Intérim
            </p>
            <div className="mt-2 flex items-center justify-center space-x-2 text-xs text-gray-500">
              <span>Designé et conçu par</span>
              <a 
                href="https://awana-group.com" 
                target="_blank" 
                rel="noopener noreferrer"
                className="inline-flex items-center hover:opacity-80 transition-opacity"
              >
                <img 
                  src="/logo-awana.png" 
                  alt="Awana Group" 
                  className="h-6 w-auto object-contain ml-1"
                />
              </a>
            </div>
          </div>
        </footer>
      </div>
    </div>
  )
}
