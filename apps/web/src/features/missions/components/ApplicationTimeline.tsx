import React from 'react'
import { format } from 'date-fns'
import { fr } from 'date-fns/locale'
import { 
  CheckCircle2, 
  Clock, 
  Circle, 
  XCircle,
  User,
  FileText
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import type { ApplicationHistoryEntry } from '../api/missionApi'

interface ApplicationTimelineProps {
  history: ApplicationHistoryEntry[]
  currentStatus: string
  showStats?: boolean
  totalDurationDays?: number
}

export const ApplicationTimeline: React.FC<ApplicationTimelineProps> = ({ 
  history, 
  currentStatus,
  showStats = false,
  totalDurationDays = 0
}) => {
  // Mapper les statuts à des labels français
  const getStatusLabel = (status: string): string => {
    const statusMap: Record<string, string> = {
      'submitted': 'Candidature soumise',
      'received': 'Candidature reçue',
      'under_review': 'En cours de revue',
      'shortlisted': 'Présélectionné(e)',
      'rejected_initial': 'Non retenu(e)',
      'interview_scheduled': 'Entretien programmé',
      'interview_completed': 'Entretien réalisé',
      'selected_for_client': 'Sélectionné pour le client',
      'rejected_after_interview': 'Non retenu après entretien',
      'sent_to_client': 'Envoyé au client',
      'selected_by_client': 'Retenu par le client',
      'rejected_by_client': 'Non retenu par le client',
      'standby': 'En attente',
      'medical_check_pending': 'Visite médicale en attente',
      'medical_approved': 'Visite médicale validée',
      'medical_rejected': 'Visite médicale non validée',
      'contract_pending': 'Contrat en attente',
      'contract_signed': 'Contrat signé',
      'hired': 'Embauché(e)',
      'rejected': 'Candidature rejetée',
      'withdrawn': 'Candidature retirée',
    }
    return statusMap[status] || status
  }

  // Déterminer l'état d'une entrée (completed, in_progress, rejected, pending)
  const getEntryState = (entry: ApplicationHistoryEntry, index: number): 'completed' | 'in_progress' | 'rejected' | 'pending' => {
    const isLast = index === history.length - 1
    const isRejected = entry.new_status.includes('rejected') || entry.new_status === 'withdrawn'
    
    if (isRejected) return 'rejected'
    if (isLast) return 'in_progress'
    return 'completed'
  }

  // Icône selon l'état
  const getIcon = (state: string) => {
    switch (state) {
      case 'completed':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />
      case 'in_progress':
        return <Clock className="h-5 w-5 text-blue-500" />
      case 'rejected':
        return <XCircle className="h-5 w-5 text-red-500" />
      default:
        return <Circle className="h-5 w-5 text-gray-300" />
    }
  }

  // Couleur de la ligne de connexion
  const getLineColor = (state: string) => {
    switch (state) {
      case 'completed':
        return 'bg-green-500'
      case 'in_progress':
        return 'bg-blue-500'
      case 'rejected':
        return 'bg-red-500'
      default:
        return 'bg-gray-300'
    }
  }

  if (!history || history.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <p>Aucun historique disponible</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Stats */}
      {showStats && totalDurationDays > 0 && (
        <Card className="bg-muted/50">
          <CardContent className="pt-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Durée totale</span>
              <span className="font-medium">{totalDurationDays} jour{totalDurationDays > 1 ? 's' : ''}</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Timeline */}
      <div className="relative">
        {history.map((entry, index) => {
          const state = getEntryState(entry, index)
          const isLast = index === history.length - 1
          const date = new Date(entry.changed_at_iso || entry.changed_at)

          return (
            <div key={entry.id} className="relative pb-8">
              {/* Ligne de connexion */}
              {!isLast && (
                <div 
                  className={`absolute left-[10px] top-[28px] w-[2px] h-full ${getLineColor(state)}`}
                />
              )}

              {/* Contenu de l'étape */}
              <div className="flex items-start gap-4">
                {/* Icône */}
                <div className="relative z-10 flex-shrink-0 bg-background">
                  {getIcon(state)}
                </div>

                {/* Détails */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2 flex-wrap">
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm">
                        {getStatusLabel(entry.new_status)}
                      </p>
                      
                      {entry.old_status && (
                        <p className="text-xs text-muted-foreground">
                          De : {getStatusLabel(entry.old_status)}
                        </p>
                      )}
                    </div>

                    {/* Badge état */}
                    {isLast && (
                      <Badge variant={state === 'rejected' ? 'destructive' : 'default'} className="text-xs">
                        En cours
                      </Badge>
                    )}
                  </div>

                  {/* Date et utilisateur */}
                  <div className="mt-2 space-y-1">
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Clock className="h-3 w-3" />
                      <span>
                        {format(date, 'dd MMMM yyyy à HH:mm', { locale: fr })}
                      </span>
                    </div>

                    {entry.changed_by_name && (
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <User className="h-3 w-3" />
                        <span>{entry.changed_by_name}</span>
                      </div>
                    )}

                    {entry.reason && (
                      <div className="flex items-start gap-2 text-xs text-muted-foreground mt-2">
                        <FileText className="h-3 w-3 mt-0.5 flex-shrink-0" />
                        <span className="italic">{entry.reason}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// Composant pour afficher la timeline dans une modal
export const ApplicationTimelineModal: React.FC<{
  applicationId: string
  history: ApplicationHistoryEntry[]
  currentStatus: string
  onClose: () => void
}> = ({ applicationId, history, currentStatus, onClose }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Suivi de la candidature</CardTitle>
      </CardHeader>
      <CardContent>
        <ApplicationTimeline 
          history={history} 
          currentStatus={currentStatus}
          showStats
        />
      </CardContent>
    </Card>
  )
}
