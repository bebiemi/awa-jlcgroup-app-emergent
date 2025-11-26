/**
 * Profile Completion Widget
 * Shows profile completion percentage and missing fields
 */
import React from 'react'
import Card from '@/components/Card'
import { Link } from 'react-router-dom'
import { CheckCircleIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline'
import { useGetMyProfileQuery } from '@/features/profile/api/profileApi'
import { useValidationTypes } from '@/hooks/useAppConfig'
import { ValidationTypes } from '@/constants/iamConstants'

export default function ProfileCompletionWidget() {
  const { data: profile, isLoading } = useGetMyProfileQuery()
  const validationTypes = useValidationTypes()

  if (isLoading) {
    return (
      <Card>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div className="h-20 bg-gray-200 rounded"></div>
        </div>
      </Card>
    )
  }

  const completeness = profile?.profile?.profile_completion_percentage || 0
  const resolvedValidationTypes = {
    interim: validationTypes.interim || ValidationTypes.INTERIM,
  }
  
  const getMissingFields = () => {
    if (!profile?.profile) return []
    const p = profile.profile
    const missing = []
    if (!p.first_name) missing.push('Prénom')
    if (!p.last_name) missing.push('Nom')
    if (!p.phone) missing.push('Téléphone')
    if (!p.photo_url) missing.push('Photo de profil')
    if (!p.address) missing.push('Adresse')
    if (!p.date_of_birth) missing.push('Date de naissance')
    // Additional fields based on profile type
    if (profile.profile_type === resolvedValidationTypes.interim) {
      if (!p.skills || p.skills.length === 0) missing.push('Compétences')
      if (!p.years_of_experience) missing.push('Années d\'expérience')
      if (!p.cv_document_id) missing.push('CV')
      if (!p.available_immediately && !p.available_from_date) missing.push('Disponibilité')
    }
    return missing
  }

  const missingFields = getMissingFields()
  const isComplete = completeness >= 100

  // Color based on completion
  const getColorClasses = () => {
    if (completeness >= 90) return 'from-green-500 to-emerald-600'
    if (completeness >= 70) return 'from-yellow-500 to-orange-600'
    if (completeness >= 50) return 'from-orange-500 to-red-600'
    return 'from-red-500 to-pink-600'
  }

  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Complétion du profil</h3>
        {isComplete ? (
          <CheckCircleIcon className="h-6 w-6 text-green-500" />
        ) : (
          <ExclamationCircleIcon className="h-6 w-6 text-orange-500" />
        )}
      </div>

      {/* Progress Bar */}
      <div className="relative pt-1">
        <div className="flex mb-2 items-center justify-between">
          <div>
            <span className={`text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full ${
              isComplete ? 'text-green-600 bg-green-200' : 'text-orange-600 bg-orange-200'
            }`}>
              {isComplete ? 'Complet' : 'En cours'}
            </span>
          </div>
          <div className="text-right">
            <span className="text-xl font-bold text-gray-900">{completeness}%</span>
          </div>
        </div>
        <div className="overflow-hidden h-3 mb-4 text-xs flex rounded-full bg-gray-200">
          <div
            style={{ width: `${completeness}%` }}
            className={`shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-gradient-to-r ${getColorClasses()} transition-all duration-500`}
          ></div>
        </div>
      </div>

      {/* Missing Fields */}
      {!isComplete && missingFields.length > 0 && (
        <div className="mt-4 p-3 bg-orange-50 border border-orange-200 rounded-lg">
          <p className="text-sm font-medium text-orange-900 mb-2">
            Champs manquants ({missingFields.length}) :
          </p>
          <ul className="text-sm text-orange-700 space-y-1">
            {missingFields.slice(0, 5).map((field, index) => (
              <li key={index} className="flex items-center">
                <span className="inline-block w-1.5 h-1.5 bg-orange-500 rounded-full mr-2"></span>
                {field}
              </li>
            ))}
            {missingFields.length > 5 && (
              <li className="text-xs text-orange-600 italic">
                et {missingFields.length - 5} autre(s)...
              </li>
            )}
          </ul>
        </div>
      )}

      {/* Action Button */}
      <div className="mt-4">
        <Link
          to="/profile"
          className={`block w-full text-center px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            isComplete
              ? 'bg-green-100 text-green-700 hover:bg-green-200'
              : 'bg-gradient-to-r from-jlc-purple-500 to-jlc-purple-600 text-white hover:from-jlc-purple-600 hover:to-jlc-purple-700'
          }`}
        >
          {isComplete ? 'Voir mon profil' : 'Compléter mon profil'}
        </Link>
      </div>
    </Card>
  )
}
