import { Link, useNavigate } from 'react-router-dom'
import { useAppSelector, useAppDispatch } from '@/store/hooks'
import { logoutAction } from '@/features/auth/slices/authSlice'
import { useLogoutMutation } from '@/features/auth/api/authApi'
import { BellIcon, UserCircleIcon } from '@heroicons/react/24/outline'
import { useGetNotificationsQuery } from '@/features/notifications/api/notificationApi'
import { useState } from 'react'
import NotificationDropdown from '@/features/notifications/components/NotificationDropdown'

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const { user } = useAppSelector((state) => state.auth)
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const [logout] = useLogoutMutation()
  const [showNotifications, setShowNotifications] = useState(false)

  const { data: notificationsData } = useGetNotificationsQuery({
    page: 1,
    page_size: 10,
  })

  const handleLogout = async () => {
    try {
      await logout().unwrap()
      dispatch(logoutAction())
      navigate('/login')
    } catch (error) {
      console.error('Logout failed:', error)
      dispatch(logoutAction())
      navigate('/login')
    }
  }

  const getNavLinks = () => {
    if (!user) return []

    const links: { to: string; label: string }[] = [
      { to: '/profile', label: 'Mon Profil' },
    ]

    if (user.roles.includes('admin')) {
      links.unshift(
        { to: '/admin', label: 'Tableau de Bord' },
        { to: '/admin/validations', label: 'Validations' }
      )
    } else if (user.roles.includes('interim')) {
      links.unshift({ to: '/interimaire', label: 'Tableau de Bord' })
    }

    return links
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-jlc-purple-600 to-jlc-purple-700 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-3">
              <div className="text-white font-bold text-2xl flex items-center">
                <span className="bg-gradient-to-r from-purple-300 to-blue-200 bg-clip-text text-transparent">
                  JLC
                </span>
                <span className="ml-2 text-jlc-accent-light text-lg">GROUP</span>
                <span className="ml-1 text-jlc-accent-yellow text-xl">★</span>
              </div>
            </Link>

            {/* Navigation */}
            <nav className="hidden md:flex space-x-6">
              {getNavLinks().map((link) => (
                <Link
                  key={link.to}
                  to={link.to}
                  className="text-white hover:text-jlc-accent-yellow transition-colors duration-200 font-medium"
                >
                  {link.label}
                </Link>
              ))}
            </nav>

            {/* Right side */}
            <div className="flex items-center space-x-4">
              {/* Notifications */}
              <div className="relative">
                <button
                  onClick={() => setShowNotifications(!showNotifications)}
                  className="relative p-2 text-white hover:text-jlc-accent-yellow transition-colors"
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

              {/* User menu */}
              <div className="flex items-center space-x-3">
                <UserCircleIcon className="h-8 w-8 text-white" />
                <div className="hidden md:block">
                  <p className="text-sm font-medium text-white">
                    {user?.full_name || user?.username}
                  </p>
                  <p className="text-xs text-jlc-accent-light">
                    {user?.roles.join(', ')}
                  </p>
                </div>
                <button
                  onClick={handleLogout}
                  className="ml-4 px-4 py-2 text-sm font-medium text-jlc-purple-700 bg-white rounded-lg hover:bg-jlc-accent-yellow hover:text-jlc-purple-800 transition-all duration-200"
                >
                  Déconnexion
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-500">
            © {new Date().getFullYear()} JLC Group - Plateforme de Gestion d'Intérim
          </p>
        </div>
      </footer>
    </div>
  )
}
