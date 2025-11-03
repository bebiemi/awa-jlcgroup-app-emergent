import { 
  PencilSquareIcon, 
  TrashIcon, 
  EyeIcon,
  CheckCircleIcon,
  XCircleIcon,
  UserPlusIcon,
  ArrowPathIcon,
  NoSymbolIcon,
  ClockIcon
} from '@heroicons/react/24/outline'

type ActionType = 'edit' | 'delete' | 'view' | 'approve' | 'reject' | 'assign' | 'reset' | 'block' | 'pending' | 'custom'

interface ActionButtonProps {
  type: ActionType
  onClick: () => void
  label?: string
  disabled?: boolean
  size?: 'sm' | 'md' | 'lg'
  icon?: any  // For custom type
  color?: string  // For custom type
}

const actionConfig = {
  edit: { icon: PencilSquareIcon, color: 'text-blue-600 hover:bg-blue-50', label: 'Modifier' },
  delete: { icon: TrashIcon, color: 'text-red-600 hover:bg-red-50', label: 'Supprimer' },
  view: { icon: EyeIcon, color: 'text-gray-600 hover:bg-gray-50', label: 'Voir' },
  approve: { icon: CheckCircleIcon, color: 'text-green-600 hover:bg-green-50', label: 'Approuver' },
  reject: { icon: XCircleIcon, color: 'text-red-600 hover:bg-red-50', label: 'Rejeter' },
  assign: { icon: UserPlusIcon, color: 'text-blue-600 hover:bg-blue-50', label: 'Assigner' },
  reset: { icon: ArrowPathIcon, color: 'text-orange-600 hover:bg-orange-50', label: 'Réinitialiser' },
  block: { icon: NoSymbolIcon, color: 'text-red-600 hover:bg-red-50', label: 'Bloquer' },
  pending: { icon: ClockIcon, color: 'text-yellow-600 hover:bg-yellow-50', label: 'En attente' },
}

export default function ActionButton({ 
  type, 
  onClick, 
  label, 
  disabled = false,
  size = 'md',
  icon: CustomIcon,
  color: customColor
}: ActionButtonProps) {
  // For custom type, use provided icon and color
  const config = type === 'custom' 
    ? { icon: CustomIcon, color: customColor || 'text-gray-600 hover:bg-gray-50', label: label || 'Action' }
    : actionConfig[type]
    
  const Icon = config.icon
  
  const sizeClasses = {
    sm: 'p-1.5',
    md: 'p-2',
    lg: 'p-3',
  }
  
  const iconSizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-5 w-5',
    lg: 'h-6 w-6',
  }

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      title={label || config.label}
      className={`${sizeClasses[size]} rounded-lg transition ${config.color} disabled:opacity-50 disabled:cursor-not-allowed`}
    >
      <Icon className={iconSizeClasses[size]} />
    </button>
  )
}

// Export pour utilisation groupée
export function ActionButtonGroup({ children, className = '' }: { children: React.ReactNode, className?: string }) {
  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      {children}
    </div>
  )
}
