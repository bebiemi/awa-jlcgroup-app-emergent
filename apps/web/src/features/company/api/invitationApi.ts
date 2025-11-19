import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

const API_URL = import.meta.env.VITE_BACKEND_URL || ''

export interface Invitation {
  id: string
  token: string
  email: string
  entreprise_id: string
  entreprise_name: string
  profile_code: string
  status: 'pending' | 'accepted' | 'expired' | 'cancelled'
  message?: string
  created_at: string
  expires_at: string
  created_by: string
  created_by_name?: string
  accepted_at?: string
  user_id?: string
}

export interface InvitationCreate {
  email: string
  entreprise_id: string
  profile_code?: string
  message?: string
}

export interface BulkInvitationCreate {
  emails: string[]
  entreprise_id: string
  profile_code?: string
  message?: string
}

export interface InvitationValidation {
  email: string
  entreprise_name: string
  entreprise_details: any
  profile_code: string
  expires_at: string
  message?: string
}

export interface InvitationAccept {
  username: string
  full_name: string
  password: string
  phone?: string
}

export const invitationApi = createApi({
  reducerPath: 'invitationApi',
  baseQuery: fetchBaseQuery({
    baseUrl: `${API_URL}/api`,
    prepareHeaders: (headers) => {
      const token = localStorage.getItem('access_token')
      if (token) {
        headers.set('Authorization', `Bearer ${token}`)
      }
      return headers
    },
  }),
  tagTypes: ['Invitations'],
  endpoints: (builder) => ({
    // Créer une invitation
    createInvitation: builder.mutation<Invitation, InvitationCreate>({
      query: (data) => ({
        url: '/invitations/',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Invitations'],
    }),

    // Créer plusieurs invitations
    createBulkInvitations: builder.mutation<Invitation[], BulkInvitationCreate>({
      query: (data) => ({
        url: '/invitations/bulk',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Invitations'],
    }),

    // Lister les invitations
    listInvitations: builder.query<Invitation[], { entreprise_id?: string; status?: string }>({
      query: (params) => ({
        url: '/invitations/',
        params,
      }),
      providesTags: ['Invitations'],
    }),

    // Valider un token d'invitation (public, sans auth)
    validateInvitation: builder.query<InvitationValidation, string>({
      query: (token) => `/invitations/${token}`,
    }),

    // Accepter une invitation (public, sans auth)
    acceptInvitation: builder.mutation<any, { token: string; data: InvitationAccept }>({
      query: ({ token, data }) => ({
        url: `/invitations/${token}/accept`,
        method: 'POST',
        body: data,
      }),
    }),
  }),
})

export const {
  useCreateInvitationMutation,
  useCreateBulkInvitationsMutation,
  useListInvitationsQuery,
  useValidateInvitationQuery,
  useAcceptInvitationMutation,
} = invitationApi
