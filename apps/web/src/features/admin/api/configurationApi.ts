import { createApi } from '@reduxjs/toolkit/query/react'
import { createBaseQueryWithAuth } from '@/utils/baseQueryWithAuth'
import type { RootState } from '@/store/store'

export interface SystemReference {
  id: string
  category: string
  code: string
  label_fr: string
  label_en?: string
  description?: string
  parent_id?: string
  order: number
  metadata: Record<string, any>
  is_active: boolean
  is_system: boolean
  created_at: string
  updated_at: string
}

export interface ApplicationSetting {
  id: string
  key: string
  value: string
  type: 'string' | 'integer' | 'boolean' | 'json' | 'array'
  category: string
  label: string
  description?: string
  is_public: boolean
  typed_value?: any
}

export const configurationApi = createApi({
  reducerPath: 'configurationApi',
  baseQuery: createBaseQueryWithAuth('/auth/config'),
  tagTypes: ['References', 'Settings'],
  endpoints: (builder) => ({
    // CONFIGURATION GLOBALE
    getAllConfig: builder.query<{
      roles: Record<string, string>
      user_statuses: Record<string, string>
      mission_statuses: string[]
      application_statuses: string[]
      validation_statuses: string[]
      validation_types: string[]
      contract_types: string[]
      permissions: {
        mission: Record<string, string[]>
        application: Record<string, string[]>
        validation: Record<string, string[]>
      }
    }, void>({
      query: () => '/all',
      // Cache pendant 5 minutes
      keepUnusedDataFor: 300,
    }),
    
    // RÉFÉRENTIELS
    getReferences: builder.query<{ references: SystemReference[] }, {
      category?: string
      parent_id?: string
      is_active?: boolean
    }>({
      query: (params) => ({
        url: '/references',
        params,
      }),
      providesTags: ['References'],
    }),
    
    createReference: builder.mutation<{ reference: SystemReference }, Partial<SystemReference>>({
      query: (data) => ({
        url: '/references',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['References'],
    }),
    
    updateReference: builder.mutation<{ reference: SystemReference }, {
      id: string
      data: Partial<SystemReference>
    }>({
      query: ({ id, data }) => ({
        url: `/references/${id}`,
        method: 'PATCH',
        body: data,
      }),
      invalidatesTags: ['References'],
    }),
    
    deleteReference: builder.mutation<void, string>({
      query: (id) => ({
        url: `/references/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['References'],
    }),
    
    // PARAMÈTRES
    getSettings: builder.query<{ settings: ApplicationSetting[] }, {
      category?: string
      is_public?: boolean
    }>({
      query: (params) => ({
        url: '/settings',
        params,
      }),
      providesTags: ['Settings'],
    }),
    
    updateSetting: builder.mutation<{ setting: ApplicationSetting }, {
      key: string
      value: string
    }>({
      query: ({ key, value }) => ({
        url: `/settings/${key}`,
        method: 'PATCH',
        body: { value },
      }),
      invalidatesTags: ['Settings'],
    }),
  }),
})

export const {
  useGetAllConfigQuery,
  useGetReferencesQuery,
  useCreateReferenceMutation,
  useUpdateReferenceMutation,
  useDeleteReferenceMutation,
  useGetSettingsQuery,
  useUpdateSettingMutation,
} = configurationApi
