import { createApi } from '@reduxjs/toolkit/query/react'
import { createBaseQueryWithAuth } from '@/utils/baseQueryWithAuth'

const baseUrl = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8000'

export interface AllowedEmailDomain {
  id: string
  domain: string
  country_code?: string
  is_active: boolean
  created_at: string
  created_by?: string
  updated_at?: string
  metadata?: Record<string, any>
}

export interface AllowedEmailDomainCreate {
  domain: string
  country_code?: string
  is_active?: boolean
  metadata?: Record<string, any>
}

export interface AllowedEmailDomainUpdate {
  country_code?: string
  is_active?: boolean
  metadata?: Record<string, any>
}

export interface EmailDomainVerification {
  email: string
  is_valid: boolean
  domain: string
  is_collaborator: boolean
  message: string
}

export const emailDomainsApi = createApi({
  reducerPath: 'emailDomainsApi',
  baseQuery: createBaseQueryWithAuth(baseUrl),
  tagTypes: ['EmailDomains'],
  endpoints: (builder) => ({
    listEmailDomains: builder.query<AllowedEmailDomain[], boolean | undefined>({
      query: (activeOnly) => ({
        url: '/api/security/email-domains',
        params: activeOnly ? { active_only: true } : {},
      }),
      providesTags: ['EmailDomains'],
    }),

    getEmailDomain: builder.query<AllowedEmailDomain, string>({
      query: (id) => `/api/security/email-domains/${id}`,
      providesTags: ['EmailDomains'],
    }),

    verifyEmailDomain: builder.query<EmailDomainVerification, string>({
      query: (email) => ({
        url: '/api/security/email-domains/verify',
        params: { email },
      }),
    }),

    getActiveDomainsList: builder.query<string[], void>({
      query: () => '/api/security/email-domains/active/list',
    }),

    createEmailDomain: builder.mutation<AllowedEmailDomain, AllowedEmailDomainCreate>({
      query: (data) => ({
        url: '/api/security/email-domains',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['EmailDomains'],
    }),

    updateEmailDomain: builder.mutation<AllowedEmailDomain, { id: string; data: AllowedEmailDomainUpdate }>({
      query: ({ id, data }) => ({
        url: `/api/security/email-domains/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: ['EmailDomains'],
    }),

    deleteEmailDomain: builder.mutation<void, string>({
      query: (id) => ({
        url: `/api/security/email-domains/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['EmailDomains'],
    }),
  }),
})

export const {
  useListEmailDomainsQuery,
  useGetEmailDomainQuery,
  useVerifyEmailDomainQuery,
  useLazyVerifyEmailDomainQuery,
  useGetActiveDomainsListQuery,
  useCreateEmailDomainMutation,
  useUpdateEmailDomainMutation,
  useDeleteEmailDomainMutation,
} = emailDomainsApi
