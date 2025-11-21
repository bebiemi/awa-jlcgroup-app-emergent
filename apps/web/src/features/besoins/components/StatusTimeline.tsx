import { StatusHistoryEntry } from '../api/besoinsApi'
import { WorkflowConfig } from '../api/configApi'
import { CheckCircleIcon, ArrowRightIcon } from '@heroicons/react/24/solid'

interface StatusTimelineProps {
  history: StatusHistoryEntry[]
  workflowConfig?: WorkflowConfig
}

export default function StatusTimeline({ history, workflowConfig }: StatusTimelineProps) {
  const getStatusConfig = (statusKey: string) => {
    if (!workflowConfig) return null
    return workflowConfig.statuses.find((s) => s.key === statusKey)
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const getStatusLabel = (statusKey?: string) => {
    if (!statusKey) return 'Création'
    const config = getStatusConfig(statusKey)
    return config?.label.fr || statusKey
  }

  const getStatusColor = (statusKey?: string) => {
    if (!statusKey) return '#9CA3AF'
    const config = getStatusConfig(statusKey)
    return config?.color || '#9CA3AF'
  }

  if (!history || history.length === 0) {
    return (
      <div className="text-center py-4 text-gray-500 text-sm">
        Aucun historique disponible
      </div>
    )
  }

  // Sort history by date (most recent first)
  const sortedHistory = [...history].sort(
    (a, b) => new Date(b.changed_at).getTime() - new Date(a.changed_at).getTime()
  )

  return (
    <div className="space-y-4">
      {sortedHistory.map((entry, index) => {
        const isLast = index === sortedHistory.length - 1
        const toStatusConfig = getStatusConfig(entry.to_status)
        const statusColor = getStatusColor(entry.to_status)

        return (
          <div key={index} className="relative">
            {/* Timeline Line */}
            {!isLast && (
              <div
                className="absolute left-4 top-10 w-0.5 h-full -ml-px"
                style={{ backgroundColor: '#E5E7EB' }}
              />
            )}

            {/* Timeline Item */}
            <div className="flex gap-3">
              {/* Icon */}
              <div
                className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center shadow-sm"
                style={{ backgroundColor: `${statusColor}20` }}
              >
                <CheckCircleIcon
                  className="h-5 w-5"
                  style={{ color: statusColor }}
                />
              </div>

              {/* Content */}
              <div className="flex-1 pb-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    {/* Status Change */}
                    <div className="flex items-center gap-2 mb-1">
                      {entry.from_status && (
                        <>
                          <span
                            className="text-sm font-medium"
                            style={{ color: getStatusColor(entry.from_status) }}
                          >
                            {getStatusLabel(entry.from_status)}
                          </span>
                          <ArrowRightIcon className="h-4 w-4 text-gray-400" />
                        </>
                      )}
                      <span
                        className="text-sm font-semibold"
                        style={{ color: statusColor }}
                      >
                        {getStatusLabel(entry.to_status)}
                      </span>
                    </div>

                    {/* Author and Date */}
                    <div className="flex items-center gap-2 text-xs text-gray-600 mb-2">
                      <span>Par {entry.changed_by_name}</span>
                      <span>•</span>
                      <span>{formatDate(entry.changed_at)}</span>
                    </div>

                    {/* Comment */}
                    {entry.comment && (
                      <div className="mt-2 p-2 bg-gray-50 rounded border border-gray-200">
                        <p className="text-sm text-gray-700">{entry.comment}</p>
                      </div>
                    )}
                  </div>

                  {/* Status Badge */}
                  {toStatusConfig && (
                    <span
                      className="text-xs px-2 py-1 rounded-full font-medium flex-shrink-0"
                      style={{
                        backgroundColor: `${statusColor}20`,
                        color: statusColor,
                      }}
                    >
                      {toStatusConfig.label.fr}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
