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
} from '@heroicons/react/24/outline'
import { Link } from 'react-router-dom'

export default function CompanyDashboard() {
  const { user } = useAppSelector((state) => state.auth)

  // Mock data - À remplacer par de vraies données de l'API
  const stats = {
    totalMissions: 5,
    activeMissions: 2,
    totalApplications: 12,
    selectedCandidates: 3,
  }

  const recentMissions = [
    {
      id: '1',
      title: 'Développeur Full Stack',
      status: 'active',
      applications: 5,
      date: '2025-01-15',
    },
    {
      id: '2',
      title: 'Chef de Projet IT',
      status: 'draft',
      applications: 0,
      date: '2025-01-20',
    },
  ]

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Tableau de Bord Entreprise
            </h1>
            <p className="mt-2 text-gray-600">
              Bienvenue, {user?.full_name || user?.username} !
            </p>
            <p className="text-sm text-gray-500">
              Gérez vos besoins en recrutement d'intérimaires
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
                  Voir tous →
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
                <p className="text-sm text-green-600 mt-2">En cours de recrutement</p>
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
                <p className="text-sm text-purple-600 mt-2">Reçues au total</p>
              </div>
              <div className="p-3 bg-purple-200 rounded-lg">
                <UserGroupIcon className="h-8 w-8 text-purple-600" />
              </div>
            </div>
          </Card>

          {/* Selected Candidates */}
          <Card className="bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-orange-600">Candidats Sélectionnés</p>
                <p className="text-3xl font-bold text-orange-900 mt-2">
                  {stats.selectedCandidates}
                </p>
                <p className="text-sm text-orange-600 mt-2">En processus</p>
              </div>
              <div className="p-3 bg-orange-200 rounded-lg">
                <CheckCircleIcon className="h-8 w-8 text-orange-600" />
              </div>
            </div>
          </Card>
        </div>

        {/* Recent Missions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Missions List */}
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                <BriefcaseIcon className="h-6 w-6 text-jlc-purple-600" />
                Missions Récentes
              </h2>
              <Link
                to="/missions"
                className="text-sm text-jlc-purple-600 hover:text-jlc-purple-700"
              >
                Voir tout
              </Link>
            </div>

            <div className="space-y-3">
              {recentMissions.map((mission) => (
                <div
                  key={mission.id}
                  className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{mission.title}</h3>
                      <div className="flex items-center gap-3 mt-2 text-sm text-gray-600">
                        <span
                          className={`px-2 py-1 rounded text-xs font-medium ${
                            mission.status === 'active'
                              ? 'bg-green-100 text-green-700'
                              : 'bg-gray-100 text-gray-700'
                          }`}
                        >
                          {mission.status === 'active' ? 'Active' : 'Brouillon'}
                        </span>
                        <span>{mission.applications} candidature(s)</span>
                      </div>
                    </div>
                    <Link
                      to={`/missions/${mission.id}`}
                      className="px-3 py-1 text-sm text-jlc-purple-600 hover:text-jlc-purple-700 font-medium"
                    >
                      Voir →
                    </Link>
                  </div>
                </div>
              ))}

              {recentMissions.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <BriefcaseIcon className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                  <p>Aucune mission pour le moment</p>
                  <Link
                    to="/missions/create"
                    className="text-jlc-purple-600 hover:text-jlc-purple-700 mt-2 inline-block"
                  >
                    Créer votre première mission
                  </Link>
                </div>
              )}
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
                <p className="text-sm text-gray-600">Publier une offre d'intérim</p>
              </Link>

              <Link
                to="/missions"
                className="block p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <BriefcaseIcon className="h-6 w-6 text-jlc-purple-600 mb-2" />
                <p className="font-medium text-gray-900">Gérer Mes Missions</p>
                <p className="text-sm text-gray-600">Consulter et modifier vos missions</p>
              </Link>

              <Link
                to="/missions"
                className="block p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <UserGroupIcon className="h-6 w-6 text-jlc-purple-600 mb-2" />
                <p className="font-medium text-gray-900">Voir les Candidatures</p>
                <p className="text-sm text-gray-600">Examiner les profils reçus</p>
              </Link>

              <Link
                to="/profile"
                className="block p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <CheckCircleIcon className="h-6 w-6 text-jlc-purple-600 mb-2" />
                <p className="font-medium text-gray-900">Mon Profil Entreprise</p>
                <p className="text-sm text-gray-600">Mettre à jour mes informations</p>
              </Link>
            </div>
          </Card>
        </div>

        {/* Help Section */}
        <Card className="bg-gradient-to-r from-jlc-purple-50 to-purple-50 border-jlc-purple-200">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-jlc-purple-100 rounded-lg">
              <ChartBarIcon className="h-6 w-6 text-jlc-purple-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900 mb-2">
                Comment fonctionne le processus de recrutement ?
              </h3>
              <ol className="text-sm text-gray-700 space-y-2 list-decimal list-inside">
                <li>Créez une mission en définissant vos besoins</li>
                <li>Publiez l'offre pour la rendre visible aux intérimaires</li>
                <li>Recevez et examinez les candidatures</li>
                <li>Pré-sélectionnez et planifiez des entretiens</li>
                <li>Sélectionnez le candidat idéal</li>
                <li>Finalisez avec les documents requis (visite médicale, contrat)</li>
              </ol>
              <Link
                to="/missions/create"
                className="inline-block mt-4 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 transition-colors text-sm font-medium"
              >
                Commencer maintenant
              </Link>
            </div>
          </div>
        </Card>
      </div>
    </Layout>
  )
}
