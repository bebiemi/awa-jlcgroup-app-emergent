/**
 * Unified Dashboard
 * Dynamic dashboard with configurable widgets based on user role
 */
import React from 'react'
import Layout from '@/components/Layout'
import { useSelector } from 'react-redux'
import { RootState } from '@/store/store'
import { useDashboardWidgets } from '@/features/config/api/appConfigApi'
import ProfileCompletionWidget from '../components/ProfileCompletionWidget'
import MissingDocumentsWidget from '../components/MissingDocumentsWidget'
import RecentNotificationsWidget from '../components/RecentNotificationsWidget'
import { SparklesIcon } from '@heroicons/react/24/solid'

export default function UnifiedDashboard() {
  const { user } = useAuth()
  const { data: widgetsConfig, isLoading } = useDashboardWidgets()

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
        </div>
      </Layout>
    )
  }

  // Get user's primary role
  const userRole = user?.roles?.[0] || 'interim'
  const userName = user?.full_name || user?.username || 'Utilisateur'

  // Filter widgets based on user role and enabled status
  const getEnabledWidgets = () => {
    if (!widgetsConfig) return []

    const widgets = []

    // Check each widget
    Object.entries(widgetsConfig).forEach(([key, config]: [string, any]) => {
      if (
        config.enabled &&
        (config.roles.includes('all') || config.roles.includes(userRole))
      ) {
        widgets.push({
          key,
          priority: config.priority || 999,
          component: getWidgetComponent(key),
        })
      }
    })

    // Sort by priority (lower number = higher priority)
    return widgets.sort((a, b) => a.priority - b.priority)
  }

  const getWidgetComponent = (key: string) => {
    switch (key) {
      case 'profile_completion':
        return <ProfileCompletionWidget />
      case 'missing_documents':
        return <MissingDocumentsWidget />
      case 'recent_notifications':
        return <RecentNotificationsWidget />
      case 'active_applications':
        // TODO: Create ActiveApplicationsWidget
        return null
      case 'recommended_missions':
        // TODO: Create RecommendedMissionsWidget
        return null
      default:
        return null
    }
  }

  const enabledWidgets = getEnabledWidgets()

  // Get time-based greeting
  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Bonjour'
    if (hour < 18) return 'Bon après-midi'
    return 'Bonsoir'
  }

  // Get role-specific emoji
  const getRoleEmoji = () => {
    switch (userRole) {
      case 'admin':
        return '👨‍💼'
      case 'interim':
        return '💼'
      case 'company':
        return '🏢'
      case 'agency':
        return '🏛️'
      case 'postulant':
        return '🎯'
      default:
        return '👋'
    }
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Welcome Header */}
        <div className="bg-gradient-to-r from-jlc-purple-600 via-jlc-purple-700 to-jlc-neon-pink-600 rounded-xl shadow-xl p-8 text-white overflow-hidden relative">
          {/* Background pattern */}
          <div className="absolute inset-0 opacity-10">
            <div className="absolute inset-0" style={{
              backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
              backgroundSize: '32px 32px'
            }}></div>
          </div>

          <div className="relative z-10">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <SparklesIcon className="h-6 w-6 text-yellow-300" />
                  <span className="text-sm font-medium text-purple-200 uppercase tracking-wide">
                    JLC Group
                  </span>
                </div>
                <h1 className="text-3xl md:text-4xl font-bold">
                  {getGreeting()}, {userName} {getRoleEmoji()}
                </h1>
                <p className="mt-2 text-purple-100 text-lg">
                  Bienvenue sur votre tableau de bord personnalisé
                </p>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="bg-white bg-opacity-20 backdrop-blur-sm rounded-lg p-4 border border-white border-opacity-30">
                <p className="text-sm font-medium text-purple-100">Profil</p>
                <p className="text-2xl font-bold text-white mt-1">
                  {/* Will be populated from profile completion */}
                  En cours
                </p>
              </div>
              <div className="bg-white bg-opacity-20 backdrop-blur-sm rounded-lg p-4 border border-white border-opacity-30">
                <p className="text-sm font-medium text-purple-100">Notifications</p>
                <p className="text-2xl font-bold text-white mt-1">
                  {/* Will be populated from notifications */}
                  0 non lues
                </p>
              </div>
              <div className="bg-white bg-opacity-20 backdrop-blur-sm rounded-lg p-4 border border-white border-opacity-30">
                <p className="text-sm font-medium text-purple-100">Statut</p>
                <p className="text-2xl font-bold text-white mt-1">Actif</p>
              </div>
            </div>
          </div>
        </div>

        {/* Dynamic Widgets Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {enabledWidgets.map((widget, index) => (
            widget.component && (
              <div key={widget.key} className="animate-fade-in" style={{ animationDelay: `${index * 100}ms` }}>
                {widget.component}
              </div>
            )
          ))}
        </div>

        {/* No widgets message */}
        {enabledWidgets.length === 0 && (
          <div className="text-center py-12">
            <SparklesIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Aucun widget disponible
            </h3>
            <p className="text-gray-600">
              Votre tableau de bord est en cours de configuration.
            </p>
          </div>
        )}
      </div>
    </Layout>
  )
}
