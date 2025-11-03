import Layout from '@/components/Layout'
import Card from '@/components/Card'
import { useGetAdminStatsQuery } from '../api/adminApi'
import { Link } from 'react-router-dom'
import {
  UserGroupIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ChartBarIcon,
  ShieldCheckIcon,
  UserPlusIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline'

export default function AdminDashboard() {
  const { data: stats, isLoading, refetch } = useGetAdminStatsQuery(undefined, {
    pollingInterval: 30000, // Auto-refresh every 30 seconds
  })

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
        </div>
      </Layout>
    )
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Tableau de Bord Administrateur</h1>
            <p className="mt-2 text-gray-600">Vue d'ensemble de la plateforme JLC Group</p>
          </div>
          <div className="flex items-center space-x-3">
            <span className="text-sm text-gray-500">
              Dernière mise à jour: {stats?.last_updated ? formatDate(stats.last_updated) : '-'}
            </span>
            <button
              onClick={() => refetch()}
              className="p-2 text-gray-600 hover:text-jlc-purple-600 hover:bg-gray-100 rounded-lg transition"
              title="Actualiser"
            >
              <ArrowPathIcon className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* KPI Cards - Users */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Utilisateurs</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="border-l-4 border-jlc-purple-600">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <UserGroupIcon className="h-8 w-8 text-jlc-purple-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Total Utilisateurs</p>
                  <p className="text-2xl font-bold text-gray-900">{stats?.total_users || 0}</p>
                  <Link to="/admin/users" className="text-xs text-jlc-purple-600 hover:underline mt-1">
                    Voir tous →
                  </Link>
                </div>
              </div>
            </Card>

            <Card className="border-l-4 border-green-500">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <CheckCircleIcon className="h-8 w-8 text-green-500" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Comptes Actifs</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {stats?.users_by_status.active || 0}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">Comptes approuvés</p>
                </div>
              </div>
            </Card>

            <Card className="border-l-4 border-yellow-500">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ClockIcon className="h-8 w-8 text-yellow-500" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">En Attente</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {stats?.users_by_status.pending || 0}
                  </p>
                  <Link to="/admin/validations" className="text-xs text-yellow-600 hover:underline mt-1">
                    Valider →
                  </Link>
                </div>
              </div>
            </Card>

            <Card className="border-l-4 border-red-500">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <XCircleIcon className="h-8 w-8 text-red-500" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Suspendus</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {stats?.users_by_status.suspended || 0}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">Comptes bloqués</p>
                </div>
              </div>
            </Card>
          </div>
        </div>

        {/* Activity Stats */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Activité</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card>
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <UserPlusIcon className="h-8 w-8 text-blue-500" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Nouveaux (7 jours)</p>
                  <p className="text-2xl font-bold text-gray-900">{stats?.recent_users_7d || 0}</p>
                  <p className="text-xs text-gray-500 mt-1">Inscriptions récentes</p>
                </div>
              </div>
            </Card>

            <Card>
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ChartBarIcon className="h-8 w-8 text-indigo-500" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Connexions (24h)</p>
                  <p className="text-2xl font-bold text-gray-900">{stats?.recent_logins_24h || 0}</p>
                  <p className="text-xs text-gray-500 mt-1">Activité récente</p>
                </div>
              </div>
            </Card>

            <Card>
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ShieldCheckIcon className="h-8 w-8 text-purple-500" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">MFA Activé</p>
                  <p className="text-2xl font-bold text-gray-900">{stats?.mfa_enabled || 0}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {stats?.total_users
                      ? Math.round((stats.mfa_enabled / stats.total_users) * 100)
                      : 0}
                    % des utilisateurs
                  </p>
                </div>
              </div>
            </Card>
          </div>
        </div>

        {/* Users by Role */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Répartition par Rôle</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <Card className="bg-gradient-to-br from-red-50 to-red-100">
              <div className="text-center">
                <p className="text-sm font-medium text-gray-600">Super Admins</p>
                <p className="text-3xl font-bold text-red-600">{stats?.users_by_role.super_admin || 0}</p>
              </div>
            </Card>
            <Card className="bg-gradient-to-br from-orange-50 to-orange-100">
              <div className="text-center">
                <p className="text-sm font-medium text-gray-600">Admins</p>
                <p className="text-3xl font-bold text-orange-600">{stats?.users_by_role.admin || 0}</p>
              </div>
            </Card>
            <Card className="bg-gradient-to-br from-blue-50 to-blue-100">
              <div className="text-center">
                <p className="text-sm font-medium text-gray-600">Intérimaires</p>
                <p className="text-3xl font-bold text-blue-600">{stats?.users_by_role.interim || 0}</p>
              </div>
            </Card>
            <Card className="bg-gradient-to-br from-green-50 to-green-100">
              <div className="text-center">
                <p className="text-sm font-medium text-gray-600">Entreprises</p>
                <p className="text-3xl font-bold text-green-600">{stats?.users_by_role.company || 0}</p>
              </div>
            </Card>
            <Card className="bg-gradient-to-br from-purple-50 to-purple-100">
              <div className="text-center">
                <p className="text-sm font-medium text-gray-600">Agences</p>
                <p className="text-3xl font-bold text-purple-600">{stats?.users_by_role.agency || 0}</p>
              </div>
            </Card>
          </div>
        </div>

        {/* Users by Provider & System Stats */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Méthode d'Authentification</h2>
            <Card>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Local (Email/Password)</span>
                  <span className="text-2xl font-bold text-gray-900">{stats?.users_by_provider.local || 0}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Google OAuth</span>
                  <span className="text-2xl font-bold text-gray-900">{stats?.users_by_provider.google || 0}</span>
                </div>
              </div>
            </Card>
          </div>

          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Configuration Système</h2>
            <Card>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Groupes</span>
                  <Link
                    to="/admin/groups"
                    className="text-2xl font-bold text-jlc-purple-600 hover:underline"
                  >
                    {stats?.groups_count || 0}
                  </Link>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Profils de Permissions</span>
                  <Link
                    to="/admin/profiles"
                    className="text-2xl font-bold text-jlc-purple-600 hover:underline"
                  >
                    {stats?.profiles_count || 0}
                  </Link>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </Layout>
  )
}

          <Card className="border-l-4 border-red-500">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <XCircleIcon className="h-8 w-8 text-red-500" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Rejets (7j)</p>
                <p className="text-2xl font-bold text-gray-900">
                  {kpis?.validations.recent_rejections_7d || 0}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Dernière semaine
                </p>
              </div>
            </div>
          </Card>

          <Card className="border-l-4 border-jlc-purple-500">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <UserGroupIcon className="h-8 w-8 text-jlc-purple-500" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total profils</p>
                <p className="text-2xl font-bold text-gray-900">
                  {kpis?.profiles.total || 0}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {kpis?.profiles.interim || 0} intérimaires
                </p>
              </div>
            </div>
          </Card>
        </div>

        {/* Pending Validations */}
        <Card
          title="Demandes de validation en attente"
          subtitle={`${pendingValidations?.total || 0} demande(s) à traiter`}
          actions={
            <Link
              to="/admin/validations"
              className="text-sm font-medium text-jlc-purple-600 hover:text-jlc-purple-700"
            >
              Voir tout →
            </Link>
          }
        >
          {pendingValidations && pendingValidations.items.length > 0 ? (
            <div className="divide-y divide-gray-200">
              {pendingValidations.items.map((validation) => (
                <div key={validation.id} className="py-3 flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {validation.user_name || validation.user_email}
                    </p>
                    <p className="text-xs text-gray-500">
                      Type: {validation.validation_type} - Soumis le{' '}
                      {new Date(validation.created_at).toLocaleDateString('fr-FR')}
                    </p>
                  </div>
                  <Link
                    to="/admin/validations"
                    className="text-sm text-jlc-purple-600 hover:text-jlc-purple-700 font-medium"
                  >
                    Traiter
                  </Link>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center text-gray-500 py-8">
              ✅ Aucune demande en attente
            </p>
          )}
        </Card>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link
            to="/admin/validations"
            className="block p-6 bg-gradient-to-r from-jlc-purple-500 to-jlc-purple-600 rounded-lg shadow-md hover:shadow-lg transition-shadow text-white"
          >
            <ChartBarIcon className="h-8 w-8 mb-3" />
            <h3 className="text-lg font-semibold">Validations</h3>
            <p className="text-sm mt-2 text-purple-100">
              Gérer les demandes de validation
            </p>
          </Link>

          <Link
            to="/admin/users"
            className="block p-6 bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg shadow-md hover:shadow-lg transition-shadow text-white"
          >
            <UserGroupIcon className="h-8 w-8 mb-3" />
            <h3 className="text-lg font-semibold">Utilisateurs</h3>
            <p className="text-sm mt-2 text-blue-100">
              Gérer les profils utilisateurs
            </p>
          </Link>

          <div className="block p-6 bg-gradient-to-r from-gray-400 to-gray-500 rounded-lg shadow-md text-white opacity-60">
            <ChartBarIcon className="h-8 w-8 mb-3" />
            <h3 className="text-lg font-semibold">Rapports</h3>
            <p className="text-sm mt-2 text-gray-100">
              Statistiques et analyses (bientôt)
            </p>
          </div>
        </div>
      </div>
    </Layout>
  )
}
