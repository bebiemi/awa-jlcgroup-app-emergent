import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { logoutAction } from '@/features/auth/slices/authSlice'
import { useSidebar } from '@/contexts/SidebarContext'
import { useSidebarTheme } from '@/contexts/SidebarThemeContext'
import { BellIcon, Bars3Icon, XMarkIcon, ArrowRightOnRectangleIcon } from '@heroicons/react/24/outline'
import { useGetNotificationsQuery } from '@/features/notifications/api/notificationApi'
import { useGetMyPresenceQuery } from '@/features/presence/api/presenceApi'
import { useEffect, useState } from 'react'
import NotificationDropdown from '@/features/notifications/components/NotificationDropdown'
import UserStatusIndicator from './UserStatusIndicator'
import Breadcrumb from './Breadcrumb'
import EmailVerificationBanner from './EmailVerificationBanner'
import AnimatedGradientBar from './AnimatedGradientBar'

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const dispatch = useAppDispatch()
  const { user, isAuthenticated } = useAppSelector((state) => state.auth)
  const { isOpen, toggleSidebar } = useSidebar()
  const { themeConfig } = useSidebarTheme()
  const [showNotifications, setShowNotifications] = useState(false)
  
  // Fetch presence status ONLY if authenticated and user exists
  const shouldFetchPresence =
    isAuthenticated && user && localStorage.getItem('access_token')

  const { data: presence } = useGetMyPresenceQuery(undefined, {
    skip: !shouldFetchPresence,
    pollingInterval: 300000,
    refetchOnMountOrArgChange: false,
    refetchOnFocus: false,
    refetchOnReconnect: false,
  })

  const { data: notificationsData } = useGetNotificationsQuery(
    {
      page: 1,
      page_size: 10,
    },
    { skip: !isAuthenticated }
  )

  const handleLogout = () => {
    dispatch(logoutAction())
    window.location.href = '/login'
  }

  return (
    <div className="min-h-screen">
      {/* Contenu principal avec offset lié au sidebar via CSS var */}
      <div
        className="min-h-screen flex flex-col"
        style={{
          paddingLeft: 'var(--sidebar-offset, 0px)',
          ['--text-primary' as any]: themeConfig.textPrimary,
          ['--text-secondary' as any]: themeConfig.textSecondary,
          ['--text-heading' as any]: themeConfig.textHeading,
          ['--text-accent' as any]: themeConfig.textAccent,
          background: themeConfig.pageBg,
          color: themeConfig.textPrimary,
        }}
      >
        {/* Top Header Bar - Only for authenticated users */}
        {isAuthenticated && (
          <header className="sticky top-0 z-20 backdrop-blur-md bg-white/70 border-b border-white/40">
            <div className="px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between items-center h-16">
                {/* Left side - menu toggle + espace futur */}
                <div className="flex items-center space-x-3 flex-1">
                  {/* Bouton toggle sidebar */}
                  <button
                    type="button"
                    onClick={toggleSidebar}
                    className="inline-flex items-center justify-center rounded-lg p-2 text-gray-600 hover:text-jlc-purple-600 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-jlc-purple-500 focus:ring-offset-2 md:mr-2"
                    aria-label="Basculer le menu latéral"
                  >
                    {isOpen ? (
                      <XMarkIcon className="h-5 w-5" />
                    ) : (
                      <Bars3Icon className="h-5 w-5" />
                    )}
                  </button>
                  {/* Réservé pour un éventuel titre de page ou recherche */}
                </div>

                {/* Right side - User Info & Notifications */}
                <div className="flex items-center space-x-4">
                  {/* User Avatar with Status Indicator */}
                  <div className="flex items-center space-x-3">
                    <div className="relative">
                      <div className="h-10 w-10 rounded-full bg-gradient-to-br from-jlc-accent-yellow to-yellow-500 flex items-center justify-center text-jlc-purple-900 font-semibold">
                        {user?.full_name?.charAt(0) ||
                          user?.username?.charAt(0) ||
                          'U'}
                      </div>
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
                      {notificationsData &&
                        notificationsData.unread_count > 0 && (
                          <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-500 rounded-full">
                            {notificationsData.unread_count}
                          </span>
                        )}
                    </button>
                    {showNotifications && (
                      <NotificationDropdown
                        onClose={() => setShowNotifications(false)}
                      />
                    )}
                  </div>

                  {/* Logout */}
                  <button
                    onClick={handleLogout}
                    className="inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-gray-700 hover:text-red-600 hover:bg-red-50 transition-colors min-w-[44px]"
                  >
                    <ArrowRightOnRectangleIcon className="h-5 w-5" />
                    <span className="hidden md:inline">Déconnexion</span>
                    <span className="inline md:hidden">Quitter</span>
                  </button>
                </div>
              </div>
            </div>
          </header>
        )}

        {/* Email Verification Banner */}
        {isAuthenticated && <EmailVerificationBanner />}

        {/* Breadcrumb - Sticky just below header (unique instance) */}
        {isAuthenticated && (
          <div className="sticky top-16 z-10 bg-transparent relative backdrop-blur-md">
            <div className="px-4 sm:px-6 lg:px-8 py-3">
              <Breadcrumb />
            </div>
            <AnimatedGradientBar />
          </div>
        )}

        {/* Main content */}
        <main className="flex-1 px-4 sm:px-6 lg:px-8 py-8 pr-[10px]">
          <div
            className="max-w-7xl mx-auto space-y-6 app-surface rounded-3xl p-6 sm:p-8"
            style={{
              ['--app-surface-bg' as any]: themeConfig.contentBg,
              ['--app-surface-border' as any]: themeConfig.contentBorder,
              ['--app-surface-glow' as any]: themeConfig.glow,
            }}
          >
            {children}
          </div>
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
              </a>{' '}
              - Plateforme de Gestion d&apos;Intérim
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
