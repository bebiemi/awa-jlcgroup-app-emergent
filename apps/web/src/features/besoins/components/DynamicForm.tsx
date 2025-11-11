import { FormSchema, ReferenceDataItem } from '../api/configApi'

interface DynamicFormProps {
  schema: FormSchema
  data: Record<string, any>
  onChange: (data: Record<string, any>) => void
  errors: Record<string, string>
  referenceData?: Record<string, ReferenceDataItem[]>
  disabled?: boolean
}

export default function DynamicForm({
  schema,
  data,
  onChange,
  errors,
  referenceData = {},
  disabled = false,
}: DynamicFormProps) {
  const handleChange = (key: string, value: any) => {
    onChange({ ...data, [key]: value })
  }

  const shouldShowField = (field: any): boolean => {
    if (!field.depends_on) return true
    
    const dependentValue = data[field.depends_on]
    if (!field.depends_condition) return !!dependentValue
    
    // Simple equality check
    if (field.depends_condition.eq) {
      return dependentValue === field.depends_condition.eq
    }
    
    return true
  }

  const renderField = (field: any) => {
    if (!shouldShowField(field)) return null

    const label = field.label?.fr || field.key
    const placeholder = field.placeholder?.fr || ''
    const helpText = field.help_text?.fr
    const error = errors[field.key]
    const value = data[field.key] || ''

    const baseClasses = `w-full px-4 py-2 border ${
      error ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-jlc-purple-500'
    } rounded-lg focus:ring-2 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed`

    switch (field.type) {
      case 'text':
      case 'email':
      case 'phone':
        return (
          <div key={field.key} className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              {label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </label>
            <input
              type={field.type}
              value={value}
              onChange={(e) => handleChange(field.key, e.target.value)}
              placeholder={placeholder}
              disabled={disabled}
              className={baseClasses}
            />
            {helpText && <p className="text-sm text-gray-500">{helpText}</p>}
            {error && <p className="text-sm text-red-500">{error}</p>}
          </div>
        )

      case 'textarea':
        return (
          <div key={field.key} className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              {label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </label>
            <textarea
              value={value}
              onChange={(e) => handleChange(field.key, e.target.value)}
              placeholder={placeholder}
              disabled={disabled}
              rows={4}
              className={baseClasses}
            />
            {helpText && <p className="text-sm text-gray-500">{helpText}</p>}
            {error && <p className="text-sm text-red-500">{error}</p>}
          </div>
        )

      case 'number':
        return (
          <div key={field.key} className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              {label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </label>
            <input
              type="number"
              value={value}
              onChange={(e) => handleChange(field.key, parseFloat(e.target.value))}
              placeholder={placeholder}
              disabled={disabled}
              className={baseClasses}
            />
            {helpText && <p className="text-sm text-gray-500">{helpText}</p>}
            {error && <p className="text-sm text-red-500">{error}</p>}
          </div>
        )

      case 'date':
        return (
          <div key={field.key} className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              {label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </label>
            <input
              type="date"
              value={value}
              onChange={(e) => handleChange(field.key, e.target.value)}
              disabled={disabled}
              className={baseClasses}
            />
            {helpText && <p className="text-sm text-gray-500">{helpText}</p>}
            {error && <p className="text-sm text-red-500">{error}</p>}
          </div>
        )

      case 'select':
        // Get options from field or reference data
        let options = field.options || []
        if (referenceData[field.key]) {
          options = referenceData[field.key].map((item: ReferenceDataItem) => ({
            value: item.key,
            label: item.label,
            active: item.active,
          }))
        }

        return (
          <div key={field.key} className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              {label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </label>
            <select
              value={value}
              onChange={(e) => handleChange(field.key, e.target.value)}
              disabled={disabled}
              className={`${baseClasses} appearance-none`}
            >
              <option value="">Sélectionner...</option>
              {options
                .filter((opt: any) => opt.active !== false)
                .map((option: any) => (
                  <option key={option.value} value={option.value}>
                    {option.label?.fr || option.label}
                  </option>
                ))}
            </select>
            {helpText && <p className="text-sm text-gray-500">{helpText}</p>}
            {error && <p className="text-sm text-red-500">{error}</p>}
          </div>
        )

      case 'multi_select':
        // Get options from field or reference data
        let multiOptions = field.options || []
        if (field.key === 'competences_attendues' && referenceData['competences']) {
          multiOptions = referenceData['competences'].map((item: ReferenceDataItem) => ({
            value: item.key,
            label: item.label,
            active: item.active,
          }))
        }

        const selectedValues = Array.isArray(value) ? value : []

        return (
          <div key={field.key} className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              {label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </label>
            <div className="border border-gray-300 rounded-lg p-3 max-h-48 overflow-y-auto">
              {multiOptions
                .filter((opt: any) => opt.active !== false)
                .map((option: any) => (
                  <label
                    key={option.value}
                    className="flex items-center gap-2 py-1 hover:bg-gray-50 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={selectedValues.includes(option.value)}
                      onChange={(e) => {
                        const newValues = e.target.checked
                          ? [...selectedValues, option.value]
                          : selectedValues.filter((v: string) => v !== option.value)
                        handleChange(field.key, newValues)
                      }}
                      disabled={disabled}
                      className="rounded text-jlc-purple-600 focus:ring-jlc-purple-500"
                    />
                    <span className="text-sm text-gray-700">{option.label?.fr || option.label}</span>
                  </label>
                ))}
            </div>
            {helpText && <p className="text-sm text-gray-500">{helpText}</p>}
            {error && <p className="text-sm text-red-500">{error}</p>}
          </div>
        )

      case 'checkbox':
        return (
          <div key={field.key} className="space-y-2">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={!!value}
                onChange={(e) => handleChange(field.key, e.target.checked)}
                disabled={disabled}
                className="rounded text-jlc-purple-600 focus:ring-jlc-purple-500"
              />
              <span className="text-sm font-medium text-gray-700">
                {label}
                {field.required && <span className="text-red-500 ml-1">*</span>}
              </span>
            </label>
            {helpText && <p className="text-sm text-gray-500 ml-6">{helpText}</p>}
            {error && <p className="text-sm text-red-500 ml-6">{error}</p>}
          </div>
        )

      case 'file':
        return (
          <div key={field.key} className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              {label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </label>
            <input
              type="file"
              multiple
              disabled={disabled}
              onChange={(e) => {
                // TODO: Handle file upload
                console.log('Files:', e.target.files)
              }}
              className={baseClasses}
            />
            {helpText && <p className="text-sm text-gray-500">{helpText}</p>}
            {error && <p className="text-sm text-red-500">{error}</p>}
          </div>
        )

      default:
        return null
    }
  }

  // Group fields by group
  const groupedFields: Record<string, any[]> = {}
  const ungroupedFields: any[] = []

  schema.fields
    .filter((f) => f.active)
    .sort((a, b) => a.order - b.order)
    .forEach((field) => {
      if (field.group) {
        if (!groupedFields[field.group]) {
          groupedFields[field.group] = []
        }
        groupedFields[field.group].push(field)
      } else {
        ungroupedFields.push(field)
      }
    })

  return (
    <div className="space-y-8">
      {/* Ungrouped fields */}
      {ungroupedFields.length > 0 && (
        <div className="space-y-4">
          {ungroupedFields.map((field) => renderField(field))}
        </div>
      )}

      {/* Grouped fields */}
      {schema.groups?.map((group: any) => {
        const fields = groupedFields[group.key] || []
        if (fields.length === 0) return null

        return (
          <div key={group.key} className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 border-b border-gray-200 pb-2">
              {group.label?.fr || group.key}
            </h3>
            <div className="space-y-4">
              {fields.map((field) => renderField(field))}
            </div>
          </div>
        )
      })}
    </div>
  )
}
