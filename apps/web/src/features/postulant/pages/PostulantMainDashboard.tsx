/**
 * Main Dashboard for Postulants/Candidats
 * Overview with KPIs and metrics
 */
import { useState } from 'react'
import Layout from '@/components/Layout'
import Card from '@/components/Card'
import { useGetMyProfileQuery } from '@/features/profile/api/profileApi'
import { useGetDocumentTypesQuery } from '@/features/profile/api/referencesApi'
import { useGetMissionsQuery } from '@/features/missions/api/missionsApi'
import { useGetMyApplicationsQuery } from '@/features/missions/api/missionApi'
import MissionDetailModal from '@/features/missions/components/MissionDetailModal'
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
import type { Mission } from '@/features/missions/api/missionApi'

export default function PostulantMainDashboard() {
  const { data: profileData, isLoading, error } = useGetMyProfileQuery()
  const { data: documentTypesData, isLoading: isLoadingDocTypes } = useGetDocumentTypesQuery({ requiredOnly: false })
  const { data: missionsData, isLoading: isLoadingMissions } = useGetMissionsQuery({ published_only: true, limit: 5 })
  const { data: myApplications = [] } = useGetMyApplicationsQuery()
  
  // État pour la modale de détail de mission
  const [selectedMission, setSelectedMission] = useState<Mission | null>(null)
  const [isMissionModalOpen, setIsMissionModalOpen] = useState(false)
  
  // Fonction pour ouvrir la modale
  const handleMissionClick = (mission: Mission) => {
    setSelectedMission(mission)
    setIsMissionModalOpen(true)
  }
  
  // Fonction pour fermer la modale
  const handleCloseMissionModal = () => {
    setIsMissionModalOpen(false)
    setTimeout(() => setSelectedMission(null), 300)
  }
  
  // Vérifier si l'utilisateur a déjà postulé à une mission
  const hasAppliedToMission = (missionId: string) => {
    return myApplications.some((app: any) => app.mission_id === missionId)
  }

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
        </div>
      </Layout>
    )
  }

  if (error || !profileData) {
    return (
      <Layout>
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <p className="text-gray-700 font-medium">Erreur lors du chargement de votre profil</p>
            <p className="text-sm text-gray-500 mt-2">Veuillez réessayer dans quelques instants</p>
          </div>
        </div>
      </Layout>
    )
  }

  const profile = profileData?.profile
  const completionPercentage = profile?.profile_completion_percentage || 0
  // Use is_verified from profile (comes from user entity)
  const isEmailVerified = profile?.is_verified || false

  // Get all document types from references
  const allDocumentTypes = documentTypesData?.data || []
  const requiredDocTypes = allDocumentTypes.filter(dt => 
    dt.is_system || dt.metadata?.required_for?.includes('onboarding')
  )
  
  // Get user's uploaded documents
  const userDocuments = profile?.documents || []
  const userDocumentCodes = userDocuments.map((doc: any) => doc.type || doc.document_type)
  
  // Calculate missing documents
  const missingDocuments = requiredDocTypes.filter(
    reqDoc => !userDocumentCodes.includes(reqDoc.code)
  )
  
  // Calculate KPIs
  const documentsCount = userDocuments.length
  const requiredDocuments = requiredDocTypes.length
  const skillsCount = Array.isArray(profile?.skills) 
    ? profile.skills.length 
    : (typeof profile?.skills === 'string' ? profile.skills.split(',').filter(Boolean).length : 0)
  
  // Real missions data
  const availableMissions = missionsData || []
  const applicationsCount = 0 // TODO: Get from applications API
  
  // Determine user status based on profile data
  const getUserStatus = () => {
    // Check if user has active contracts
    if (profile?.contracts && profile.contracts.length > 0) {
      const hasActiveContract = profile.contracts.some((c: any) => c.status === 'active')
      if (hasActiveContract) return 'Intérimaire'
    }
    
    // Check if user has been shortlisted/selected for any mission
    if (profile?.applications && profile.applications.length > 0) {
      const hasShortlistedApp = profile.applications.some((a: any) => 
        ['shortlisted', 'selected', 'hired'].includes(a.status)
      )
      if (hasShortlistedApp) return 'Candidat'
    }
    
    // Check completion percentage
    if (completionPercentage >= 80) {
      return 'Candidat'
    }
    
    return 'Postulant'
  }
  
  const userStatus = getUserStatus()

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

        {/* User Status Badge */}
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Votre Statut</h2>
              <p className="text-sm text-gray-600 mt-1">Niveau actuel dans le processus de recrutement</p>
            </div>
            <div className={`px-6 py-3 rounded-full font-bold text-lg ${
              userStatus === 'Intérimaire' 
                ? 'bg-green-100 text-green-800' 
                : userStatus === 'Candidat' 
                ? 'bg-blue-100 text-blue-800' 
                : 'bg-gray-100 text-gray-800'
            }`}>
              {userStatus}
            </div>
          </div>
        </Card>

        {/* Missing Documents */}
        {missingDocuments.length > 0 && (
          <Card className="border-l-4 border-orange-400">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Documents Manquants ({missingDocuments.length})
            </h2>
            <p className="text-sm text-gray-600 mb-4">
              Pour compléter votre dossier, veuillez fournir les documents suivants :
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {missingDocuments.map((doc) => (
                <div 
                  key={doc.id} 
                  className="flex items-center gap-3 p-3 bg-orange-50 rounded-lg border border-orange-200"
                >
                  <DocumentTextIcon className="h-5 w-5 text-orange-600 flex-shrink-0" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{doc.label_fr}</p>
                    {doc.description && (
                      <p className="text-xs text-gray-600">{doc.description}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
            <Link
              to="/profile?tab=documents"
              className="inline-block mt-4 text-sm font-medium text-jlc-purple-600 hover:text-jlc-purple-700"
            >
              Uploader mes documents →
            </Link>
          </Card>
        )}

        {/* Available Missions */}
        {!isLoadingMissions && availableMissions.length > 0 && (
          <Card>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Missions Disponibles</h2>
                <p className="text-sm text-gray-600 mt-1">
                  {availableMissions.length} mission(s) correspondent à votre profil
                </p>
              </div>
              <Link
                to="/offres"
                className="text-sm font-medium text-jlc-purple-600 hover:text-jlc-purple-700"
              >
                Voir toutes →
              </Link>
            </div>
            <div className="space-y-3">
              {availableMissions.slice(0, 3).map((mission) => {
                const hasApplied = hasAppliedToMission(mission.id)
                
                return (
                  <button
                    key={mission.id}
                    onClick={() => handleMissionClick(mission)}
                    className="w-full text-left p-4 bg-gray-50 hover:bg-purple-50 rounded-lg border border-gray-200 hover:border-jlc-purple-300 transition-all"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h3 className="font-semibold text-gray-900">{mission.title}</h3>
                          {hasApplied && (
                            <span className="px-2 py-0.5 text-xs bg-blue-100 text-blue-700 rounded-full">
                              Candidature envoyée
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-600 mt-1 line-clamp-2">{mission.description}</p>
                        <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                          <span>📍 {mission.location}</span>
                          <span>💰 {mission.salary_range}</span>
                          <span>⏱️ {mission.duration}</span>
                        </div>
                      </div>
                      <BriefcaseIcon className="h-6 w-6 text-gray-400 flex-shrink-0 ml-3" />
                    </div>
                  </button>
                )
              })}
            </div>
          </Card>
        )}

        {/* Recent Activity */}
        <Card>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Activité Récente</h2>
          <div className="space-y-3">
            {/* Profile creation */}
            {profile?.created_at && (
              <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                <ClockIcon className="h-5 w-5 text-gray-400 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm text-gray-900">Inscription réussie</p>
                  <p className="text-xs text-gray-500">
                    {new Date(profile.created_at).toLocaleDateString('fr-FR', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}
                  </p>
                </div>
              </div>
            )}

            {/* Email verification */}
            {isEmailVerified && (
              <div className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
                <CheckCircleIcon className="h-5 w-5 text-green-600 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm text-gray-900">Email vérifié ✓</p>
                  <p className="text-xs text-gray-500">Votre compte est actif</p>
                </div>
              </div>
            )}

            {/* Profile completion milestone */}
            {completionPercentage >= 50 && completionPercentage < 100 && (
              <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                <CheckCircleIcon className="h-5 w-5 text-blue-600 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm text-gray-900">Profil à {completionPercentage}% !</p>
                  <p className="text-xs text-gray-500">Continue comme ça, plus que {100 - completionPercentage}%</p>
                </div>
              </div>
            )}

            {/* Profile completed */}
            {completionPercentage === 100 && (
              <div className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
                <CheckCircleIcon className="h-5 w-5 text-green-600 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm text-gray-900">Profil 100% complet ! 🎉</p>
                  <p className="text-xs text-gray-500">Tu es prêt(e) pour postuler aux missions</p>
                </div>
              </div>
            )}

            {/* Last profile update */}
            {profile?.updated_at && profile.updated_at !== profile.created_at && (
              <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                <ClockIcon className="h-5 w-5 text-gray-400 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm text-gray-900">Profil mis à jour</p>
                  <p className="text-xs text-gray-500">
                    {new Date(profile.updated_at).toLocaleDateString('fr-FR', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}
                  </p>
                </div>
              </div>
            )}

            {/* Empty state */}
            {!profile?.created_at && !isEmailVerified && completionPercentage === 0 && (
              <div className="text-center py-8 text-gray-500">
                <p className="text-sm">Aucune activité récente</p>
                <p className="text-xs mt-1">Commencez par compléter votre profil</p>
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Modale de détail de mission */}
      <MissionDetailModal
        mission={selectedMission}
        isOpen={isMissionModalOpen}
        onClose={handleCloseMissionModal}
        hasAlreadyApplied={selectedMission ? hasAppliedToMission(selectedMission.id) : false}
      />
    </Layout>
  )
}
