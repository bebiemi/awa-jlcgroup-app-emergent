import React, { useState } from 'react'
import { CheckCircle2, TrendingUp, AlertCircle } from 'lucide-react'
import type { MatchingResult } from '../api/missionApi'

interface MatchingBadgeProps {
  matching: MatchingResult
  variant?: 'default' | 'compact' | 'detailed'
  showTooltip?: boolean
}

export const MatchingBadge: React.FC<MatchingBadgeProps> = ({ 
  matching, 
  variant = 'default',
  showTooltip = true 
}) => {
  const { score, is_excellent_match, is_good_match, breakdown, matched_skills, recommendations } = matching

  // Déterminer la couleur et l'icône selon le score
  const getScoreColor = () => {
    if (score >= 85) return 'bg-green-500 hover:bg-green-600'
    if (score >= 70) return 'bg-blue-500 hover:bg-blue-600'
    if (score >= 50) return 'bg-yellow-500 hover:bg-yellow-600'
    return 'bg-gray-400 hover:bg-gray-500'
  }

  const getScoreLabel = () => {
    if (is_excellent_match) return 'Excellent match'
    if (is_good_match) return 'Bon match'
    if (score >= 50) return 'Match partiel'
    return 'Match faible'
  }

  const getIcon = () => {
    if (is_excellent_match) return <CheckCircle2 className="h-3 w-3" />
    if (is_good_match) return <TrendingUp className="h-3 w-3" />
    return <AlertCircle className="h-3 w-3" />
  }

  const [showTooltipState, setShowTooltipState] = useState(false)

  // Badge compact (juste le score)
  if (variant === 'compact') {
    return (
      <span className={`${getScoreColor()} text-white text-xs px-2 py-1 rounded-full inline-block`}>
        {Math.round(score)}%
      </span>
    )
  }

  // Badge avec tooltip
  const badge = (
    <span className={`${getScoreColor()} text-white flex items-center gap-1 px-2 py-1 rounded-full text-sm cursor-pointer`}>
      {getIcon()}
      <span>{Math.round(score)}%</span>
      {variant === 'detailed' && <span className="ml-1 text-xs opacity-90">{getScoreLabel()}</span>}
    </span>
  )

  if (!showTooltip) {
    return badge
  }

  return (
    <div 
      className="relative inline-block"
      onMouseEnter={() => setShowTooltipState(true)}
      onMouseLeave={() => setShowTooltipState(false)}
    >
      {badge}
      
      {showTooltipState && (
        <div className="absolute z-50 w-80 max-w-sm p-4 mt-2 bg-white rounded-lg shadow-xl border border-gray-200 right-0"
             style={{ top: '100%' }}>
          <div className="space-y-3">
            {/* Score global */}
            <div className="border-b pb-2">
              <p className="font-semibold text-sm">{getScoreLabel()}</p>
              <p className="text-xs text-muted-foreground">Score de correspondance : {Math.round(score)}%</p>
            </div>

            {/* Détails par catégorie */}
            <div className="space-y-2">
              <p className="text-xs font-medium">Détails :</p>
              
              {/* Compétences */}
              <div className="flex justify-between items-center text-xs">
                <span className="text-muted-foreground">Compétences</span>
                <span className="font-medium">
                  {Math.round(breakdown.skills.score)}% 
                  {breakdown.skills.matched !== undefined && breakdown.skills.total_required !== undefined && (
                    <span className="text-muted-foreground ml-1">
                      ({breakdown.skills.matched}/{breakdown.skills.total_required})
                    </span>
                  )}
                </span>
              </div>

              {/* Expérience */}
              <div className="flex justify-between items-center text-xs">
                <span className="text-muted-foreground">Expérience</span>
                <span className="font-medium">
                  {Math.round(breakdown.experience.score)}%
                  {breakdown.experience.status === 'overqualified' && (
                    <span className="text-blue-500 ml-1">(surqualifié)</span>
                  )}
                  {breakdown.experience.status === 'underqualified' && (
                    <span className="text-orange-500 ml-1">(sous-qualifié)</span>
                  )}
                </span>
              </div>

              {/* Secteur */}
              <div className="flex justify-between items-center text-xs">
                <span className="text-muted-foreground">Secteur</span>
                <span className="font-medium">{Math.round(breakdown.sectors.score)}%</span>
              </div>

              {/* Niveau d'études */}
              <div className="flex justify-between items-center text-xs">
                <span className="text-muted-foreground">Formation</span>
                <span className="font-medium">{Math.round(breakdown.education.score)}%</span>
              </div>
            </div>

            {/* Compétences matchées */}
            {matched_skills.length > 0 && (
              <div className="border-t pt-2">
                <p className="text-xs font-medium mb-1">Compétences correspondantes :</p>
                <div className="flex flex-wrap gap-1">
                  {matched_skills.slice(0, 5).map((skill, idx) => (
                    <Badge key={idx} variant="secondary" className="text-xs">
                      {skill}
                    </Badge>
                  ))}
                  {matched_skills.length > 5 && (
                    <span className="text-xs text-muted-foreground">+{matched_skills.length - 5} autres</span>
                  )}
                </div>
              </div>
            )}

            {/* Recommandations */}
            {recommendations.length > 0 && (
              <div className="border-t pt-2">
                <p className="text-xs font-medium mb-1">Suggestions :</p>
                <ul className="text-xs text-gray-600 space-y-1">
                  {recommendations.slice(0, 2).map((rec, idx) => (
                    <li key={idx} className="flex items-start gap-1">
                      <span className="text-orange-500 mt-0.5">•</span>
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
