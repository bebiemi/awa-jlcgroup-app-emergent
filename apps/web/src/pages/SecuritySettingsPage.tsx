import Layout from '@/components/Layout'
import MfaSettings from '@/features/auth/components/MfaSettings'
import { ShieldCheckIcon } from '@heroicons/react/24/outline'

export default function SecuritySettingsPage() {
  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        {/* Page Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-2">
            <ShieldCheckIcon className="h-8 w-8 text-jlc-purple-600" />
            <h1 className="text-3xl font-bold text-gray-900">Paramètres de Sécurité</h1>
          </div>
          <p className="text-gray-600">
            Gérez vos options de sécurité et d'authentification
          </p>
        </div>

        {/* MFA Settings Section */}
        <MfaSettings />

        {/* Additional Security Info */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">
            Pourquoi activer l'authentification à deux facteurs ?
          </h3>
          <ul className="space-y-2 text-sm text-blue-800">
            <li className="flex items-start">
              <span className="mr-2">•</span>
              <span>Protège votre compte même si votre mot de passe est compromis</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2">•</span>
              <span>Empêche les accès non autorisés à vos données sensibles</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2">•</span>
              <span>Conformité avec les standards de sécurité professionnels</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2">•</span>
              <span>Recommandé pour tous les comptes administrateurs</span>
            </li>
          </ul>
        </div>
      </div>
    </Layout>
  )
}
