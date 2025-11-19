import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

const API_URL = import.meta.env.VITE_BACKEND_URL || ''

export interface FieldOption {
  label: string
  value: string
}

export interface FieldValidation {
  required: boolean
  min_length?: number
  max_length?: number
  min_value?: number
  max_value?: number
  pattern?: string
  custom_error_message?: string
}

export interface FormFieldConfig {
  id: string
  field_key: string
  field_label: string
  field_type: 'text' | 'textarea' | 'select' | 'multiselect' | 'checkbox' | 'radio' | 'date' | 'number' | 'email' | 'tel' | 'url' | 'file'
  category: string
  order: number
  placeholder?: string
  help_text?: string
  default_value?: any
  options?: FieldOption[]
  validation: FieldValidation
  visible_for_roles: string[]
  editable_for_roles: string[]
  is_active: boolean
  is_system: boolean
  created_at: string
  updated_at: string
  created_by: string
}

export interface FormFieldCreate {
  field_key: string
  field_label: string
  field_type: string
  category?: string
  order?: number
  placeholder?: string
  help_text?: string
  default_value?: any
  options?: FieldOption[]
  validation?: FieldValidation
  visible_for_roles?: string[]
  editable_for_roles?: string[]
  is_active?: boolean
}

export interface FormFieldUpdate {
  field_label?: string
  field_type?: string
  category?: string
  order?: number
  placeholder?: string
  help_text?: string
  default_value?: any
  options?: FieldOption[]
  validation?: FieldValidation
  visible_for_roles?: string[]
  editable_for_roles?: string[]
  is_active?: boolean
}

export interface FormConfigResponse {
  fields: FormFieldConfig[]
  categories: string[]
  total_fields: number
}

export const entrepriseFormConfigApi = createApi({
  reducerPath: 'entrepriseFormConfigApi',
  baseQuery: fetchBaseQuery({
    baseUrl: `${API_URL}/api/entreprises/form-config`,
    prepareHeaders: (headers) => {
      const token = localStorage.getItem('access_token')
      if (token) {
        headers.set('Authorization', `Bearer ${token}`)
      }
      return headers
    },
  }),
  tagTypes: ['FormFields'],
  endpoints: (builder) => ({
    // Liste des champs
    getFormFields: builder.query<FormConfigResponse, { category?: string; is_active?: boolean }>({
      query: (params) => ({
        url: '/fields',
        params,
      }),
      providesTags: ['FormFields'],
    }),

    // Détail d'un champ
    getFormField: builder.query<FormFieldConfig, string>({
      query: (id) => `/fields/${id}`,
      providesTags: (_result, _error, id) => [{ type: 'FormFields', id }],
    }),

    // Créer un champ
    createFormField: builder.mutation<FormFieldConfig, FormFieldCreate>({
      query: (data) => ({
        url: '/fields',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['FormFields'],
    }),

    // Mettre à jour un champ
    updateFormField: builder.mutation<FormFieldConfig, { id: string; data: FormFieldUpdate }>({
      query: ({ id, data }) => ({
        url: `/fields/${id}`,
        method: 'PATCH',
        body: data,
      }),
      invalidatesTags: (_result, _error, { id }) => [{ type: 'FormFields', id }, 'FormFields'],
    }),

    // Supprimer un champ
    deleteFormField: builder.mutation<void, string>({
      query: (id) => ({
        url: `/fields/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['FormFields'],
    }),

    // Réorganiser les champs
    reorderFormFields: builder.mutation<any, Array<{ id: string; order: number }>>({
      query: (fieldOrders) => ({
        url: '/fields/reorder',
        method: 'POST',
        body: fieldOrders,
      }),
      invalidatesTags: ['FormFields'],
    }),

    // Champs pour un rôle spécifique
    getFieldsForRole: builder.query<{ fields: FormFieldConfig[]; total: number }, string>({
      query: (role) => `/fields/for-role/${role}`,
    }),
    
    // Champs publics pour l'inscription (sans authentification)
    getPublicFormFields: builder.query<FormConfigResponse, void>({
      query: () => '/fields/public',
    }),
  }),
})

export const {
  useGetFormFieldsQuery,
  useGetFormFieldQuery,
  useCreateFormFieldMutation,
  useUpdateFormFieldMutation,
  useDeleteFormFieldMutation,
  useReorderFormFieldsMutation,
  useGetFieldsForRoleQuery,
  useGetPublicFormFieldsQuery,
} = entrepriseFormConfigApi
