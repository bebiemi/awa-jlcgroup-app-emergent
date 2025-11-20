import { createApi } from '@reduxjs/toolkit/query/react'
import { baseQueryWithAuth } from '@/utils/baseQueryWithAuth'

// Types
export interface FormField {
  key: string
  type: string
  label: Record<string, string>
  placeholder?: Record<string, string>
  help_text?: Record<string, string>
  required: boolean
  default_value?: any
  validations: ValidationRule[]
  options: FieldOption[]
  depends_on?: string
  depends_condition?: Record<string, any>
  order: number
  group?: string
  active: boolean
}

export interface ValidationRule {
  type: string
  value?: string | number | boolean
  message: string
}

export interface FieldOption {
  value: string
  label: Record<string, string>
  description?: Record<string, string>
  active: boolean
}

export interface FormSchema {
  id: string
  form_type: string
  version: string
  fields: FormField[]
  groups?: any[]
  metadata: Record<string, any>
  created_at: string
  updated_at: string
}

export interface StatusConfig {
  key: string
  label: Record<string, string>
  description?: Record<string, string>
  color: string
  icon?: string
  allowed_transitions: string[]
  permissions_required: string[]
  notifications: string[]
  order: number
  is_terminal: boolean
  active: boolean
}

export interface WorkflowConfig {
  id: string
  entity_type: string
  version: string
  statuses: StatusConfig[]
  initial_status: string
  metadata: Record<string, any>
  created_at: string
  updated_at: string
}

export interface ReferenceDataItem {
  key: string
  label: Record<string, string>
  description?: Record<string, string>
  metadata: Record<string, any>
  order: number
  active: boolean
  parent_key?: string
}

export interface ReferenceData {
  id: string
  reference_type: string
  version: string
  items: ReferenceDataItem[]
  metadata: Record<string, any>
  created_at: string
  updated_at: string
}

export const configApi = createApi({
  reducerPath: 'configApi',
  baseQuery: baseQueryWithAuth,
  tagTypes: ['FormSchema', 'WorkflowConfig', 'ReferenceData'],
  endpoints: (builder) => ({
    // Form schemas
    getFormSchema: builder.query<FormSchema, string>({
      query: (formType) => `/config/forms/${formType}`,
      providesTags: (result, error, formType) => [{ type: 'FormSchema', id: formType }],
    }),

    // Workflow configs
    getWorkflowConfig: builder.query<WorkflowConfig, string>({
      query: (entityType) => `/config/workflows/${entityType}`,
      providesTags: (result, error, entityType) => [{ type: 'WorkflowConfig', id: entityType }],
    }),

    // Reference data
    getReferenceData: builder.query<ReferenceData, string>({
      query: (referenceType) => `/config/references/${referenceType}`,
      providesTags: (result, error, referenceType) => [{ type: 'ReferenceData', id: referenceType }],
    }),
  }),
})

export const {
  useGetFormSchemaQuery,
  useGetWorkflowConfigQuery,
  useGetReferenceDataQuery,
} = configApi
