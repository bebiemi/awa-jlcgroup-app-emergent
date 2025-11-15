/**
 * Recommended Missions Widget
 * Shows AI-matched missions for postulants/intérimaires
 */
import React from 'react'
import Card from '@/components/Card'
import { Link } from 'react-router-dom'
import { BriefcaseIcon, MapPinIcon, CurrencyEuroIcon, SparklesIcon } from '@heroicons/react/24/outline'
import { useDashboardWidgets } from '@/features/config/api/appConfigApi'

// Mock missions for now (will be replaced with AI matching API)
const mockMissions = [
  {
    id: '1',
    title: 'Développeur Full Stack',
    company: 'TechCorp Gabon',
    location: 'Libreville, Gabon',
    salary: '2500-3500',
    match_score: 95,
    skills: ['React', 'Node.js', 'MongoDB'],
    duration: '6 mois',
  },
  {
    id: '2',
    title: 'Assistant Administratif',
    company: 'Services Plus',
    location: 'Port-Gentil, Gabon',
    salary: '1500-2000',
    match_score: 85,
    skills: ['Bureautique', 'Communication', 'Organisation'],
    duration: '3 mois',
  },
  {
    id: '3',
    title: 'Commercial B2B',
    company: 'Ventes Direct',
    location: 'Libreville, Gabon',
    salary: '1800-2500',
    match_score: 78,
    skills: ['Vente', 'Négociation', 'CRM'],
    duration: '12 mois',
  },
]

export default function RecommendedMissionsWidget() {
  const { data: widgetsConfig } = useDashboardWidgets()
  
  // Get max items from config (default 5)
  const maxItems = widgetsConfig?.recommended_missions?.max_items || 5
  const missions = mockMissions.slice(0, maxItems)

  const getMatchColor = (score: number) => {
    if (score >= 90) return 'text-green-600 bg-green-100'
    if (score >= 75) return 'text-blue-600 bg-blue-100'
    if (score >= 60) return 'text-orange-600 bg-orange-100'
    return 'text-gray-600 bg-gray-100'
  }

  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <SparklesIcon className="h-6 w-6 text-jlc-purple-600" />
          <h3 className="text-lg font-semibold text-gray-900">Missions Recommandées</h3>
        </div>
        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
          IA Match
        </span>
      </div>

      <p className="text-sm text-gray-600 mb-4">
        Nos algorithmes ont trouvé ces missions qui correspondent à votre profil 🎯
      </p>

      {missions.length === 0 ? (
        <div className="text-center py-8">
          <BriefcaseIcon className="h-12 w-12 text-gray-300 mx-auto mb-3" />
          <p className="text-sm text-gray-500">Aucune mission disponible pour le moment</p>
          <p className="text-xs text-gray-400 mt-2">Complétez votre profil pour de meilleures recommandations</p>
        </div>
      ) : (
        <div className="space-y-3">
          {missions.map((mission, index) => (
            <Link
              key={mission.id}
              to={`/missions/${mission.id}`}
              className="block p-4 bg-gradient-to-br from-white to-gray-50 hover:from-jlc-purple-50 hover:to-jlc-purple-100 border border-gray-200 hover:border-jlc-purple-300 rounded-lg transition-all duration-200 hover:shadow-md"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-semibold text-gray-900">{mission.title}</h4>
                    {index === 0 && (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-gradient-to-r from-yellow-400 to-orange-500 text-white text-xs font-bold rounded-full">
                        <SparklesIcon className="h-3 w-3" />
                        TOP
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600">{mission.company}</p>
                </div>
                <span className={`flex-shrink-0 px-2.5 py-1 rounded-full text-xs font-bold ${getMatchColor(mission.match_score)}`}>
                  {mission.match_score}% Match
                </span>
              </div>

              <div className="flex flex-wrap items-center gap-3 text-xs text-gray-600 mt-3">
                <span className="flex items-center gap-1">
                  <MapPinIcon className="h-4 w-4" />
                  {mission.location}
                </span>
                <span className="flex items-center gap-1">
                  <CurrencyEuroIcon className="h-4 w-4" />
                  {mission.salary}€
                </span>
                <span className="flex items-center gap-1">
                  <BriefcaseIcon className="h-4 w-4" />
                  {mission.duration}
                </span>
              </div>

              <div className="flex flex-wrap gap-1 mt-3">
                {mission.skills.slice(0, 3).map((skill, i) => (
                  <span
                    key={i}
                    className="inline-block px-2 py-0.5 bg-jlc-purple-100 text-jlc-purple-700 text-xs rounded"
                  >
                    {skill}
                  </span>
                ))}
                {mission.skills.length > 3 && (
                  <span className="inline-block px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded">
                    +{mission.skills.length - 3}
                  </span>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}

      <div className="mt-4 pt-4 border-t border-gray-200">
        <Link
          to="/missions"
          className="block w-full text-center px-4 py-2 bg-gradient-to-r from-jlc-purple-500 to-jlc-purple-600 text-white rounded-lg text-sm font-medium hover:from-jlc-purple-600 hover:to-jlc-purple-700 transition-colors"
        >
          Voir toutes les missions
        </Link>
      </div>
    </Card>
  )
}
