import { useReferences } from '@/hooks/useReferences'

interface StatusBadgeProps {
  category: string
  status: string
  showIcon?: boolean
  className?: string
}

export default function StatusBadge({
  category,
  status,
  showIcon = false,
  className = ''
}: StatusBadgeProps) {
  const { getLabel, getMetadata } = useReferences(category)
  
  const label = getLabel(status)
  const metadata = getMetadata(status)
  const color = metadata.color || '#6B7280'

  return (
    <span
      className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${className}`}
      style={{
        backgroundColor: `${color}20`,
        color: color,
        border: `1px solid ${color}`
      }}
    >
      {showIcon && metadata.icon && (
        <span className="text-sm">{metadata.icon}</span>
      )}
      {label}
    </span>
  )
}
