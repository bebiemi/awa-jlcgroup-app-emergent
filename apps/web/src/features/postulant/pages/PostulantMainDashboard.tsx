/**
 * Main Dashboard for Postulants/Candidats
 * Overview with KPIs and metrics
 */
import Layout from '@/components/Layout'
import Card from '@/components/Card'
import { useGetMyProfileQuery } from '@/features/profile/api/profileApi'
import { Link } from 'react-router-dom'
import {
  CheckCircleIcon,
  ClockIcon,
  DocumentTextIcon,
  BriefcaseIcon,
  ChartBarIcon,
  UserCircleIcon,
  ArrowTrendingUpIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline'

export default function PostulantMainDashboard() {
  const { data: profileData, isLoading } = useGetMyProfileQuery()

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
        </div>
      </Layout>
    )
  }

  const profile = profileData?.profile
  const completionPercentage = profile?.profile_completion_percentage || 0
  // Use is_verified from profile (comes from user entity)
  const isEmailVerified = profile?.is_verified || false

  // Calculate KPIs
  const documentsCount = profile?.document_ids?.length || 0
  // TODO: Get required documents count from business rules/configuration
  const requiredDocuments = 5 // cv, id, photo, diploma, work_permit
  const skillsCount = Array.isArray(profile?.skills) 
    ? profile.skills.length 
    : (typeof profile?.skills === 'string' ? profile.skills.split(',').filter(Boolean).length : 0)
  
  // TODO: Replace with real data from missions API
  const applicationsCount = 0
  const interviewsCount = 0
  const offersCount = 0

  // Define KPI cards
  const kpis = [
    {
      title: 'Complétion Profil',
      value: `${completionPercentage}%`,
      icon: UserCircleIcon,
      color: completionPercentage >= 80 ? 'green' : completionPercentage >= 50 ? 'yellow' : 'red',
      trend: completionPercentage >= 80 ? 'up' : 'neutral',
      description: completionPercentage >= 100 ? 'Profil complet' : `${100 - completionPercentage}% restant`,
      link: '/postulant/profile-overview',
    },
    {
      title: 'Documents',
      value: `${documentsCount}/${requiredDocuments}`,
      icon: DocumentTextIcon,
      color: documentsCount >= requiredDocuments ? 'green' : documentsCount > 0 ? 'yellow' : 'red',
      trend: documentsCount >= requiredDocuments ? 'up' : 'neutral',
      description: `${requiredDocuments - documentsCount} document(s) manquant(s)`,
      link: '/profile?tab=documents',
    },
    {
      title: 'Compétences',
      value: skillsCount,
      icon: ChartBarIcon,
      color: skillsCount >= 5 ? 'green' : skillsCount > 0 ? 'yellow' : 'gray',
      trend: skillsCount >= 5 ? 'up' : 'neutral',
      description: skillsCount === 0 ? 'Aucune compétence ajoutée' : `${skillsCount} compétence(s)`,
      link: '/profile?section=experience',
    },
    {
      title: 'Candidatures',
      value: applicationsCount,
      icon: BriefcaseIcon,
      color: applicationsCount > 0 ? 'blue' : 'gray',
      trend: applicationsCount > 0 ? 'up' : 'neutral',
      description: applicationsCount === 0 ? 'Aucune candidature' : 'En cours',
      link: '/mes-candidatures',
    },
  ]

  // Status messages - Only show alerts for incomplete items
  const alerts = []
  
  // Alert 1: Email verification (only if not verified)
  if (!isEmailVerified) {
    alerts.push({
      type: 'warning',
      title: 'Email non vérifié',
      message: 'Vérifiez votre email pour accéder à toutes les fonctionnalités',
      link: '/postulant/profile-overview',
    })
  }
  
  // Alert 2: Profile completion (only if < 100%)
  if (completionPercentage < 100) {
    alerts.push({
      type: 'info',
      title: 'Profil incomplet',
      message: `Complétez votre profil pour maximiser vos chances (${100 - completionPercentage}% restant)`,
      link: '/postulant/profile-overview',
    })
  }
  
  // Alert 3: Documents (only if missing)
  if (documentsCount < requiredDocuments) {
    const missingCount = requiredDocuments - documentsCount
    alerts.push({
      type: 'warning',
      title: 'Documents manquants',
      message: `${missingCount} document(s) requis manquant(s)`,
      link: '/profile?tab=documents',
    })
  }

  const getColorClasses = (color: string) => {
    const colors = {
      green: 'bg-green-100 text-green-800 border-green-200',
      yellow: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      red: 'bg-red-100 text-red-800 border-red-200',
      blue: 'bg-blue-100 text-blue-800 border-blue-200',
      gray: 'bg-gray-100 text-gray-800 border-gray-200',
    }
    return colors[color as keyof typeof colors] || colors.gray
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Tableau de Bord
          </h1>
          <p className="text-gray-600 mt-1">
            Vue d'ensemble de votre parcours candidat
          </p>
        </div>

        {/* Alerts */}
        {alerts.length > 0 && (
          <div className="space-y-3">
            {alerts.map((alert, index) => (
              <Card
                key={index}
                className={`border-l-4 ${
                  alert.type === 'warning'
                    ? 'border-yellow-400 bg-yellow-50'
                    : alert.type === 'info'
                    ? 'border-blue-400 bg-blue-50'
                    : 'border-red-400 bg-red-50'
                }`}
              >
                <div className="flex items-start gap-3">
                  <ExclamationTriangleIcon
                    className={`h-6 w-6 flex-shrink-0 ${
                      alert.type === 'warning'
                        ? 'text-yellow-600'
                        : alert.type === 'info'
                        ? 'text-blue-600'
                        : 'text-red-600'
                    }`}
                  />
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{alert.title}</h3>
                    <p className="text-sm text-gray-700 mt-1">{alert.message}</p>
                    <Link
                      to={alert.link}
                      className="text-sm font-medium text-jlc-purple-600 hover:text-jlc-purple-700 mt-2 inline-block"
                    >
                      Voir →
                    </Link>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* KPI Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {kpis.map((kpi, index) => {
            const Icon = kpi.icon
            return (
              <Link key={index} to={kpi.link}>
                <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm text-gray-600 font-medium">{kpi.title}</p>
                      <p className="text-3xl font-bold text-gray-900 mt-2">{kpi.value}</p>
                      <p className="text-xs text-gray-500 mt-1">{kpi.description}</p>
                    </div>
                    <div className={`p-3 rounded-lg ${getColorClasses(kpi.color)}`}>
                      <Icon className="h-6 w-6" />
                    </div>
                  </div>
                  {kpi.trend === 'up' && (
                    <div className="flex items-center gap-1 mt-3 text-green-600 text-sm">
                      <ArrowTrendingUpIcon className="h-4 w-4" />
                      <span className="font-medium">Objectif atteint</span>
                    </div>
                  )}
                </Card>
              </Link>
            )
          })}
        </div>

        {/* Quick Actions */}
        <Card>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Actions Rapides</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link
              to="/postulant/profile-overview"
              className="flex items-center gap-3 p-4 border-2 border-gray-200 rounded-lg hover:border-jlc-purple-500 hover:bg-purple-50 transition-all group"
            >
              <UserCircleIcon className="h-8 w-8 text-gray-400 group-hover:text-jlc-purple-600" />
              <div>
                <p className="font-semibold text-gray-900">Compléter mon profil</p>
                <p className="text-xs text-gray-600">Étapes détaillées</p>
              </div>
            </Link>

            <Link
              to="/profile?tab=documents"
              className="flex items-center gap-3 p-4 border-2 border-gray-200 rounded-lg hover:border-jlc-purple-500 hover:bg-purple-50 transition-all group"
            >
              <DocumentTextIcon className="h-8 w-8 text-gray-400 group-hover:text-jlc-purple-600" />
              <div>
                <p className="font-semibold text-gray-900">Gérer mes documents</p>
                <p className="text-xs text-gray-600">Upload et validation</p>
              </div>
            </Link>

            <Link
              to="/offres"
              className="flex items-center gap-3 p-4 border-2 border-gray-200 rounded-lg hover:border-jlc-purple-500 hover:bg-purple-50 transition-all group"
            >
              <BriefcaseIcon className="h-8 w-8 text-gray-400 group-hover:text-jlc-purple-600" />
              <div>
                <p className="font-semibold text-gray-900">Voir les offres</p>
                <p className="text-xs text-gray-600">Missions disponibles</p>
              </div>
            </Link>
          </div>
        </Card>

        {/* Recent Activity */}
        <Card>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Activité Récente</h2>
          <div className="space-y-3">
            <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
              <ClockIcon className="h-5 w-5 text-gray-400 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm text-gray-900">Inscription réussie</p>
                <p className="text-xs text-gray-500">
                  {profile?.created_at
                    ? new Date(profile.created_at).toLocaleDateString('fr-FR', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                      })
                    : 'Aujourd\'hui'}
                </p>
              </div>
            </div>

            {isEmailVerified && (
              <div className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
                <CheckCircleIcon className="h-5 w-5 text-green-600 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm text-gray-900">Email vérifié</p>
                  <p className="text-xs text-gray-500">Votre compte est actif</p>
                </div>
              </div>
            )}

            {completionPercentage === 0 && (
              <div className="text-center py-8 text-gray-500">
                <p className="text-sm">Aucune activité récente</p>
                <p className="text-xs mt-1">Commencez par compléter votre profil</p>
              </div>
            )}
          </div>
        </Card>
      </div>
    </Layout>
  )
}
