import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import type { RootState } from '@/store/store'
import { baseQueryWithAuth } from '@/utils/baseQueryWithAuth'

// Types
export type MissionStatus = 
  | 'draft' 
  | 'pending_validation'
  | 'published'
  | 'accepting_applications'
  | 'applications_closed'
  | 'in_review'
  | 'interviews_scheduled'
  | 'interviews_completed'
  | 'profiles_sent_to_client'
  | 'client_selection_pending'
  | 'client_selection_completed'
  | 'medical_check_pending'
  | 'medical_check_completed'
  | 'contract_pending'
  | 'contract_signed'
  | 'completed'
  | 'cancelled'
  | 'on_hold'

export type ApplicationStatus = 
  | 'submitted'
  | 'received'
  | 'under_review'
  | 'shortlisted'
  | 'rejected_initial'
  | 'interview_scheduled'
  | 'interview_completed'
  | 'selected_for_client'
  | 'rejected_after_interview'
  | 'sent_to_client'
  | 'selected_by_client'
  | 'rejected_by_client'
  | 'standby'
  | 'medical_check_pending'
  | 'medical_approved'
  | 'medical_rejected'
  | 'contract_pending'
  | 'contract_signed'
  | 'hired'
  | 'rejected'
  | 'withdrawn'

export type MedicalStatus = 'not_required' | 'pending' | 'scheduled' | 'completed_apte' | 'completed_inapte' | 'document_uploaded'

export type ContractStatus = 'not_generated' | 'draft' | 'sent' | 'signed_by_interim' | 'signed_by_company' | 'fully_signed'

export interface Mission {
  id: string
  title: string
  description: string
  company_id: string
  
  // Détails du poste
  job_type: string
  required_skills: string[]
  experience_required: string
  education_level?: string
  
  // Informations mission
  start_date?: string
  end_date?: string
  duration?: string
  location: string
  location_details?: Record<string, any>
  
  // Conditions
  salary_range?: string
  contract_type: string
  working_hours?: string
  benefits?: string[]
  
  // Configuration
  max_applications?: number
  application_deadline?: string
  requires_medical_check: boolean
  
  // Workflow
  status: MissionStatus
  created_by: string
  commercial_id?: string
  
  // Statistiques
  applications_count: number
  shortlisted_count: number
  selected_count: number
  hired_count: number
  
  // Tracking
  published_at?: string
  closed_at?: string
  completed_at?: string
  
  created_at: string
  updated_at: string
  custom_fields?: Record<string, any>
}

export interface MissionCreate {
  title: string
  description: string
  company_id: string
  job_type: string
  required_skills: string[]
  experience_required: string
  education_level?: string
  start_date?: string
  end_date?: string
  duration?: string
  location: string
  location_details?: Record<string, any>
  salary_range?: string
  contract_type: string
  working_hours?: string
  benefits?: string[]
  max_applications?: number
  application_deadline?: string
  requires_medical_check?: boolean
  created_by: string
  commercial_id?: string
}

export interface MissionUpdate {
  title?: string
  description?: string
  job_type?: string
  required_skills?: string[]
  experience_required?: string
  education_level?: string
  start_date?: string
  end_date?: string
  duration?: string
  location?: string
  salary_range?: string
  contract_type?: string
  working_hours?: string
  benefits?: string[]
  max_applications?: number
  application_deadline?: string
  requires_medical_check?: boolean
  status?: MissionStatus
  commercial_id?: string
}

export interface Application {
  id: string
  mission_id: string
  user_id: string
  
  cover_letter?: string
  matching_skills: string[]
  additional_info?: string
  
  status: ApplicationStatus
  score?: number
  internal_notes?: string
  
  // Entretien
  interview_scheduled_at?: string
  interview_completed_at?: string
  interview_notes?: string
  interview_rating?: number
  
  // Client
  sent_to_client_at?: string
  client_response_at?: string
  client_selected?: boolean
  client_feedback?: string
  
  // Médical
  medical_status: MedicalStatus
  medical_document_url?: string
  medical_scheduled_at?: string
  medical_completed_at?: string
  medical_notes?: string
  
  // Contrat
  contract_status: ContractStatus
  contract_url?: string
  contract_sent_at?: string
  contract_signed_at?: string
  
  created_at: string
  updated_at: string
}

export interface ApplicationCreate {
  mission_id: string
  user_id: string
  cover_letter?: string
  matching_skills?: string[]
  additional_info?: string
}

export interface ApplicationUpdate {
  status?: ApplicationStatus
  cover_letter?: string
  matching_skills?: string[]
  additional_info?: string
  internal_notes?: string
  score?: number
  interview_scheduled_at?: string
  interview_notes?: string
  interview_rating?: number
  client_feedback?: string
  client_selected?: boolean
  medical_status?: MedicalStatus
  medical_document_url?: string
  medical_notes?: string
  contract_status?: ContractStatus
  contract_url?: string
  contract_signed_at?: string
}

export interface MissionStats {
  mission_id: string
  total_applications: number
  shortlisted: number
  selected_by_client: number
  hired: number
  conversion_rate: number
}

export const missionApi = createApi({
  reducerPath: 'missionApi',
  baseQuery: baseQueryWithAuth,
  tagTypes: ['Mission', 'Application', 'MyApplications'],
  endpoints: (builder) => ({
    // ==================== MISSIONS ====================
    getMissions: builder.query<Mission[], {
      status?: MissionStatus
      company_id?: string
      commercial_id?: string
      published_only?: boolean
      skip?: number
      limit?: number
    }>({
      query: (params) => ({
        url: '/api/missions',
        params,
      }),
      providesTags: ['Mission'],
    }),

    getMission: builder.query<Mission, string>({
      query: (id) => `/missions/${id}`,
      providesTags: (result, error, id) => [{ type: 'Mission', id }],
    }),

    createMission: builder.mutation<Mission, MissionCreate>({
      query: (data) => ({
        url: '/api/missions',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Mission'],
    }),

    updateMission: builder.mutation<Mission, { id: string; data: MissionUpdate }>({
      query: ({ id, data }) => ({
        url: `/missions/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [{ type: 'Mission', id }, 'Mission'],
    }),

    deleteMission: builder.mutation<void, string>({
      query: (id) => ({
        url: `/missions/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Mission'],
    }),

    publishMission: builder.mutation<Mission, string>({
      query: (id) => ({
        url: `/missions/${id}/publish`,
        method: 'POST',
      }),
      invalidatesTags: (result, error, id) => [{ type: 'Mission', id }, 'Mission'],
    }),

    getMissionStats: builder.query<MissionStats, string>({
      query: (id) => `/missions/${id}/stats`,
    }),

    // ==================== APPLICATIONS ====================
    applyToMission: builder.mutation<Application, ApplicationCreate>({
      query: (data) => ({
        url: `/missions/${data.mission_id}/apply`,
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Mission', 'MyApplications'],
    }),

    getMissionApplications: builder.query<Application[], {
      mission_id: string
      status?: ApplicationStatus
    }>({
      query: ({ mission_id, status }) => ({
        url: `/missions/${mission_id}/applications`,
        params: status ? { status } : {},
      }),
      providesTags: ['Application'],
    }),

    getMyApplications: builder.query<Application[], void>({
      query: () => '/missions/applications/my-applications',
      providesTags: ['MyApplications'],
    }),

    updateApplication: builder.mutation<Application, { id: string; data: ApplicationUpdate }>({
      query: ({ id, data }) => ({
        url: `/missions/applications/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: ['Application', 'MyApplications', 'Mission'],
    }),

    shortlistApplication: builder.mutation<Application, string>({
      query: (id) => ({
        url: `/missions/applications/${id}/shortlist`,
        method: 'POST',
      }),
      invalidatesTags: ['Application', 'Mission'],
    }),

    uploadMedicalDocument: builder.mutation<Application, {
      application_id: string
      file_url: string
      medical_status: MedicalStatus
      notes?: string
    }>({
      query: ({ application_id, ...data }) => ({
        url: `/missions/applications/${application_id}/upload-medical`,
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Application', 'MyApplications'],
    }),
  }),
})

export const {
  useGetMissionsQuery,
  useGetMissionQuery,
  useCreateMissionMutation,
  useUpdateMissionMutation,
  useDeleteMissionMutation,
  usePublishMissionMutation,
  useGetMissionStatsQuery,
  useApplyToMissionMutation,
  useGetMissionApplicationsQuery,
  useGetMyApplicationsQuery,
  useUpdateApplicationMutation,
  useShortlistApplicationMutation,
  useUploadMedicalDocumentMutation,
} = missionApi
