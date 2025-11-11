import { createApi } from '@reduxjs/toolkit/query/react'
import { baseQueryWithAuth } from '@/utils/baseQueryWithAuth'

export interface InterimProfile {
  user_id: string
  photo_url?: string
  nationality?: string
  social_security_number?: string
  education_level?: string
  years_of_experience?: number
  sectors: string[]
  skills: Array<{ name: string; years_of_experience?: number }>
  languages: Array<{ language: string; level: string }>
  has_driving_license: boolean
  driving_license_types: string[]
  general_availability: Array<{ day_of_week: number; start_time: string; end_time: string }>
  available_immediately: boolean
  available_from_date?: string
  accepted_mission_types: string[]
  blocked_dates: string[]
  cv_document_id?: string
  document_ids: string[]
  profile_completed: boolean
  profile_completion_percentage: number
  updated_at: string
}

export interface CompanyManagerProfile {
  user_id: string
  job_title?: string
  department?: string
  document_ids: string[]
  profile_completed: boolean
  updated_at: string
}

export interface Document {
  id: string
  user_id: string
  type: string
  filename: string
  original_filename: string
  file_size: number
  mime_type: string
  uploaded_at: string
}

export interface ProfileResponse {
  profile_type: 'interim' | 'company' | 'collaborator'
  profile: InterimProfile | CompanyManagerProfile | any
}

export const profileApi = createApi({
  reducerPath: 'profileApi',
  baseQuery: fetchBaseQuery({
    baseUrl: '/auth-api/profiles',
    prepareHeaders: (headers) => {
      const token = localStorage.getItem('access_token')
      if (token) {
        headers.set('Authorization', `Bearer ${token}`)
      }
      return headers
    },
  }),
  tagTypes: ['Profile', 'Documents'],
  endpoints: (builder) => ({
    getMyProfile: builder.query<ProfileResponse, void>({
      query: () => '/me',
      providesTags: ['Profile'],
    }),

    updateMyProfile: builder.mutation<{ success: boolean; message: string; completion_percentage: number }, Partial<InterimProfile | CompanyManagerProfile>>({
      query: (data) => ({
        url: '/me',
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: ['Profile'],
    }),

    uploadDocument: builder.mutation<{ success: boolean; document_id: string; filename: string; file_size: number; message: string }, { file: File; document_type: string }>({
      query: ({ file, document_type }) => {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('document_type', document_type)
        
        return {
          url: '/documents',
          method: 'POST',
          body: formData,
        }
      },
      invalidatesTags: ['Documents', 'Profile'],
    }),

    getMyDocuments: builder.query<{ documents: Document[] }, void>({
      query: () => '/documents',
      providesTags: ['Documents'],
    }),

    deleteDocument: builder.mutation<{ success: boolean; message: string }, string>({
      query: (documentId) => ({
        url: `/documents/${documentId}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Documents', 'Profile'],
    }),
  }),
})

export const {
  useGetMyProfileQuery,
  useUpdateMyProfileMutation,
  useUploadDocumentMutation,
  useGetMyDocumentsQuery,
  useDeleteDocumentMutation,
} = profileApi
