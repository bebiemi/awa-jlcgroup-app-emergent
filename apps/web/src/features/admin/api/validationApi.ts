import { createApi } from '@reduxjs/toolkit/query/react'
import { baseQueryWithAuth } from '@/utils/baseQueryWithAuth'
import type { RootState } from '@/store/store'

export interface Validation {
  id: string
  user_id: string
  user_email: string
  user_full_name: string
  validation_type: string
  status: 'pending' | 'approved' | 'rejected'
  country_name?: string
  province_name?: string
  city_name?: string
  district_name?: string
  neighborhood_name?: string
  has_location_warning: boolean
  location_warning_message?: string
  missing_country?: string
  assigned_to?: string
  validated_by?: string
  validated_at?: string
  rejection_reason?: string
  notes?: string
  // Collaborator-specific fields
  employee_number?: string
  department?: string
  job_title?: string
  created_at: string
  updated_at: string
}

export interface ValidationStats {
  total_pending: number
  pending_interim: number
  pending_company: number
  pending_collaborator: number
  with_location_warnings: number
  total_approved: number
  total_rejected: number
}

export const validationApi = createApi({
  reducerPath: 'validationApi',
  baseQuery: baseQueryWithAuth,
  tagTypes: ['Validation', 'ValidationStats'],
  endpoints: (builder) => ({
    getValidations: builder.query<Validation[], { 
      validation_type?: string
      status?: string
      has_location_warning?: boolean
      assigned_to?: string
      page?: number
      page_size?: number 
    }>({
      query: (params) => {
        const searchParams = new URLSearchParams()
        if (params.validation_type) searchParams.append('validation_type', params.validation_type)
        if (params.status) searchParams.append('status', params.status)
        if (params.has_location_warning !== undefined) searchParams.append('has_location_warning', String(params.has_location_warning))
        if (params.assigned_to) searchParams.append('assigned_to', params.assigned_to)
        if (params.page) searchParams.append('page', String(params.page))
        if (params.page_size) searchParams.append('page_size', String(params.page_size))
        return `/validations?${searchParams.toString()}`
      },
      providesTags: ['Validation'],
    }),
    
    getValidationStats: builder.query<ValidationStats, void>({
      query: () => '/validations/stats',
      providesTags: ['ValidationStats'],
    }),
    
    getValidation: builder.query<Validation, string>({
      query: (id) => `/validations/${id}`,
      providesTags: ['Validation'],
    }),
    
    getMyValidation: builder.query<Validation | null, void>({
      query: () => '/validations/my-validation',
      providesTags: ['Validation'],
    }),
    
    approveValidation: builder.mutation<{ success: boolean; message: string }, { id: string; notes?: string }>({
      query: ({ id, notes }) => ({
        url: `/validations/${id}/approve`,
        method: 'POST',
        body: { notes },
      }),
      invalidatesTags: ['Validation', 'ValidationStats'],
    }),
    
    rejectValidation: builder.mutation<{ success: boolean; message: string }, { id: string; rejection_reason: string; notes?: string }>({
      query: ({ id, rejection_reason, notes }) => ({
        url: `/validations/${id}/reject`,
        method: 'POST',
        body: { rejection_reason, notes },
      }),
      invalidatesTags: ['Validation', 'ValidationStats'],
    }),
    
    assignValidation: builder.mutation<{ success: boolean; message: string }, { id: string; assigned_to: string }>({
      query: ({ id, assigned_to }) => ({
        url: `/validations/${id}/assign`,
        method: 'POST',
        body: { assigned_to },
      }),
      invalidatesTags: ['Validation'],
    }),
    
    addCountryFromValidation: builder.mutation<{ success: boolean; message: string; country_id: string }, string>({
      query: (id) => ({
        url: `/validations/${id}/add-country`,
        method: 'POST',
      }),
      invalidatesTags: ['Validation'],
    }),
  }),
})

export const {
  useGetValidationsQuery,
  useGetValidationStatsQuery,
  useGetValidationQuery,
  useGetMyValidationQuery,
  useApproveValidationMutation,
  useRejectValidationMutation,
  useAssignValidationMutation,
  useAddCountryFromValidationMutation,
} = validationApi
