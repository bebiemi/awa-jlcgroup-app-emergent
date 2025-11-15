/**
 * References API
 * Gestion des référentiels système (document_types, skills, etc.)
 */
import { createApi } from '@reduxjs/toolkit/query/react'
import { baseQueryWithAuth } from '@/utils/baseQueryWithAuth'

export interface DocumentType {
  id: string
  category: string
  code: string
  label_fr: string
  label_en: string
  description: string
  order: number
  metadata?: {
    color?: string
    icon?: string
    required_for?: string[]
    max_size_mb?: number
    allowed_formats?: string[]
  }
  is_active: boolean
  is_system: boolean
  created_at: string
  updated_at: string
}

export interface DocumentTypesResponse {
  success: boolean
  data: DocumentType[]
  total: number
}

export const referencesApi = createApi({
  reducerPath: 'referencesApi',
  baseQuery: baseQueryWithAuth,
  tagTypes: ['DocumentTypes', 'References'],
  endpoints: (builder) => ({
    getDocumentTypes: builder.query<DocumentTypesResponse, { requiredOnly?: boolean }>({
      query: ({ requiredOnly = false }) => ({
        url: `/system-references/document-types${requiredOnly ? '?required_only=true' : ''}`,
        method: 'GET',
      }),
      providesTags: ['DocumentTypes'],
    }),
    
    getReferencesByCategory: builder.query<any, string>({
      query: (category) => ({
        url: `/system-references/categories/${category}`,
        method: 'GET',
      }),
      providesTags: (_result, _error, category) => [{ type: 'References' as const, id: category }],
    }),
  }),
})

export const {
  useGetDocumentTypesQuery,
  useGetReferencesByCategoryQuery,
} = referencesApi
