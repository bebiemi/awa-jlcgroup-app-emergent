import { useReferences } from '@/hooks/useReferences'

interface ReferenceSelectProps {
  category: string
  value: string
  onChange: (value: string) => void
  label?: string
  required?: boolean
  disabled?: boolean
  className?: string
}

export default function ReferenceSelect({
  category,
  value,
  onChange,
  label,
  required = false,
  disabled = false,
  className = ''
}: ReferenceSelectProps) {
  const { options, isLoading } = useReferences(category)

  if (isLoading) {
    return <div className="animate-pulse h-10 bg-gray-200 rounded"></div>
  }

  return (
    <div className={className}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
      )}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required={required}
        disabled={disabled}
        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-jlc-purple-500 focus:ring-jlc-purple-500"
      >
        <option value="">Sélectionner...</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  )
}
