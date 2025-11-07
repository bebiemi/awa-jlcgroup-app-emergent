import { PresenceStatus } from '@/features/presence/api/presenceApi'
import clsx from 'clsx'

interface UserStatusIndicatorProps {
  status: PresenceStatus
  size?: 'sm' | 'md' | 'lg'
  showTooltip?: boolean
  className?: string
}

const STATUS_CONFIG = {
  online: {
    color: 'bg-green-500',
    label: 'En ligne',
    border: 'ring-green-400',
  },
  away: {
    color: 'bg-yellow-500',
    label: 'Inactif',
    border: 'ring-yellow-400',
  },
  do_not_disturb: {
    color: 'bg-red-500',
    label: 'Ne pas déranger',
    border: 'ring-red-400',
  },
  offline: {
    color: 'bg-gray-400',
    label: 'Absent',
    border: 'ring-gray-300',
  },
  invisible: {
    color: 'bg-gray-600',
    label: 'Hors ligne',
    border: 'ring-gray-500',
  },
}

const SIZE_CONFIG = {
  sm: 'w-2 h-2',
  md: 'w-3 h-3',
  lg: 'w-4 h-4',
}

export default function UserStatusIndicator({
  status,
  size = 'md',
  showTooltip = true,
  className = '',
}: UserStatusIndicatorProps) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.offline

  return (
    <div
      className={clsx('relative inline-flex items-center justify-center', className)}
      title={showTooltip ? config.label : undefined}
    >
      <span
        className={clsx(
          'rounded-full',
          config.color,
          SIZE_CONFIG[size],
          'ring-2 ring-white',
          'shadow-sm'
        )}
      />
    </div>
  )
}
