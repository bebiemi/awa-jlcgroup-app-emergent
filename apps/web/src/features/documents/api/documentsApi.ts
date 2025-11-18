import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import type { RootState } from '@/store/store'

export interface Document {
  id: string
  user_id: string
  user_email: string
  user_name?: string
  filename: string
  original_filename: string
  file_size: number
  mime_type: string
  category: string
  visibility: string
  description?: string
  tags: string[]
  status: string
  is_confidential: boolean
  verified_by?: string
  verified_at?: string
  retention_period_days?: number
  expiry_date?: string
  created_at: string
  updated_at: string
  download_count: number
}

export interface UpdateDocumentRequest {
  category?: string
  visibility?: string
  description?: string
  tags?: string[]
  status?: string
  is_confidential?: boolean
}

export const documentsApi = createApi({
  reducerPath: 'documentsApi',
  baseQuery: fetchBaseQuery({
    baseUrl: '/api/documents',
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token
      if (token) {
        headers.set('authorization', `Bearer ${token}`)
      }
      return headers
    },
  }),
  tagTypes: ['Documents'],
  endpoints: (builder) => ({
    // Upload document
    uploadDocument: builder.mutation<Document, FormData>({
      query: (formData) => ({
        url: '/upload',
        method: 'POST',
        body: formData,
      }),
      invalidatesTags: ['Documents'],
    }),

    // List documents
    listDocuments: builder.query<Document[], { category?: string; status?: string }>({
      query: (params) => ({
        url: '/',
        params,
      }),
      providesTags: ['Documents'],
    }),

    // Get document
    getDocument: builder.query<Document, string>({
      query: (id) => `/${id}`,
      providesTags: (result, error, id) => [{ type: 'Documents', id }],
    }),

    // Update document
    updateDocument: builder.mutation<Document, { id: string; data: UpdateDocumentRequest }>({
      query: ({ id, data }) => ({
        url: `/${id}`,
        method: 'PATCH',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => ['Documents', { type: 'Documents', id }],
    }),

    // Delete document
    deleteDocument: builder.mutation<void, string>({
      query: (id) => ({
        url: `/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Documents'],
    }),

    // Download document (returns URL)
    getDownloadUrl: builder.query<string, string>({
      query: (id) => `/download/${id}`,
      transformResponse: (response, meta, arg) => `/api/documents/${arg}/download`,
    }),
  }),
})

export const {
  useUploadDocumentMutation,
  useListDocumentsQuery,
  useGetDocumentQuery,
  useUpdateDocumentMutation,
  useDeleteDocumentMutation,
  useGetDownloadUrlQuery,
} = documentsApi
