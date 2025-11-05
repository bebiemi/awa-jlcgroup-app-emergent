import Layout from '@/components/Layout'
import Card from '@/components/Card'
import Button from '@/components/Button'
import { useGetMyProfileQuery } from '@/features/profile/api/profileApi'
import { useGetMyValidationQuery } from '@/features/admin/api/validationApi'
import { useGetActiveContractQuery } from '@/features/contracts/api/contractApi'
import { useUserStatuses } from '@/hooks/useAppConfig'
import { Link } from 'react-router-dom'
import {
  CheckCircleIcon,
  ClockIcon,
  DocumentTextIcon,
  UserCircleIcon,
  BriefcaseIcon,
  MagnifyingGlassIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline'
import clsx from 'clsx'

export default function InterimDashboard() {
  const { data: profile, isLoading: profileLoading } = useGetMyProfileQuery()
  const { data: validation } = useGetMyValidationQuery()
  const userStatuses = useUserStatuses()

  if (profileLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
        </div>
      </Layout>
    )
  }

  const completeness = profile?.completeness || 0
  const getMissingFields = () => {
    if (!profile) return []
    const missing = []
    if (!profile.first_name) missing.push('Prénom')
    if (!profile.last_name) missing.push('Nom')
    if (!profile.phone) missing.push('Téléphone')
    if (!profile.avatar_url) missing.push('Photo de profil')
    if (!profile.interim_data?.skills?.length) missing.push('Compétences')
    if (!profile.interim_data?.experience_years) missing.push('Années d’expérience')
    if (!profile.interim_data?.resume_url) missing.push('CV')
    if (!profile.interim_data?.availability) missing.push('Disponibilité')
    if (!profile.interim_data?.bio) missing.push('Biographie')
    return missing
  }

  const missingFields = getMissingFields()

  return (
    <Layout>
      <div className="space-y-6">
        {/* Welcome Header */}
        <div className="bg-gradient-to-r from-jlc-purple-600 to-jlc-purple-700 rounded-lg shadow-lg p-8 text-white">
          <h1 className="text-3xl font-bold">
            Bonjour, {profile?.first_name || 'Intérimaire'} 👋
          </h1>
          <p className="mt-2 text-purple-100">
            Bienvenue sur votre tableau de bord JLC Group
          </p>
        </div>

        {/* Validation Status Banner */}
        {validation && (
          <Card
            className={clsx(
              'border-l-4',
              validation.status === userStatuses.pending && 'border-yellow-500 bg-yellow-50',
              validation.status === 'approved' && 'border-green-500 bg-green-50',
              validation.status === 'rejected' && 'border-red-500 bg-red-50'
            )}
          >
            <div className="flex items-center">
              <div className="flex-shrink-0">
                {validation.status === userStatuses.pending && (
                  <ClockIcon className="h-8 w-8 text-yellow-600" />
                )}
                {validation.status === 'approved' && (
                  <CheckCircleIcon className="h-8 w-8 text-green-600" />
                )}
                {validation.status === 'rejected' && (
                  <CheckCircleIcon className="h-8 w-8 text-red-600" />
                )}
              </div>
              <div className="ml-4 flex-1">
                {validation.status === userStatuses.pending && (
                  <>
                    <h3 className="text-lg font-semibold text-yellow-900">
                      Validation en cours
                    </h3>
                    <p className="text-sm text-yellow-700 mt-1">
                      Votre compte est en cours de vérification par notre équipe.
                      Vous recevrez une notification dès validation.
                    </p>
                  </>
                )}
                {validation.status === 'approved' && (
                  <>
                    <h3 className="text-lg font-semibold text-green-900">
                      Compte approuvé ✅
                    </h3>
                    <p className="text-sm text-green-700 mt-1">
                      Félicitations! Votre compte a été validé. Vous pouvez maintenant
                      accéder à toutes les fonctionnalités.
                    </p>
                  </>
                )}
                {validation.status === 'rejected' && (
                  <>
                    <h3 className="text-lg font-semibold text-red-900">
                      Compte refusé
                    </h3>
                    <p className="text-sm text-red-700 mt-1">
                      Motif: {validation.comment}
                    </p>
                  </>
                )}
              </div>
            </div>
          </Card>
        )}

        {/* Profile Completeness */}
        <Card title="Complétude de votre profil" subtitle={`${completeness}% complété`}>
          <div className="space-y-4">
            {/* Progress bar */}
            <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
              <div
                className={clsx(
                  'h-full rounded-full transition-all duration-500',
                  completeness < 50 && 'bg-red-500',
                  completeness >= 50 && completeness < 80 && 'bg-yellow-500',
                  completeness >= 80 && 'bg-green-500'
                )}
                style={{ width: `${completeness}%` }}
              />
            </div>

            {/* Missing fields checklist */}
            {missingFields.length > 0 && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-blue-900 mb-3">
                  📝 Pour compléter votre profil:
                </h4>
                <ul className="space-y-2">
                  {missingFields.map((field, index) => (
                    <li key={index} className="flex items-center text-sm text-blue-800">
                      <span className="inline-block w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                      {field}
                    </li>
                  ))}
                </ul>
                <Link to="/profile">
                  <Button variant="primary" size="sm" className="mt-4">
                    Compléter mon profil
                  </Button>
                </Link>
              </div>
            )}

            {completeness === 100 && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
                <CheckCircleIcon className="h-12 w-12 text-green-600 mx-auto mb-2" />
                <p className="text-sm font-semibold text-green-900">
                  🎉 Votre profil est complet!
                </p>
              </div>
            )}
          </div>
        </Card>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link
            to="/profile"
            className="block p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow border-l-4 border-jlc-purple-500"
          >
            <UserCircleIcon className="h-8 w-8 text-jlc-purple-600 mb-3" />
            <h3 className="text-lg font-semibold text-gray-900">Mon Profil</h3>
            <p className="text-sm text-gray-600 mt-2">
              Mettre à jour mes informations
            </p>
          </Link>

          <div className="block p-6 bg-white rounded-lg shadow-md border-l-4 border-blue-500">
            <DocumentTextIcon className="h-8 w-8 text-blue-600 mb-3" />
            <h3 className="text-lg font-semibold text-gray-900">Missions</h3>
            <p className="text-sm text-gray-600 mt-2">
              Consulter les missions disponibles
            </p>
            <p className="text-xs text-gray-400 mt-2">(Bientôt disponible)</p>
          </div>

          <div className="block p-6 bg-white rounded-lg shadow-md border-l-4 border-green-500">
            <CheckCircleIcon className="h-8 w-8 text-green-600 mb-3" />
            <h3 className="text-lg font-semibold text-gray-900">Mes Candidatures</h3>
            <p className="text-sm text-gray-600 mt-2">
              Suivre l'état de mes candidatures
            </p>
            <p className="text-xs text-gray-400 mt-2">(Bientôt disponible)</p>
          </div>
        </div>

        {/* Profile Summary */}
        {profile && (
          <Card title="Mon Profil en Bref">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-sm font-medium text-gray-500">Informations personnelles</h4>
                <dl className="mt-3 space-y-2">
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">Nom complet:</dt>
                    <dd className="text-sm font-medium text-gray-900">
                      {profile.first_name} {profile.last_name}
                    </dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">Téléphone:</dt>
                    <dd className="text-sm font-medium text-gray-900">
                      {profile.phone || 'Non renseigné'}
                    </dd>
                  </div>
                </dl>
              </div>

              {profile.interim_data && (
                <div>
                  <h4 className="text-sm font-medium text-gray-500">Compétences</h4>
                  <div className="mt-3">
                    {profile.interim_data.skills.length > 0 ? (
                      <div className="flex flex-wrap gap-2">
                        {profile.interim_data.skills.map((skill, index) => (
                          <span
                            key={index}
                            className="px-3 py-1 bg-jlc-purple-100 text-jlc-purple-800 rounded-full text-xs font-medium"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-gray-500">Aucune compétence renseignée</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          </Card>
        )}
      </div>
    </Layout>
  )
}
