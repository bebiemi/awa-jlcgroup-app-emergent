import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import type { RootState } from '@/store/store'

export interface FeatureFlag {
  id: string
  key: string
  type: 'GLOBAL' | 'ROLE' | 'USER' | 'ENV'
  value: boolean
  target: string | null
  metadata: {
    description?: string
    rollout_percentage: number
    created_by_name?: string
    tags: string[]
    dependencies: string[]
  }
  created_by: string
  created_at: string
  updated_at: string
}

export interface CreateFeatureFlagRequest {
  key: string
  type: 'GLOBAL' | 'ROLE' | 'USER' | 'ENV'
  value?: boolean
  target?: string | null
  metadata?: {
    description?: string
    rollout_percentage?: number
    tags?: string[]
    dependencies?: string[]
  }
}

export interface UpdateFeatureFlagRequest {
  value?: boolean
  target?: string | null
  metadata?: {
    description?: string
    rollout_percentage?: number
    tags?: string[]
    dependencies?: string[]
  }
}

export interface RolloutRequest {
  rollout_percentage: number
  description?: string
}

export interface AuditEvent {
  id: string
  actor_id: string
  actor_name: string | null
  action: string
  target_type: string
  target_id: string | null
  payload: Record<string, any>
  created_at: string
}

export const featureFlagApi = createApi({
  reducerPath: 'featureFlagApi',
  baseQuery: fetchBaseQuery({
    baseUrl: '/api',
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token
      if (token) {
        headers.set('authorization', `Bearer ${token}`)
      }
      return headers
    },
  }),
  tagTypes: ['FeatureFlag', 'AuditEvent'],
  endpoints: (builder) => ({
    // Vérifier si un flag est activé pour l'utilisateur actuel
    checkFeatureFlag: builder.query<{ flag_key: string; enabled: boolean }, string>({
      query: (flagKey) => `/feature-flags/check/${flagKey}`,
    }),

    // Lister tous les flags
    listFeatureFlags: builder.query<
      { flags: FeatureFlag[]; total: number; can_create: boolean },
      { include_inactive?: boolean; type_filter?: string }
    >({
      query: ({ include_inactive, type_filter }) => {
        const params = new URLSearchParams()
        if (include_inactive) params.append('include_inactive', 'true')
        if (type_filter) params.append('type_filter', type_filter)
        return `/feature-flags?${params.toString()}`
      },
      providesTags: ['FeatureFlag'],
    }),

    // Créer un flag
    createFeatureFlag: builder.mutation<
      { message: string; flag: FeatureFlag },
      CreateFeatureFlagRequest
    >({
      query: (body) => ({
        url: '/feature-flags',
        method: 'POST',
        body,
      }),
      invalidatesTags: ['FeatureFlag'],
    }),

    // Mettre à jour un flag
    updateFeatureFlag: builder.mutation<
      { message: string; flag: FeatureFlag },
      { id: string; data: UpdateFeatureFlagRequest }
    >({
      query: ({ id, data }) => ({
        url: `/feature-flags/${id}`,
        method: 'PATCH',
        body: data,
      }),
      invalidatesTags: ['FeatureFlag', 'AuditEvent'],
    }),

    // Supprimer un flag
    deleteFeatureFlag: builder.mutation<{ message: string }, string>({
      query: (id) => ({
        url: `/feature-flags/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['FeatureFlag'],
    }),

    // Appliquer un rollout
    applyRollout: builder.mutation<
      { message: string; flag: FeatureFlag },
      { id: string; data: RolloutRequest }
    >({
      query: ({ id, data }) => ({
        url: `/feature-flags/${id}/rollout`,
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['FeatureFlag', 'AuditEvent'],
    }),

    // Historique d'un flag
    getFlagHistory: builder.query<
      { flag_id: string; events: AuditEvent[]; total: number },
      { id: string; limit?: number }
    >({
      query: ({ id, limit = 50 }) => `/feature-flags/${id}/history?limit=${limit}`,
      providesTags: ['AuditEvent'],
    }),

    // Tous les événements d'audit
    getAllAuditEvents: builder.query<
      { events: AuditEvent[]; total: number; filtered_by: string | null },
      { limit?: number; target_type?: string }
    >({
      query: ({ limit = 50, target_type }) => {
        const params = new URLSearchParams({ limit: limit.toString() })
        if (target_type) params.append('target_type', target_type)
        return `/feature-flags/audit/all?${params.toString()}`
      },
      providesTags: ['AuditEvent'],
    }),
  }),
})

export const {
  useCheckFeatureFlagQuery,
  useListFeatureFlagsQuery,
  useCreateFeatureFlagMutation,
  useUpdateFeatureFlagMutation,
  useDeleteFeatureFlagMutation,
  useApplyRolloutMutation,
  useGetFlagHistoryQuery,
  useGetAllAuditEventsQuery,
} = featureFlagApi
