/**
 * DynamicFormField Component
 * Renders form fields dynamically based on configuration
 */
import React from 'react'
import type { FormFieldConfig } from '../api/entrepriseFormConfigApi'
import { ExclamationCircleIcon } from '@heroicons/react/24/outline'

interface DynamicFormFieldProps {
  field: FormFieldConfig
  value: any
  onChange: (key: string, value: any) => void
  error?: string
  disabled?: boolean
}

export default function DynamicFormField({
  field,
  value,
  onChange,
  error,
  disabled = false
}: DynamicFormFieldProps) {
  const baseInputClasses = `
    w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-jlc-purple-500
    ${error ? 'border-red-500' : 'border-gray-300'}
    ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}
  `

  const renderField = () => {
    switch (field.field_type) {
      case 'text':
      case 'email':
      case 'tel':
      case 'url':
        return (
          <input
            type={field.field_type}
            id={field.field_key}
            value={value || ''}
            onChange={(e) => onChange(field.field_key, e.target.value)}
            placeholder={field.placeholder}
            disabled={disabled}
            className={baseInputClasses}
            required={field.validation.required}
            minLength={field.validation.min_length}
            maxLength={field.validation.max_length}
            pattern={field.validation.pattern}
          />
        )

      case 'number':
        return (
          <input
            type="number"
            id={field.field_key}
            value={value || ''}
            onChange={(e) => onChange(field.field_key, e.target.value)}
            placeholder={field.placeholder}
            disabled={disabled}
            className={baseInputClasses}
            required={field.validation.required}
            min={field.validation.min_value}
            max={field.validation.max_value}
          />
        )

      case 'textarea':
        return (
          <textarea
            id={field.field_key}
            value={value || ''}
            onChange={(e) => onChange(field.field_key, e.target.value)}
            placeholder={field.placeholder}
            disabled={disabled}
            className={`${baseInputClasses} min-h-[100px]`}
            required={field.validation.required}
            maxLength={field.validation.max_length}
            rows={4}
          />
        )

      case 'select':
        return (
          <select
            id={field.field_key}
            value={value || ''}
            onChange={(e) => onChange(field.field_key, e.target.value)}
            disabled={disabled}
            className={baseInputClasses}
            required={field.validation.required}
          >
            <option value="">{field.placeholder || 'Sélectionner...'}</option>
            {field.options?.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        )

      case 'checkbox':
        return (
          <div className="flex items-center">
            <input
              type="checkbox"
              id={field.field_key}
              checked={value || false}
              onChange={(e) => onChange(field.field_key, e.target.checked)}
              disabled={disabled}
              className="h-4 w-4 text-jlc-purple-600 focus:ring-jlc-purple-500 border-gray-300 rounded"
              required={field.validation.required}
            />
            <label htmlFor={field.field_key} className="ml-2 text-sm text-gray-700">
              {field.placeholder || field.field_label}
            </label>
          </div>
        )

      case 'radio':
        return (
          <div className="space-y-2">
            {field.options?.map((option) => (
              <div key={option.value} className="flex items-center">
                <input
                  type="radio"
                  id={`${field.field_key}_${option.value}`}
                  name={field.field_key}
                  value={option.value}
                  checked={value === option.value}
                  onChange={(e) => onChange(field.field_key, e.target.value)}
                  disabled={disabled}
                  className="h-4 w-4 text-jlc-purple-600 focus:ring-jlc-purple-500 border-gray-300"
                  required={field.validation.required}
                />
                <label htmlFor={`${field.field_key}_${option.value}`} className="ml-2 text-sm text-gray-700">
                  {option.label}
                </label>
              </div>
            ))}
          </div>
        )

      case 'date':
        return (
          <input
            type="date"
            id={field.field_key}
            value={value || ''}
            onChange={(e) => onChange(field.field_key, e.target.value)}
            disabled={disabled}
            className={baseInputClasses}
            required={field.validation.required}
          />
        )

      default:
        return (
          <input
            type="text"
            id={field.field_key}
            value={value || ''}
            onChange={(e) => onChange(field.field_key, e.target.value)}
            placeholder={field.placeholder}
            disabled={disabled}
            className={baseInputClasses}
            required={field.validation.required}
          />
        )
    }
  }

  return (
    <div>
      <label htmlFor={field.field_key} className="block text-sm font-medium text-gray-700 mb-1">
        {field.field_label}
        {field.validation.required && <span className="text-red-500 ml-1">*</span>}
      </label>
      
      {renderField()}

      {field.help_text && !error && (
        <p className="mt-1 text-xs text-gray-500">{field.help_text}</p>
      )}

      {error && (
        <div className="mt-1 flex items-center text-sm text-red-600">
          <ExclamationCircleIcon className="h-4 w-4 mr-1" />
          <span>{error}</span>
        </div>
      )}
    </div>
  )
}
