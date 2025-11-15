/**
 * Missions API
 * Gestion des missions d'intérim
 */
import { createApi } from '@reduxjs/toolkit/query/react'
import { baseQueryWithAuth } from '@/utils/baseQueryWithAuth'

export interface Mission {
  id: string
  title: string
  description: string
  company_id: string
  job_type: string
  required_skills: string[]
  experience_required: string
  education_level: string
  start_date: string | null
  end_date: string | null
  duration: string
  location: string
  location_details: string | null
  salary_range: string
  contract_type: string
  working_hours: string
  benefits: string[]
  max_applications: number | null
  application_deadline: string | null
  requires_medical_check: boolean
  custom_fields: any | null
  status: string
  created_by: string
  commercial_id: string | null
  applications_count: number
  shortlisted_count: number
  selected_count: number
  hired_count: number
  published_at: string | null
  closed_at: string | null
  completed_at: string | null
  created_at: string
  updated_at: string
}

export interface MissionsQueryParams {
  status?: string
  company_id?: string
  commercial_id?: string
  published_only?: boolean
  skip?: number
  limit?: number
}

export const missionsApi = createApi({
  reducerPath: 'missionsApi',
  baseQuery: baseQueryWithAuth,
  tagTypes: ['Missions'],
  endpoints: (builder) => ({
    getMissions: builder.query<Mission[], MissionsQueryParams>({
      query: (params) => {
        const queryString = new URLSearchParams()
        if (params.status) queryString.append('status', params.status)
        if (params.company_id) queryString.append('company_id', params.company_id)
        if (params.commercial_id) queryString.append('commercial_id', params.commercial_id)
        if (params.published_only !== undefined) queryString.append('published_only', String(params.published_only))
        if (params.skip !== undefined) queryString.append('skip', String(params.skip))
        if (params.limit !== undefined) queryString.append('limit', String(params.limit))
        
        const url = `/missions${queryString.toString() ? `?${queryString.toString()}` : ''}`
        return {
          url,
          method: 'GET',
        }
      },
      providesTags: ['Missions'],
    }),
  }),
})

export const {
  useGetMissionsQuery,
} = missionsApi
