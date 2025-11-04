import { useAppSelector } from '@/store/hooks'
import Layout from '@/components/Layout'
import Card from '@/components/Card'
import {
  BuildingOfficeIcon,
  BriefcaseIcon,
  UserGroupIcon,
  ClockIcon,
  CheckCircleIcon,
  ChartBarIcon,
  PlusIcon,
} from '@heroicons/react/24/outline'
import { Link } from 'react-router-dom'

export default function AgencyDashboard() {
  const { user } = useAppSelector((state) => state.auth)

  // Mock data - À remplacer par de vraies données de l'API
  const stats = {
    totalClients: 8,
    activeMissions: 12,
    totalInterims: 45,
    ongoingPlacements: 7,
  }

  const recentActivity = [
    {
      id: '1',
      type: 'mission',
      title: 'Nouvelle mission créée',
      client: 'Entreprise ABC',
      date: '2025-01-20',
    },
    {
      id: '2',
      type: 'placement',
      title: 'Placement confirmé',
      interim: 'Jean Dupont',
      date: '2025-01-19',
    },
    {
      id: '3',
      type: 'candidate',
      title: 'Nouveau candidat inscrit',
      name: 'Marie Martin',
      date: '2025-01-18',
    },
  ]

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Tableau de Bord Agence
            </h1>
            <p className="mt-2 text-gray-600">
              Bienvenue, {user?.full_name || user?.username} !
            </p>
            <p className="text-sm text-gray-500">
              Gérez vos clients, missions et intérimaires
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
          {/* Total Clients */}
          <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-blue-600">Clients Actifs</p>
                <p className="text-3xl font-bold text-blue-900 mt-2">
                  {stats.totalClients}
                </p>
                <p className="text-sm text-blue-600 mt-2">Entreprises partenaires</p>
              </div>
              <div className="p-3 bg-blue-200 rounded-lg">
                <BuildingOfficeIcon className="h-8 w-8 text-blue-600" />
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
                <Link
                  to="/missions"
                  className="text-sm text-green-600 hover:text-green-700 mt-2 inline-flex items-center"
                >
                  Gérer →
                </Link>
              </div>
              <div className="p-3 bg-green-200 rounded-lg">
                <BriefcaseIcon className="h-8 w-8 text-green-600" />
              </div>
            </div>
          </Card>

          {/* Total Interims */}
          <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-purple-600">Intérimaires</p>
                <p className="text-3xl font-bold text-purple-900 mt-2">
                  {stats.totalInterims}
                </p>
                <p className="text-sm text-purple-600 mt-2">Dans notre base</p>
              </div>
              <div className="p-3 bg-purple-200 rounded-lg">
                <UserGroupIcon className="h-8 w-8 text-purple-600" />
              </div>
            </div>
          </Card>

          {/* Ongoing Placements */}
          <Card className="bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-orange-600">Placements en Cours</p>
                <p className="text-3xl font-bold text-orange-900 mt-2">
                  {stats.ongoingPlacements}
                </p>
                <p className="text-sm text-orange-600 mt-2">En finalisation</p>
              </div>
              <div className="p-3 bg-orange-200 rounded-lg">
                <CheckCircleIcon className="h-8 w-8 text-orange-600" />
              </div>
            </div>
          </Card>
        </div>

        {/* Recent Activity & Quick Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Activity */}
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
                          ? 'bg-green-100'
                          : activity.type === 'placement'
                          ? 'bg-blue-100'
                          : 'bg-purple-100'
                      }`}
                    >
                      {activity.type === 'mission' ? (
                        <BriefcaseIcon className="h-5 w-5 text-green-600" />
                      ) : activity.type === 'placement' ? (
                        <CheckCircleIcon className="h-5 w-5 text-blue-600" />
                      ) : (
                        <UserGroupIcon className="h-5 w-5 text-purple-600" />
                      )}
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{activity.title}</p>
                      <p className="text-sm text-gray-600 mt-1">
                        {activity.type === 'mission' && activity.client}
                        {activity.type === 'placement' && activity.interim}
                        {activity.type === 'candidate' && activity.name}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">{activity.date}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* Quick Actions */}
          <Card>
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <ChartBarIcon className="h-6 w-6 text-jlc-purple-600" />
              Actions Rapides
            </h2>

            <div className="space-y-3">
              <Link
                to="/missions/create"
                className="block p-4 border-2 border-dashed border-jlc-purple-300 rounded-lg hover:border-jlc-purple-500 hover:bg-jlc-purple-50 transition-colors text-center group"
              >
                <PlusIcon className="h-8 w-8 mx-auto text-jlc-purple-600 group-hover:scale-110 transition-transform" />
                <p className="mt-2 font-medium text-gray-900">Créer une Nouvelle Mission</p>
                <p className="text-sm text-gray-600">Pour un de vos clients</p>
              </Link>

              <Link
                to="/missions"
                className="block p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <BriefcaseIcon className="h-6 w-6 text-jlc-purple-600 mb-2" />
                <p className="font-medium text-gray-900">Gérer les Missions</p>
                <p className="text-sm text-gray-600">Toutes les missions actives</p>
              </Link>

              <Link
                to="/admin/users"
                className="block p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <UserGroupIcon className="h-6 w-6 text-jlc-purple-600 mb-2" />
                <p className="font-medium text-gray-900">Gérer les Utilisateurs</p>
                <p className="text-sm text-gray-600">Clients et intérimaires</p>
              </Link>

              <Link
                to="/missions"
                className="block p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <CheckCircleIcon className="h-6 w-6 text-jlc-purple-600 mb-2" />
                <p className="font-medium text-gray-900">Suivi des Placements</p>
                <p className="text-sm text-gray-600">Candidatures et contrats</p>
              </Link>
            </div>
          </Card>
        </div>

        {/* Info Section */}
        <Card className="bg-gradient-to-r from-jlc-purple-50 to-purple-50 border-jlc-purple-200">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-jlc-purple-100 rounded-lg">
              <BuildingOfficeIcon className="h-6 w-6 text-jlc-purple-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900 mb-2">
                Votre rôle en tant qu'Agence
              </h3>
              <p className="text-sm text-gray-700 mb-3">
                En tant qu'agence d'intérim, vous êtes l'intermédiaire entre les entreprises clientes 
                et les intérimaires. Vous gérez l'ensemble du processus de recrutement et de placement.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-gray-700">
                <div className="flex items-start gap-2">
                  <CheckCircleIcon className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                  <span>Créer des missions pour vos clients</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircleIcon className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                  <span>Gérer votre base d'intérimaires</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircleIcon className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                  <span>Suivre les candidatures et placements</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircleIcon className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                  <span>Finaliser les contrats</span>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </Layout>
  )
}
