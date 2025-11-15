/**
 * Missing Documents Widget
 * Shows required documents that are missing
 */
import React from 'react'
import Card from '@/components/Card'
import { Link } from 'react-router-dom'
import { DocumentTextIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline'
import { useDocumentCategories } from '@/features/config/api/appConfigApi'
import { useAuth } from '@/hooks/useAuth'

export default function MissingDocumentsWidget() {
  const { data: categories, isLoading } = useDocumentCategories()
  const { user } = useAuth()

  if (isLoading) {
    return (
      <Card>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div className="h-16 bg-gray-200 rounded"></div>
        </div>
      </Card>
    )
  }

  if (!categories || !user) {
    return null
  }

  // Get user's primary role
  const userRole = user.roles?.[0] || 'interim'

  // Filter required documents for user's role
  const requiredDocs = categories.filter(
    (cat) => cat.required && cat.required_for_roles.includes(userRole)
  )

  // TODO: Fetch user's actual documents and filter out uploaded ones
  // For now, showing all required docs as missing (placeholder)
  const missingDocs = requiredDocs.slice(0, 3) // Show max 3

  if (missingDocs.length === 0) {
    return (
      <Card className="bg-green-50 border-green-200">
        <div className="flex items-start gap-3">
          <DocumentTextIcon className="h-6 w-6 text-green-600 flex-shrink-0" />
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-green-900">Documents à jour</h3>
            <p className="text-sm text-green-700 mt-1">
              Tous vos documents obligatoires sont à jour. Bravo ! ✓
            </p>
          </div>
        </div>
      </Card>
    )
  }

  return (
    <Card className="border-l-4 border-orange-500">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-2">
          <ExclamationTriangleIcon className="h-6 w-6 text-orange-500" />
          <h3 className="text-lg font-semibold text-gray-900">Documents manquants</h3>
        </div>
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
          {missingDocs.length} manquant{missingDocs.length > 1 ? 's' : ''}
        </span>
      </div>

      <div className="space-y-3">
        {missingDocs.map((doc) => (
          <div key={doc.id} className="flex items-center gap-3 p-3 bg-orange-50 rounded-lg">
            <div className="flex-shrink-0">
              <DocumentTextIcon className="h-5 w-5 text-orange-600" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900">{doc.name.fr}</p>
              <p className="text-xs text-gray-600 mt-0.5">
                {doc.expirable ? 'Document expirable' : 'Document permanent'}
                {' • '}
                Max {doc.max_size_mb} MB
                {' • '}
                {doc.allowed_formats.join(', ').toUpperCase()}
              </p>
            </div>
            {doc.required && (
              <span className="flex-shrink-0 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                Obligatoire
              </span>
            )}
          </div>
        ))}
      </div>

      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
        <p className="text-xs text-gray-600">
          💡 <strong>Important :</strong> Certains documents sont obligatoires pour postuler aux missions.
          Téléchargez-les dès maintenant pour accélérer vos candidatures.
        </p>
      </div>

      <div className="mt-4">
        <Link
          to="/profile?tab=documents"
          className="block w-full text-center px-4 py-2 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-lg text-sm font-medium hover:from-orange-600 hover:to-orange-700 transition-colors"
        >
          Télécharger mes documents
        </Link>
      </div>
    </Card>
  )
}
