/**
 * API pour la gestion des politiques de rétention
 */
import { createApi } from '@reduxjs/toolkit/query/react'
import { baseQueryWithAuth } from '@/utils/baseQueryWithAuth'

export interface WorkflowStage {
  stage_name: string
  days_before_deletion: number
  action: string
  notification_recipients: string[]
  status_transition: string | null
  description: string
}

export interface RetentionPolicy {
  id: string
  entity_type: string
  entity_label: string
  retention_days: number
  is_enabled: boolean
  status: string
  workflow_stages_count: number
  created_at: string
  updated_at: string
  description?: string
}

export interface RetentionPolicyDetail {
  id: string
  entity_type: string
  entity_label: string
  retention_days: number
  is_enabled: boolean
  status: string
  workflow_stages: WorkflowStage[]
  auto_archive: boolean
  soft_delete: boolean
  keep_audit_trail: boolean
  description?: string
  legal_basis?: string
  notes?: string
  created_at: string
  updated_at: string
  created_by: string
  updated_by: string
}

export interface RetentionPoliciesListResponse {
  policies: RetentionPolicy[]
  total: number
}

export interface RetentionStatsResponse {
  total_policies: number
  active_policies: number
  inactive_policies: number
  total_entities_in_retention: {
    [key: string]: number
  }
  policies_by_entity: {
    [key: string]: {
      retention_days: number
      is_enabled: boolean
      workflow_stages: number
    }
  }
}

export interface CreateRetentionPolicyRequest {
  entity_type: string
  entity_label: string
  retention_days: number
  workflow_stages?: WorkflowStage[]
  description?: string
  legal_basis?: string
  auto_archive?: boolean
  soft_delete?: boolean
  keep_audit_trail?: boolean
}

export interface UpdateRetentionPolicyRequest {
  entity_label?: string
  retention_days?: number
  is_enabled?: boolean
  workflow_stages?: WorkflowStage[]
  description?: string
  legal_basis?: string
  auto_archive?: boolean
  soft_delete?: boolean
  keep_audit_trail?: boolean
}

export const retentionPoliciesApi = createApi({
  reducerPath: 'retentionPoliciesApi',
  baseQuery: baseQueryWithAuth,
  tagTypes: ['RetentionPolicies', 'RetentionStats'],
  endpoints: (builder) => ({
    getRetentionPolicies: builder.query<RetentionPoliciesListResponse, { entity_type?: string; enabled_only?: boolean }>({
      query: ({ entity_type, enabled_only }) => {
        const params = new URLSearchParams()
        if (entity_type) params.append('entity_type', entity_type)
        if (enabled_only) params.append('enabled_only', 'true')
        
        return {
          url: `/retention-policies${params.toString() ? `?${params.toString()}` : ''}`,
          method: 'GET',
        }
      },
      providesTags: ['RetentionPolicies'],
    }),

    getRetentionStats: builder.query<RetentionStatsResponse, void>({
      query: () => ({
        url: '/retention-policies/stats',
        method: 'GET',
      }),
      providesTags: ['RetentionStats'],
    }),

    getRetentionPolicy: builder.query<RetentionPolicyDetail, string>({
      query: (policyId) => ({
        url: `/retention-policies/${policyId}`,
        method: 'GET',
      }),
      providesTags: (_result, _error, policyId) => [{ type: 'RetentionPolicies' as const, id: policyId }],
    }),

    createRetentionPolicy: builder.mutation<RetentionPolicy, CreateRetentionPolicyRequest>({
      query: (body) => ({
        url: '/retention-policies',
        method: 'POST',
        body,
      }),
      invalidatesTags: ['RetentionPolicies', 'RetentionStats'],
    }),

    updateRetentionPolicy: builder.mutation<RetentionPolicy, { policyId: string; data: UpdateRetentionPolicyRequest }>({
      query: ({ policyId, data }) => ({
        url: `/retention-policies/${policyId}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: (_result, _error, { policyId }) => [
        { type: 'RetentionPolicies' as const, id: policyId },
        'RetentionPolicies',
        'RetentionStats',
      ],
    }),

    deleteRetentionPolicy: builder.mutation<{ message: string; policy_id: string }, string>({
      query: (policyId) => ({
        url: `/retention-policies/${policyId}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['RetentionPolicies', 'RetentionStats'],
    }),

    initializeDefaultPolicies: builder.mutation<{ message: string; created_count: number }, void>({
      query: () => ({
        url: '/retention-policies/initialize-defaults',
        method: 'POST',
      }),
      invalidatesTags: ['RetentionPolicies', 'RetentionStats'],
    }),
  }),
})

export const {
  useGetRetentionPoliciesQuery,
  useGetRetentionStatsQuery,
  useGetRetentionPolicyQuery,
  useCreateRetentionPolicyMutation,
  useUpdateRetentionPolicyMutation,
  useDeleteRetentionPolicyMutation,
  useInitializeDefaultPoliciesMutation,
} = retentionPoliciesApi
