import { createApi } from '@reduxjs/toolkit/query/react'
import { baseQueryWithAuth } from '@/utils/baseQueryWithAuth'

// Types
export interface RetentionConfig {
  retention_days: number
  source: 'yaml' | 'database'
  can_override: boolean
}

export interface RetentionConfigUpdate {
  retention_days: number
}

export const securityConfigApi = createApi({
  reducerPath: 'securityConfigApi',
  baseQuery: baseQueryWithAuth,
  tagTypes: ['RetentionConfig'],
  endpoints: (builder) => ({
    // Get retention configuration
    getRetentionConfig: builder.query<RetentionConfig, void>({
      query: () => '/iam/users/config/retention',
      providesTags: ['RetentionConfig'],
    }),

    // Update retention configuration
    updateRetentionConfig: builder.mutation<{ message: string; retention_days: number }, number>({
      query: (retention_days) => ({
        url: '/iam/users/config/retention',
        method: 'PUT',
        params: { retention_days },
      }),
      invalidatesTags: ['RetentionConfig'],
    }),
  }),
})

export const {
  useGetRetentionConfigQuery,
  useUpdateRetentionConfigMutation,
} = securityConfigApi
