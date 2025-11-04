import { useAppSelector } from '@/store/hooks'
import Layout from '@/components/Layout'
import Card from '@/components/Card'
import {
  BriefcaseIcon,
  UserGroupIcon,
  ClockIcon,
  CheckCircleIcon,
  ChartBarIcon,
  PlusIcon,
  BuildingOfficeIcon,
  PhoneIcon,
  DocumentTextIcon,
} from '@heroicons/react/24/outline'
import { Link } from 'react-router-dom'

export default function CommercialDashboard() {
  const { user } = useAppSelector((state) => state.auth)

  // Mock data - À remplacer par de vraies données de l'API
  const stats = {
    totalMissions: 15,
    activeMissions: 8,
    totalApplications: 45,
    successfulPlacements: 12,
  }

  const recentActivity = [
    {
      id: '1',
      type: 'mission',
      title: 'Nouvelle mission créée',
      company: 'Société ABC SARL',
      date: '2025-01-20',
    },
    {
      id: '2',
      type: 'application',
      title: 'Nouvelle candidature',
      mission: 'Développeur Full Stack',
      date: '2025-01-20',
    },
    {
      id: '3',
      type: 'placement',
      title: 'Placement finalisé',
      candidate: 'Jean Dupont',
      date: '2025-01-19',
    },
    {
      id: '4',
      type: 'contact',
      title: 'Nouveau contact entreprise',
      company: 'Tech Solutions',
      date: '2025-01-18',
    },
  ]

  const upcomingTasks = [
    {
      id: '1',
      title: 'Entretien candidat - Marie Martin',
      time: 'Aujourd\'hui 14:00',
      priority: 'high',
    },
    {
      id: '2',
      title: 'Suivi mission - Développeur Backend',
      time: 'Demain 10:00',
      priority: 'medium',
    },
    {
      id: '3',
      title: 'Rendez-vous client - Entreprise XYZ',
      time: 'Demain 15:00',
      priority: 'high',
    },
  ]

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Tableau de Bord Commercial
            </h1>
            <p className="mt-2 text-gray-600">
              Bienvenue, {user?.full_name || user?.username} !
            </p>
            <p className="text-sm text-gray-500">
              Gérez vos missions, clients et candidatures
            </p>
          </div>
          <Link
            to="/missions/create"
            className="flex items-center gap-2 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 transition-colors"
          >
            <PlusIcon className="h-5 w-5" />
            Nouvelle Mission
          </Link>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Total Missions */}
          <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-blue-600">Total Missions</p>
                <p className="text-3xl font-bold text-blue-900 mt-2">
                  {stats.totalMissions}
                </p>
                <Link
                  to="/missions"
                  className="text-sm text-blue-600 hover:text-blue-700 mt-2 inline-flex items-center"
                >
                  Gérer →
                </Link>
              </div>
              <div className="p-3 bg-blue-200 rounded-lg">
                <BriefcaseIcon className="h-8 w-8 text-blue-600" />
              </div>
            </div>
          </Card>

          {/* Active Missions */}
          <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-green-600">Missions Actives</p>
                <p className="text-3xl font-bold text-green-900 mt-2">
                  {stats.activeMissions}
                </p>
                <p className="text-sm text-green-600 mt-2">En recrutement</p>
              </div>
              <div className="p-3 bg-green-200 rounded-lg">
                <ClockIcon className="h-8 w-8 text-green-600" />
              </div>
            </div>
          </Card>

          {/* Total Applications */}
          <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-purple-600">Candidatures</p>
                <p className="text-3xl font-bold text-purple-900 mt-2">
                  {stats.totalApplications}
                </p>
                <p className="text-sm text-purple-600 mt-2">À traiter</p>
              </div>
              <div className="p-3 bg-purple-200 rounded-lg">
                <UserGroupIcon className="h-8 w-8 text-purple-600" />
              </div>
            </div>
          </Card>

          {/* Successful Placements */}
          <Card className="bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-orange-600">Placements Réussis</p>
                <p className="text-3xl font-bold text-orange-900 mt-2">
                  {stats.successfulPlacements}
                </p>
                <p className="text-sm text-orange-600 mt-2">Ce mois</p>
              </div>
              <div className="p-3 bg-orange-200 rounded-lg">
                <CheckCircleIcon className="h-8 w-8 text-orange-600" />
              </div>
            </div>
          </Card>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Activity - Takes 2 columns */}
          <div className="lg:col-span-2">
            <Card>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                  <ClockIcon className="h-6 w-6 text-jlc-purple-600" />
                  Activité Récente
                </h2>
              </div>

              <div className="space-y-3">
                {recentActivity.map((activity) => (
                  <div
                    key={activity.id}
                    className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start gap-3">
                      <div
                        className={`p-2 rounded-lg ${
                          activity.type === 'mission'
                            ? 'bg-blue-100'
                            : activity.type === 'application'
                            ? 'bg-purple-100'
                            : activity.type === 'placement'
                            ? 'bg-green-100'
                            : 'bg-orange-100'
                        }`}
                      >
                        {activity.type === 'mission' ? (
                          <BriefcaseIcon className="h-5 w-5 text-blue-600" />
                        ) : activity.type === 'application' ? (
                          <DocumentTextIcon className="h-5 w-5 text-purple-600" />
                        ) : activity.type === 'placement' ? (
                          <CheckCircleIcon className="h-5 w-5 text-green-600" />
                        ) : (
                          <BuildingOfficeIcon className="h-5 w-5 text-orange-600" />
                        )}
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{activity.title}</p>
                        <p className="text-sm text-gray-600 mt-1">
                          {activity.type === 'mission' && activity.company}
                          {activity.type === 'application' && activity.mission}
                          {activity.type === 'placement' && activity.candidate}
                          {activity.type === 'contact' && activity.company}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">{activity.date}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* Upcoming Tasks */}
          <div>
            <Card>
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <CheckCircleIcon className="h-6 w-6 text-jlc-purple-600" />
                Tâches à Venir
              </h2>

              <div className="space-y-3">
                {upcomingTasks.map((task) => (
                  <div
                    key={task.id}
                    className={`p-3 border-l-4 rounded ${
                      task.priority === 'high'
                        ? 'border-red-500 bg-red-50'
                        : 'border-yellow-500 bg-yellow-50'
                    }`}
                  >
                    <p className="font-medium text-gray-900 text-sm">{task.title}</p>
                    <p className="text-xs text-gray-600 mt-1">{task.time}</p>
                  </div>
                ))}
              </div>

              <button className="w-full mt-4 px-4 py-2 text-sm text-jlc-purple-600 hover:bg-jlc-purple-50 rounded-lg transition-colors">
                Voir toutes les tâches →
              </button>
            </Card>
          </div>
        </div>

        {/* Quick Actions */}
        <Card>
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <ChartBarIcon className="h-6 w-6 text-jlc-purple-600" />
            Actions Rapides
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Link
              to="/missions/create"
              className="p-4 border-2 border-dashed border-jlc-purple-300 rounded-lg hover:border-jlc-purple-500 hover:bg-jlc-purple-50 transition-colors text-center group"
            >
              <PlusIcon className="h-8 w-8 mx-auto text-jlc-purple-600 group-hover:scale-110 transition-transform" />
              <p className="mt-2 font-medium text-gray-900">Créer Mission</p>
              <p className="text-xs text-gray-600">Nouveau besoin client</p>
            </Link>

            <Link
              to="/missions"
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-center"
            >
              <BriefcaseIcon className="h-8 w-8 mx-auto text-jlc-purple-600" />
              <p className="mt-2 font-medium text-gray-900">Gérer Missions</p>
              <p className="text-xs text-gray-600">Toutes les missions</p>
            </Link>

            <Link
              to="/admin/users"
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-center"
            >
              <UserGroupIcon className="h-8 w-8 mx-auto text-jlc-purple-600" />
              <p className="mt-2 font-medium text-gray-900">Candidats</p>
              <p className="text-xs text-gray-600">Base de talents</p>
            </Link>

            <Link
              to="/admin/users?role=company"
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-center"
            >
              <BuildingOfficeIcon className="h-8 w-8 mx-auto text-jlc-purple-600" />
              <p className="mt-2 font-medium text-gray-900">Clients</p>
              <p className="text-xs text-gray-600">Entreprises clientes</p>
            </Link>
          </div>
        </Card>

        {/* Commercial Tips */}
        <Card className="bg-gradient-to-r from-jlc-purple-50 to-purple-50 border-jlc-purple-200">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-jlc-purple-100 rounded-lg">
              <PhoneIcon className="h-6 w-6 text-jlc-purple-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900 mb-2">
                Votre Rôle Commercial
              </h3>
              <p className="text-sm text-gray-700 mb-3">
                En tant que commercial, vous êtes l'interface principale entre les clients et l'agence. 
                Votre mission est d'identifier les besoins, proposer des solutions et assurer la satisfaction client.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-gray-700">
                <div className="flex items-start gap-2">
                  <CheckCircleIcon className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                  <span>Prospecter et fidéliser les clients</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircleIcon className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                  <span>Créer et gérer les missions</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircleIcon className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                  <span>Suivre les candidatures</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircleIcon className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                  <span>Coordonner les placements</span>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </Layout>
  )
}
