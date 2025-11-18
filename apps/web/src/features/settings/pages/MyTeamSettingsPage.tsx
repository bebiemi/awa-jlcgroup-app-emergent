import { useState } from 'react'
import Layout from '@/components/Layout'
import { usePermission } from '@/hooks/usePermission'
import { 
  UserGroupIcon, 
  ShieldCheckIcon,
  ExclamationCircleIcon
} from '@heroicons/react/24/outline'

export default function MyTeamSettingsPage() {
  const { hasPermission: canAssignProfiles } = usePermission('rbac.assign_profiles')
  const { hasPermission: canAssignGroups } = usePermission('rbac.assign_groups')

  if (!canAssignProfiles && !canAssignGroups) {
    return (
      <Layout>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <div className="flex items-start gap-3">
              <ExclamationCircleIcon className="h-6 w-6 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-yellow-900 mb-2">
                  Permissions insuffisantes
                </h3>
                <p className="text-sm text-yellow-800">
                  Vous n'avez pas les permissions nécessaires pour gérer une équipe.
                  Contactez votre administrateur pour obtenir les permissions <code className="px-2 py-1 bg-yellow-100 rounded">rbac.assign_profiles</code> ou <code className="px-2 py-1 bg-yellow-100 rounded">rbac.assign_groups</code>.
                </p>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <UserGroupIcon className="h-8 w-8 text-jlc-purple-600" />
            <h1 className="text-3xl font-bold text-gray-900">Mon Équipe</h1>
          </div>
          <p className="text-gray-600">
            Gérez les profils et groupes de vos collaborateurs
          </p>
        </div>

        {/* Info Banner */}
        <div className="mb-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-start gap-3">
            <ShieldCheckIcon className="h-6 w-6 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-blue-900 mb-2">
                Gestion simplifiée de votre équipe
              </h3>
              <p className="text-sm text-blue-800">
                Vous pouvez attribuer des <strong>profils métier</strong> et des <strong>groupes organisationnels</strong> à vos collaborateurs.
                Les rôles IAM techniques sont réservés aux administrateurs.
              </p>
            </div>
          </div>
        </div>

        {/* Permissions actives */}
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Vos permissions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {canAssignProfiles && (
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center gap-2 mb-1">
                  <div className="h-2 w-2 bg-green-500 rounded-full" />
                  <span className="font-medium text-green-900">Assigner des profils</span>
                </div>
                <p className="text-sm text-green-700">
                  Vous pouvez attribuer des profils métier à vos collaborateurs
                </p>
              </div>
            )}
            
            {canAssignGroups && (
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center gap-2 mb-1">
                  <div className="h-2 w-2 bg-green-500 rounded-full" />
                  <span className="font-medium text-green-900">Assigner des groupes</span>
                </div>
                <p className="text-sm text-green-700">
                  Vous pouvez ajouter vos collaborateurs à des groupes organisationnels
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Main Content */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <div className="text-center py-12">
            <UserGroupIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Interface de gestion d'équipe
            </h3>
            <p className="text-gray-600 max-w-md mx-auto mb-6">
              Cette fonctionnalité sera disponible prochainement. Elle vous permettra de :
            </p>
            
            <ul className="text-left max-w-md mx-auto space-y-2 text-gray-700">
              <li className="flex items-start gap-2">
                <span className="text-jlc-purple-600 mt-1">•</span>
                <span>Inviter de nouveaux collaborateurs</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-jlc-purple-600 mt-1">•</span>
                <span>Attribuer des profils métier à vos collaborateurs</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-jlc-purple-600 mt-1">•</span>
                <span>Organiser votre équipe en groupes</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-jlc-purple-600 mt-1">•</span>
                <span>Suivre les permissions de chaque membre</span>
              </li>
            </ul>
            
            <div className="mt-8">
              <a
                href="/admin/users"
                className="inline-flex items-center px-4 py-2 bg-jlc-purple-600 text-white rounded-md hover:bg-jlc-purple-700 transition-colors"
              >
                Accéder à la gestion des utilisateurs
              </a>
            </div>
          </div>
        </div>

        {/* Help Section */}
        <div className="mt-8 p-4 bg-gray-50 border border-gray-200 rounded-lg">
          <h3 className="font-semibold text-gray-900 mb-2">Besoin d'aide ?</h3>
          <p className="text-sm text-gray-600">
            Pour gérer votre équipe de manière avancée, utilisez la <a href="/admin/users" className="text-jlc-purple-600 hover:underline">page de gestion des utilisateurs</a> où vous pouvez :
          </p>
          <ul className="mt-2 text-sm text-gray-600 space-y-1 ml-4">
            <li>• Voir tous vos collaborateurs</li>
            <li>• Modifier leurs profils et groupes</li>
            <li>• Consulter leurs permissions effectives</li>
          </ul>
        </div>
      </div>
    </Layout>
  )
}
