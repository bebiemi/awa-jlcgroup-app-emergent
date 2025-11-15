/**
 * Entreprise API - Company Management
 * RTK Query API slice for managing company/entreprise information
 */
import { createApi } from '@reduxjs/toolkit/query/react'
import { baseQueryWithAuth } from '@/utils/baseQueryWithAuth'

export interface Entreprise {
  id: string
  nom: string
  raison_sociale: string
  siret: string
  adresse: string
  code_postal?: string
  ville?: string
  pays: string
  email: string
  telephone: string
  description?: string
  secteur_activite?: string
  effectif?: string
  site_web?: string
  status: string
  created_at: string
  updated_at?: string
  created_by?: string
}

export interface EntrepriseCreate {
  nom: string
  raison_sociale: string
  siret: string
  adresse: string
  code_postal?: string
  ville?: string
  pays?: string
  email: string
  telephone: string
  description?: string
  secteur_activite?: string
  effectif?: string
  site_web?: string
}

export interface EntrepriseUpdate {
  nom?: string
  raison_sociale?: string
  siret?: string
  adresse?: string
  code_postal?: string
  ville?: string
  pays?: string
  email?: string
  telephone?: string
  description?: string
  secteur_activite?: string
  effectif?: string
  site_web?: string
  status?: string
}

export const entrepriseApi = createApi({
  reducerPath: 'entrepriseApi',
  baseQuery: baseQueryWithAuth,
  tagTypes: ['Entreprise', 'EntrepriseList'],
  endpoints: (builder) => ({
    // Get current user's entreprise
    getMyEntreprise: builder.query<Entreprise, void>({
      query: () => '/entreprises/me',
      providesTags: ['Entreprise'],
    }),

    // Get entreprise by ID
    getEntreprise: builder.query<Entreprise, string>({
      query: (id) => `/entreprises/${id}`,
      providesTags: (result, error, id) => [{ type: 'Entreprise', id }],
    }),

    // List entreprises (admin)
    listEntreprises: builder.query<
      Entreprise[],
      { skip?: number; limit?: number; status?: string }
    >({
      query: ({ skip = 0, limit = 100, status }) => {
        const params = new URLSearchParams({
          skip: skip.toString(),
          limit: limit.toString(),
        })
        if (status) params.append('status', status)
        return `/entreprises?${params.toString()}`
      },
      providesTags: ['EntrepriseList'],
    }),

    // Create entreprise (admin)
    createEntreprise: builder.mutation<Entreprise, EntrepriseCreate>({
      query: (data) => ({
        url: '/entreprises',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['EntrepriseList'],
    }),

    // Update current user's entreprise
    updateMyEntreprise: builder.mutation<Entreprise, EntrepriseUpdate>({
      query: (data) => ({
        url: '/entreprises/me',
        method: 'PATCH',
        body: data,
      }),
      invalidatesTags: ['Entreprise'],
    }),

    // Update entreprise by ID (admin)
    updateEntreprise: builder.mutation<
      Entreprise,
      { id: string; data: EntrepriseUpdate }
    >({
      query: ({ id, data }) => ({
        url: `/entreprises/${id}`,
        method: 'PATCH',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Entreprise', id },
        'EntrepriseList',
      ],
    }),

    // Delete entreprise (admin)
    deleteEntreprise: builder.mutation<void, string>({
      query: (id) => ({
        url: `/entreprises/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['EntrepriseList'],
    }),
  }),
})

export const {
  useGetMyEntrepriseQuery,
  useGetEntrepriseQuery,
  useListEntreprisesQuery,
  useCreateEntrepriseMutation,
  useUpdateMyEntrepriseMutation,
  useUpdateEntrepriseMutation,
  useDeleteEntrepriseMutation,
} = entrepriseApi
