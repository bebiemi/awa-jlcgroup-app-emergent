import { useState, useEffect } from 'react'
import { useUpdateFormFieldMutation, type FieldOption, type FormFieldConfig } from '@/features/company/api/entrepriseFormConfigApi'
import { XMarkIcon, PlusIcon, TrashIcon } from '@heroicons/react/24/outline'
import Button from '@/components/Button'

interface EditFieldModalProps {
  field: FormFieldConfig
  isOpen: boolean
  onClose: () => void
  onSuccess?: () => void
}

export default function EditFieldModal({ field, isOpen, onClose, onSuccess }: EditFieldModalProps) {
  const [updateField, { isLoading }] = useUpdateFormFieldMutation()

  const [formData, setFormData] = useState({
    field_key: field.field_key,
    field_label: field.field_label,
    field_type: field.field_type,
    category: field.category,
    order: field.order,
    placeholder: field.placeholder || '',
    help_text: field.help_text || '',
    default_value: field.default_value || '',
  })

  const [validation, setValidation] = useState({
    required: field.validation.required,
    min_length: field.validation.min_length?.toString() || '',
    max_length: field.validation.max_length?.toString() || '',
    min_value: field.validation.min_value?.toString() || '',
    max_value: field.validation.max_value?.toString() || '',
    pattern: field.validation.pattern || '',
    custom_error_message: field.validation.custom_error_message || '',
  })

  const [visibleRoles, setVisibleRoles] = useState<string[]>(field.visible_for_roles)
  const [editableRoles, setEditableRoles] = useState<string[]>(field.editable_for_roles)
  const [options, setOptions] = useState<FieldOption[]>(field.options || [{ label: '', value: '' }])
  const [errors, setErrors] = useState<Record<string, string>>({})

  // Update state when field prop changes
  useEffect(() => {
    setFormData({
      field_key: field.field_key,
      field_label: field.field_label,
      field_type: field.field_type,
      category: field.category,
      order: field.order,
      placeholder: field.placeholder || '',
      help_text: field.help_text || '',
      default_value: field.default_value || '',
    })
    setValidation({
      required: field.validation.required,
      min_length: field.validation.min_length?.toString() || '',
      max_length: field.validation.max_length?.toString() || '',
      min_value: field.validation.min_value?.toString() || '',
      max_value: field.validation.max_value?.toString() || '',
      pattern: field.validation.pattern || '',
      custom_error_message: field.validation.custom_error_message || '',
    })
    setVisibleRoles(field.visible_for_roles)
    setEditableRoles(field.editable_for_roles)
    setOptions(field.options || [{ label: '', value: '' }])
  }, [field])

  const fieldTypes = [
    { value: 'text', label: 'Texte' },
    { value: 'textarea', label: 'Zone de texte' },
    { value: 'select', label: 'Liste déroulante' },
    { value: 'multiselect', label: 'Liste multiple' },
    { value: 'checkbox', label: 'Case à cocher' },
    { value: 'radio', label: 'Boutons radio' },
    { value: 'date', label: 'Date' },
    { value: 'number', label: 'Nombre' },
    { value: 'email', label: 'Email' },
    { value: 'tel', label: 'Téléphone' },
    { value: 'url', label: 'URL' },
    { value: 'file', label: 'Fichier' },
  ]

  const availableRoles = ['admin', 'company_manager', 'company_user', 'rh', 'commercial']

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target
    const checked = (e.target as HTMLInputElement).checked

    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }))

    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev }
        delete newErrors[name]
        return newErrors
      })
    }
  }

  const handleValidationChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target
    setValidation((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }))
  }

  const handleOptionChange = (index: number, field: 'label' | 'value', value: string) => {
    const newOptions = [...options]
    newOptions[index][field] = value
    setOptions(newOptions)
  }

  const addOption = () => {
    setOptions([...options, { label: '', value: '' }])
  }

  const removeOption = (index: number) => {
    if (options.length > 1) {
      setOptions(options.filter((_, i) => i !== index))
    }
  }

  const toggleRole = (role: string, type: 'visible' | 'editable') => {
    if (type === 'visible') {
      setVisibleRoles((prev) =>
        prev.includes(role) ? prev.filter((r) => r !== role) : [...prev, role]
      )
    } else {
      setEditableRoles((prev) =>
        prev.includes(role) ? prev.filter((r) => r !== role) : [...prev, role]
      )
    }
  }

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.field_key) newErrors.field_key = 'La clé est requise'
    else if (!/^[a-z_]+$/.test(formData.field_key))
      newErrors.field_key = 'La clé doit être en minuscules avec underscores uniquement'

    if (!formData.field_label) newErrors.field_label = 'Le label est requis'

    if (['select', 'multiselect', 'radio'].includes(formData.field_type)) {
      const validOptions = options.filter((o) => o.label && o.value)
      if (validOptions.length === 0) {
        newErrors.options = 'Au moins une option est requise'
      }
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) return

    try {
      // Préparer la validation
      const validationData: any = {
        required: validation.required,
      }

      if (validation.min_length) validationData.min_length = parseInt(validation.min_length)
      if (validation.max_length) validationData.max_length = parseInt(validation.max_length)
      if (validation.min_value) validationData.min_value = parseFloat(validation.min_value)
      if (validation.max_value) validationData.max_value = parseFloat(validation.max_value)
      if (validation.pattern) validationData.pattern = validation.pattern
      if (validation.custom_error_message)
        validationData.custom_error_message = validation.custom_error_message

      // Préparer les options si nécessaire
      const fieldOptions =
        ['select', 'multiselect', 'radio'].includes(formData.field_type)
          ? options.filter((o) => o.label && o.value)
          : undefined

      await updateField({
        id: field.id,
        data: {
          field_label: formData.field_label,
          field_type: formData.field_type,
          category: formData.category,
          order: parseInt(formData.order.toString()) || 0,
          placeholder: formData.placeholder || undefined,
          help_text: formData.help_text || undefined,
          validation: validationData,
          visible_for_roles: visibleRoles,
          editable_for_roles: editableRoles,
          options: fieldOptions,
        },
      }).unwrap()

      onSuccess?.()
    } catch (error: any) {
      console.error('Failed to create field:', error)
      setErrors({ submit: error?.data?.detail || 'Erreur lors de la création' })
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">Modifier le champ</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            disabled={isLoading}
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {errors.submit && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {errors.submit}
            </div>
          )}

          {/* Informations de base */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Informations de base</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Clé du champ <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="field_key"
                  value={formData.field_key}
                  onChange={handleChange}
                  placeholder="mon_champ_perso"
                  className={`w-full px-3 py-2 border rounded-lg ${
                    errors.field_key ? 'border-red-500' : 'border-gray-300'
                  }`}
                  disabled={true}
                />
                {errors.field_key && <p className="text-sm text-red-500 mt-1">{errors.field_key}</p>}
                <p className="text-xs text-gray-500 mt-1">Minuscules et underscores uniquement</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Label <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="field_label"
                  value={formData.field_label}
                  onChange={handleChange}
                  placeholder="Mon Champ Personnalisé"
                  className={`w-full px-3 py-2 border rounded-lg ${
                    errors.field_label ? 'border-red-500' : 'border-gray-300'
                  }`}
                  disabled={isLoading}
                />
                {errors.field_label && <p className="text-sm text-red-500 mt-1">{errors.field_label}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Type de champ</label>
                <select
                  name="field_type"
                  value={formData.field_type}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  disabled={isLoading}
                >
                  {fieldTypes.map((type) => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Catégorie</label>
                <input
                  type="text"
                  name="category"
                  value={formData.category}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  disabled={isLoading}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Ordre</label>
                <input
                  type="number"
                  name="order"
                  value={formData.order}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  disabled={isLoading}
                />
              </div>
            </div>
          </div>

          {/* Options pour select/radio */}
          {['select', 'multiselect', 'radio'].includes(formData.field_type) && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Options</h3>
              {options.map((option, index) => (
                <div key={index} className="flex items-center gap-2 mb-2">
                  <input
                    type="text"
                    value={option.label}
                    onChange={(e) => handleOptionChange(index, 'label', e.target.value)}
                    placeholder="Label"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
                    disabled={isLoading}
                  />
                  <input
                    type="text"
                    value={option.value}
                    onChange={(e) => handleOptionChange(index, 'value', e.target.value)}
                    placeholder="Valeur"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
                    disabled={isLoading}
                  />
                  {options.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeOption(index)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                      disabled={isLoading}
                    >
                      <TrashIcon className="h-5 w-5" />
                    </button>
                  )}
                </div>
              ))}
              <button
                type="button"
                onClick={addOption}
                className="flex items-center gap-2 text-sm text-jlc-purple-600 hover:text-jlc-purple-700 font-medium"
                disabled={isLoading}
              >
                <PlusIcon className="h-4 w-4" />
                Ajouter une option
              </button>
              {errors.options && <p className="text-sm text-red-500 mt-2">{errors.options}</p>}
            </div>
          )}

          {/* Textes d'aide */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Textes d'aide</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Placeholder</label>
                <input
                  type="text"
                  name="placeholder"
                  value={formData.placeholder}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  disabled={isLoading}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Texte d'aide</label>
                <textarea
                  name="help_text"
                  value={formData.help_text}
                  onChange={handleChange}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  disabled={isLoading}
                />
              </div>
            </div>
          </div>

          {/* Validation */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Validation</h3>
            <div className="space-y-3">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="required"
                  checked={validation.required}
                  onChange={handleValidationChange}
                  className="w-4 h-4 text-jlc-purple-600 border-gray-300 rounded"
                  disabled={isLoading}
                />
                <span className="ml-2 text-sm text-gray-700">Champ requis</span>
              </label>

              <div className="grid grid-cols-2 gap-4">
                {['text', 'textarea'].includes(formData.field_type) && (
                  <>
                    <div>
                      <label className="block text-sm text-gray-700 mb-1">Longueur min</label>
                      <input
                        type="number"
                        name="min_length"
                        value={validation.min_length}
                        onChange={handleValidationChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                        disabled={isLoading}
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-700 mb-1">Longueur max</label>
                      <input
                        type="number"
                        name="max_length"
                        value={validation.max_length}
                        onChange={handleValidationChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                        disabled={isLoading}
                      />
                    </div>
                  </>
                )}

                {formData.field_type === 'number' && (
                  <>
                    <div>
                      <label className="block text-sm text-gray-700 mb-1">Valeur min</label>
                      <input
                        type="number"
                        name="min_value"
                        value={validation.min_value}
                        onChange={handleValidationChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                        disabled={isLoading}
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-700 mb-1">Valeur max</label>
                      <input
                        type="number"
                        name="max_value"
                        value={validation.max_value}
                        onChange={handleValidationChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                        disabled={isLoading}
                      />
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Permissions */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Permissions</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Visible pour</label>
                <div className="space-y-2">
                  {availableRoles.map((role) => (
                    <label key={role} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={visibleRoles.includes(role)}
                        onChange={() => toggleRole(role, 'visible')}
                        className="w-4 h-4 text-jlc-purple-600 border-gray-300 rounded"
                        disabled={isLoading}
                      />
                      <span className="ml-2 text-sm text-gray-700">{role}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Éditable par</label>
                <div className="space-y-2">
                  {availableRoles.map((role) => (
                    <label key={role} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={editableRoles.includes(role)}
                        onChange={() => toggleRole(role, 'editable')}
                        className="w-4 h-4 text-jlc-purple-600 border-gray-300 rounded"
                        disabled={isLoading}
                      />
                      <span className="ml-2 text-sm text-gray-700">{role}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <Button type="button" onClick={onClose} variant="secondary" disabled={isLoading}>
              Annuler
            </Button>
            <Button type="submit" variant="primary" disabled={isLoading}>
              {isLoading ? 'Modification...' : 'Enregistrer'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
