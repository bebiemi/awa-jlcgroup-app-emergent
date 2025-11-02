import Layout from '@/components/Layout'
import Card from '@/components/Card'
import { useGetDashboardKPIsQuery } from '../api/adminApi'
import { useGetValidationsQuery } from '../api/validationApi'
import { Link } from 'react-router-dom'
import {
  UserGroupIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline'

export default function AdminDashboard() {
  const { data: kpis, isLoading: kpisLoading } = useGetDashboardKPIsQuery()
  const { data: pendingValidations } = useGetValidationsQuery({
    status: 'pending',
    page: 1,
    page_size: 5,
  })

  if (kpisLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Tableau de Bord Administrateur
          </h1>
          <p className="mt-2 text-gray-600">
            Vue d'ensemble de la plateforme JLC Group
          </p>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="border-l-4 border-jlc-accent-yellow">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ClockIcon className="h-8 w-8 text-jlc-accent-yellow" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">En attente</p>
                <p className="text-2xl font-bold text-gray-900">
                  {kpis?.validations.pending || 0}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {kpis?.validations.pending_interim || 0} intérimaires,{' '}
                  {kpis?.validations.pending_company || 0} entreprises
                </p>
              </div>
            </div>
          </Card>

          <Card className="border-l-4 border-green-500">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircleIcon className="h-8 w-8 text-green-500" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Comptes actifs</p>
                <p className="text-2xl font-bold text-gray-900">
                  {kpis?.active_users || 0}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Comptes approuvés
                </p>
              </div>
            </div>
          </Card>

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
