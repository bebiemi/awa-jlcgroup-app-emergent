import { createApi } from '@reduxjs/toolkit/query/react'
import { baseQueryWithAuth } from '@/utils/baseQueryWithAuth'

// Types
export interface Besoin {
  id: string
  entreprise_id: string
  entreprise_name: string
  titre: string
  description: string
  duree: 'indeterminee' | 'periode_precise'
  date_debut_souhaitee?: string
  date_fin_souhaitee?: string
  type_poste: string
  competences_attendues: string[]
  responsable_besoin_id: string
  responsable_besoin_name?: string
  pieces_jointes: string[]
  custom_fields: Record<string, any>
  status: string
  status_history: StatusHistoryEntry[]
  jlc_analysis?: JLCAnalysis
  mission_ids: string[]
  created_by: string
  created_by_name: string
  created_at: string
  updated_at?: string
  submitted_at?: string
  closed_at?: string
  comments_count: number
}

export interface StatusHistoryEntry {
  from_status?: string
  to_status: string
  changed_by: string
  changed_by_name: string
  changed_at: string
  comment?: string
}

export interface JLCAnalysis {
  observations?: string
  estimated_budget?: number
  estimated_duration_days?: number
  assigned_to_jlc_user_id?: string
  priority?: string
  tags: string[]
}

export interface BesoinCreate {
  titre: string
  description: string
  duree: 'indeterminee' | 'periode_precise'
  date_debut_souhaitee?: string
  date_fin_souhaitee?: string
  type_poste: string
  competences_attendues: string[]
  responsable_besoin_id?: string
  pieces_jointes?: string[]
  custom_fields?: Record<string, any>
}

export interface BesoinUpdate {
  titre?: string
  description?: string
  duree?: 'indeterminee' | 'periode_precise'
  date_debut_souhaitee?: string
  date_fin_souhaitee?: string
  type_poste?: string
  competences_attendues?: string[]
  responsable_besoin_id?: string
  pieces_jointes?: string[]
  custom_fields?: Record<string, any>
}

export interface Comment {
  id: string
  besoin_id: string
  author_type: 'entreprise' | 'jlc'
  author_id: string
  author_name: string
  content: string
  created_at: string
  updated_at?: string
}

export interface CommentCreate {
  content: string
}

export interface BesoinListResponse {
  items: Besoin[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export const besoinApi = createApi({
  reducerPath: 'besoinApi',
  baseQuery: baseQueryWithAuth,
  tagTypes: ['Besoins', 'Besoin', 'Comments'],
  endpoints: (builder) => ({
    // List besoins
    getBesoins: builder.query<BesoinListResponse, { status?: string; page?: number; page_size?: number; search?: string }>({
      query: ({ status, page = 1, page_size = 20, search }) => ({
        url: '/besoins',
        params: { status_filter: status, page, page_size, search },
      }),
      providesTags: ['Besoins'],
    }),

    // Get single besoin
    getBesoin: builder.query<Besoin, string>({
      query: (id) => `/api/besoins/${id}`,
      providesTags: (result, error, id) => [{ type: 'Besoin', id }],
    }),

    // Create besoin
    createBesoin: builder.mutation<Besoin, BesoinCreate>({
      query: (data) => ({
        url: '/besoins',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Besoins'],
    }),

    // Update besoin
    updateBesoin: builder.mutation<Besoin, { id: string; data: BesoinUpdate }>({
      query: ({ id, data }) => ({
        url: `/api/besoins/${id}`,
        method: 'PATCH',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [{ type: 'Besoin', id }, 'Besoins'],
    }),

    // Submit besoin
    submitBesoin: builder.mutation<Besoin, string>({
      query: (id) => ({
        url: `/api/besoins/${id}/submit`,
        method: 'POST',
      }),
      invalidatesTags: (result, error, id) => [{ type: 'Besoin', id }, 'Besoins'],
    }),

    // Get comments
    getComments: builder.query<Comment[], string>({
      query: (besoinId) => `/api/besoins/${besoinId}/comments`,
      providesTags: (result, error, besoinId) => [{ type: 'Comments', id: besoinId }],
    }),

    // Add comment
    addComment: builder.mutation<Comment, { besoinId: string; data: CommentCreate }>({
      query: ({ besoinId, data }) => ({
        url: `/api/besoins/${besoinId}/comments`,
        method: 'POST',
        body: data,
      }),
      invalidatesTags: (result, error, { besoinId }) => [
        { type: 'Comments', id: besoinId },
        { type: 'Besoin', id: besoinId },
      ],
    }),

    // Get audit trail
    getAuditTrail: builder.query<any, { besoinId: string; page?: number }>({
      query: ({ besoinId, page = 1 }) => ({
        url: `/api/besoins/${besoinId}/audit`,
        params: { page },
      }),
    }),

    // Validate besoin (for admin/commercial)
    validateBesoin: builder.mutation<Besoin, { id: string; approved: boolean; comment?: string }>({
      query: ({ id, approved, comment }) => ({
        url: `/api/besoins/${id}/validate`,
        method: 'POST',
        body: { approved, comment },
      }),
      invalidatesTags: (result, error, { id }) => [{ type: 'Besoin', id }, 'Besoins'],
    }),

    // Delete besoin
    deleteBesoin: builder.mutation<void, string>({
      query: (id) => ({
        url: `/api/besoins/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Besoins'],
    }),
  }),
})

export const {
  useGetBesoinsQuery,
  useGetBesoinQuery,
  useCreateBesoinMutation,
  useUpdateBesoinMutation,
  useSubmitBesoinMutation,
  useGetCommentsQuery,
  useAddCommentMutation,
  useGetAuditTrailQuery,
  useValidateBesoinMutation,
  useDeleteBesoinMutation,
} = besoinApi

// Aliases pour la config
export const useListBesoinsQuery = useGetBesoinsQuery
