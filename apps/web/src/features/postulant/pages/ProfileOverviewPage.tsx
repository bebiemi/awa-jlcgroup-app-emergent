/**
 * Postulant Dashboard
 * Dashboard for users in application/candidature phase
 * Shows profile completion steps, required documents, and next actions
 */
import React, { useState } from 'react'
import Layout from '@/components/Layout'
import Card from '@/components/Card'
import { useGetMyProfileQuery } from '@/features/profile/api/profileApi'
import { Link } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import {
  CheckCircleIcon,
  ClockIcon,
  DocumentTextIcon,
  UserCircleIcon,
  ExclamationTriangleIcon,
  ArrowRightIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline'

export default function ProfileOverviewPage() {
  const { data: profileData, isLoading } = useGetMyProfileQuery()
  const [isSendingEmail, setIsSendingEmail] = useState(false)

  const handleSendVerificationEmail = async () => {
    setIsSendingEmail(true)
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/email-verification/send', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      const data = await response.json()

      if (response.ok) {
        toast.success('Email de vérification envoyé ! Vérifiez votre boîte de réception.')
      } else {
        toast.error(data.detail || 'Erreur lors de l\'envoi')
      }
    } catch (error) {
      toast.error('Erreur de connexion')
    } finally {
      setIsSendingEmail(false)
    }
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

  const profile = profileData?.profile
  const completionPercentage = profile?.profile_completion_percentage || 0
  const isEmailVerified = profileData?.is_verified || false

  // Define required steps for postulant
  const requiredSteps = [
    {
      id: 'email',
      title: 'Vérifier mon email',
      description: 'Confirmez votre adresse email pour activer votre compte',
      completed: isEmailVerified,
      action: isEmailVerified ? null : { label: 'Envoyer email', link: null, handler: 'sendVerificationEmail' },
      priority: 1,
    },
    {
      id: 'profile_basic',
      title: 'Compléter les informations de base',
      description: 'Nom, prénom, téléphone, date de naissance',
      completed: profile?.first_name && profile?.last_name && profile?.phone && profile?.date_of_birth,
      action: { label: 'Compléter', link: '/profile?section=basic' },
      priority: 2,
    },
    {
      id: 'profile_address',
      title: 'Renseigner mon adresse',
      description: 'Adresse complète et lieu de résidence',
      completed: profile?.address && profile?.city,
      action: { label: 'Ajouter', link: '/profile?section=address' },
      priority: 3,
    },
    {
      id: 'profile_photo',
      title: 'Ajouter une photo de profil',
      description: 'Une photo professionnelle pour votre profil',
      completed: !!profile?.photo_url,
      action: { label: 'Télécharger', link: '/profile?section=photo' },
      priority: 4,
    },
    {
      id: 'documents',
      title: 'Télécharger mes documents',
      description: 'CV, pièce d\'identité et autres documents requis',
      completed: profile?.cv_document_id && profile?.document_ids && profile.document_ids.length >= 2,
      action: { label: 'Gérer documents', link: '/profile?tab=documents' },
      priority: 5,
    },
    {
      id: 'profile_experience',
      title: 'Ajouter mon expérience',
      description: 'Compétences, années d\'expérience, disponibilité',
      completed: profile?.skills && profile.skills.length > 0 && profile?.years_of_experience,
      action: { label: 'Compléter', link: '/profile?section=experience' },
      priority: 6,
    },
  ]

  const completedSteps = requiredSteps.filter((s) => s.completed).length
  const nextStep = requiredSteps.find((s) => !s.completed)
  const allCompleted = completedSteps === requiredSteps.length

  return (
    <Layout>
      <div className="space-y-6">
        {/* Welcome Banner */}
        <div className="bg-gradient-to-r from-jlc-purple-600 via-jlc-purple-700 to-jlc-neon-pink-600 rounded-xl shadow-xl p-8 text-white relative overflow-hidden">
          {/* Background pattern */}
          <div className="absolute inset-0 opacity-10">
            <div
              className="absolute inset-0"
              style={{
                backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
                backgroundSize: '32px 32px',
              }}
            ></div>
          </div>

          <div className="relative z-10">
            <div className="flex items-start gap-2 mb-2">
              <SparklesIcon className="h-6 w-6 text-yellow-300" />
              <span className="text-sm font-medium text-purple-200 uppercase tracking-wide">
                Bienvenue chez JLC Group
              </span>
            </div>
            <h1 className="text-3xl md:text-4xl font-bold mb-2">
              Complétez votre profil de candidat 🎯
            </h1>
            <p className="text-purple-100 text-lg">
              Finalisez votre inscription pour accéder aux offres de missions et postuler
            </p>

            {/* Progress Bar */}
            <div className="mt-6 bg-white bg-opacity-20 backdrop-blur-sm rounded-lg p-4 border border-white border-opacity-30">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Progression du profil</span>
                <span className="text-lg font-bold">{completionPercentage}%</span>
              </div>
              <div className="w-full bg-white bg-opacity-30 rounded-full h-3 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-green-400 to-emerald-500 h-3 rounded-full transition-all duration-500 shadow-lg"
                  style={{ width: `${completionPercentage}%` }}
                ></div>
              </div>
              <p className="text-sm text-purple-100 mt-2">
                {completedSteps} sur {requiredSteps.length} étapes complétées
              </p>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Steps */}
          <div className="lg:col-span-2 space-y-4">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Étapes requises pour devenir intérimaire
            </h2>

            {requiredSteps.map((step, index) => (
              <Card
                key={step.id}
                className={`relative ${
                  step.completed
                    ? 'bg-green-50 border-green-200'
                    : nextStep?.id === step.id
                    ? 'border-jlc-purple-500 border-2 shadow-md'
                    : ''
                }`}
              >
                <div className="flex items-start gap-4">
                  {/* Step number/status */}
                  <div
                    className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                      step.completed
                        ? 'bg-green-500 text-white'
                        : nextStep?.id === step.id
                        ? 'bg-jlc-purple-600 text-white'
                        : 'bg-gray-200 text-gray-600'
                    }`}
                  >
                    {step.completed ? <CheckCircleIcon className="h-6 w-6" /> : index + 1}
                  </div>

                  {/* Content */}
                  <div className="flex-1">
                    <div className="flex items-start justify-between">
                      <div>
                        <h3
                          className={`text-lg font-semibold ${
                            step.completed ? 'text-green-900' : 'text-gray-900'
                          }`}
                        >
                          {step.title}
                          {nextStep?.id === step.id && (
                            <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-jlc-purple-100 text-jlc-purple-800">
                              Prochaine étape
                            </span>
                          )}
                        </h3>
                        <p className={`text-sm mt-1 ${step.completed ? 'text-green-700' : 'text-gray-600'}`}>
                          {step.description}
                        </p>
                      </div>
                      {step.completed && (
                        <CheckCircleIcon className="h-6 w-6 text-green-500 flex-shrink-0" />
                      )}
                    </div>

                    {/* Action button */}
                    {!step.completed && step.action && (
                      <div className="mt-3">
                        {step.action.handler === 'sendVerificationEmail' ? (
                          <button
                            onClick={handleSendVerificationEmail}
                            disabled={isSendingEmail}
                            className="inline-flex items-center px-4 py-2 bg-jlc-purple-600 text-white text-sm font-medium rounded-lg hover:bg-jlc-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            {isSendingEmail ? 'Envoi...' : step.action.label}
                            <ArrowRightIcon className="h-4 w-4 ml-2" />
                          </button>
                        ) : (
                          <Link
                            to={step.action.link}
                            className="inline-flex items-center px-4 py-2 bg-jlc-purple-600 text-white text-sm font-medium rounded-lg hover:bg-jlc-purple-700 transition-colors"
                          >
                            {step.action.label}
                            <ArrowRightIcon className="h-4 w-4 ml-2" />
                          </Link>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {/* Right Column - Status & Info */}
          <div className="space-y-6">
            {/* Status Card */}
            <Card className={allCompleted ? 'bg-green-50 border-green-200' : 'bg-orange-50 border-orange-200'}>
              <div className="text-center py-4">
                {allCompleted ? (
                  <>
                    <CheckCircleIcon className="h-16 w-16 text-green-500 mx-auto mb-3" />
                    <h3 className="text-lg font-bold text-green-900 mb-2">Profil complet ! 🎉</h3>
                    <p className="text-sm text-green-700 mb-4">
                      Votre profil est complet. Vous pouvez maintenant consulter les missions disponibles et
                      postuler.
                    </p>
                    <Link
                      to="/offres"
                      className="inline-flex items-center px-4 py-2 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors"
                    >
                      Voir les missions
                      <ArrowRightIcon className="h-4 w-4 ml-2" />
                    </Link>
                  </>
                ) : (
                  <>
                    <ClockIcon className="h-16 w-16 text-orange-500 mx-auto mb-3" />
                    <h3 className="text-lg font-bold text-orange-900 mb-2">Profil en cours</h3>
                    <p className="text-sm text-orange-700 mb-2">
                      Encore {requiredSteps.length - completedSteps} étape(s) à compléter
                    </p>
                    <div className="mt-4 p-3 bg-white rounded-lg">
                      <p className="text-xs text-gray-600">
                        <strong>💡 Conseil :</strong> Complétez toutes les étapes pour accéder aux offres de
                        missions et maximiser vos chances.
                      </p>
                    </div>
                  </>
                )}
              </div>
            </Card>

            {/* Help Card */}
            <Card className="bg-blue-50 border-blue-200">
              <div className="flex items-start gap-3">
                <ExclamationTriangleIcon className="h-6 w-6 text-blue-600 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold text-blue-900 mb-1">Besoin d'aide ?</h4>
                  <p className="text-sm text-blue-700 mb-3">
                    Notre équipe est là pour vous accompagner dans votre inscription.
                  </p>
                  <a
                    href="mailto:support@jlcgroup.ga"
                    className="text-sm text-blue-600 hover:text-blue-700 font-medium underline"
                  >
                    Contacter le support
                  </a>
                </div>
              </div>
            </Card>

            {/* Quick Links */}
            <Card>
              <h4 className="font-semibold text-gray-900 mb-3">Liens rapides</h4>
              <div className="space-y-2">
                <Link
                  to="/profile"
                  className="flex items-center gap-2 text-sm text-gray-700 hover:text-jlc-purple-600 transition-colors"
                >
                  <UserCircleIcon className="h-4 w-4" />
                  Mon profil complet
                </Link>
                <Link
                  to="/profile?tab=documents"
                  className="flex items-center gap-2 text-sm text-gray-700 hover:text-jlc-purple-600 transition-colors"
                >
                  <DocumentTextIcon className="h-4 w-4" />
                  Mes documents
                </Link>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </Layout>
  )
}
