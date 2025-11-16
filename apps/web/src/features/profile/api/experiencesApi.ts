/**
 * Professional Experiences API
 * RTK Query endpoints for managing professional experiences
 */
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

const API_URL = import.meta.env.VITE_BACKEND_URL || ''

// ==================== Types ====================

export interface ProfessionalExperience {
  id: string
  type: 'internal_jlc' | 'external'
  job_title: string
  company_name: string
  location?: string
  start_date: string // ISO date
  end_date?: string // ISO date
  is_current: boolean
  description?: string
  achievements: string[]
  skills_used: string[]
  mission_id?: string
  contract_id?: string
  created_at: string
  updated_at: string
}

export interface ExperienceCreate {
  type?: 'internal_jlc' | 'external'
  job_title: string
  company_name: string
  location?: string
  start_date: string
  end_date?: string
  is_current?: boolean
  description?: string
  achievements?: string[]
  skills_used?: string[]
  mission_id?: string
  contract_id?: string
}

export interface ExperienceUpdate {
  type?: 'internal_jlc' | 'external'
  job_title?: string
  company_name?: string
  location?: string
  start_date?: string
  end_date?: string
  is_current?: boolean
  description?: string
  achievements?: string[]
  skills_used?: string[]
  mission_id?: string
  contract_id?: string
}

// ==================== API ====================

export const experiencesApi = createApi({
  reducerPath: 'experiencesApi',
  baseQuery: fetchBaseQuery({
    baseUrl: `${API_URL}/api`,
    credentials: 'include',
    prepareHeaders: (headers) => {
      const token = localStorage.getItem('token')
      if (token) {
        headers.set('Authorization', `Bearer ${token}`)
      }
      return headers
    },
  }),
  tagTypes: ['Experience'],
  endpoints: (builder) => ({
    // Get all experiences for current user
    getMyExperiences: builder.query<ProfessionalExperience[], void>({
      query: () => '/profiles/me/experiences',
      providesTags: ['Experience'],
    }),

    // Get a single experience by ID
    getExperience: builder.query<ProfessionalExperience, string>({
      query: (id) => `/profiles/me/experiences/${id}`,
      providesTags: (result, error, id) => [{ type: 'Experience', id }],
    }),

    // Create a new experience
    createExperience: builder.mutation<ProfessionalExperience, ExperienceCreate>({
      query: (data) => ({
        url: '/profiles/me/experiences',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Experience'],
    }),

    // Update an experience
    updateExperience: builder.mutation<
      ProfessionalExperience,
      { id: string; data: ExperienceUpdate }
    >({
      query: ({ id, data }) => ({
        url: `/profiles/me/experiences/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [{ type: 'Experience', id }, 'Experience'],
    }),

    // Delete an experience
    deleteExperience: builder.mutation<void, string>({
      query: (id) => ({
        url: `/profiles/me/experiences/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Experience'],
    }),
  }),
})

export const {
  useGetMyExperiencesQuery,
  useGetExperienceQuery,
  useCreateExperienceMutation,
  useUpdateExperienceMutation,
  useDeleteExperienceMutation,
} = experiencesApi
