import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'

export type LocationType = 'country' | 'province' | 'city' | 'district' | 'neighborhood'

export interface Location {
  id: string
  name: string
  type: LocationType
  parent_id: string | null
  custom_fields?: Record<string, any>
  is_visible: boolean
  is_required: boolean
  dial_code?: string
  created_at: string
  updated_at: string
  created_by: string
}

export interface LocationTree extends Location {
  children: LocationTree[]
}

export interface LocationCreate {
  name: string
  type: LocationType
  parent_id?: string | null
  custom_fields?: Record<string, any>
  is_visible?: boolean
  dial_code?: string
}

export interface LocationUpdate {
  name?: string
  custom_fields?: Record<string, any>
  is_visible?: boolean
  dial_code?: string
}

export const locationApi = createApi({
  reducerPath: 'locationApi',
  baseQuery: fetchBaseQuery({
    baseUrl: `${API_BASE_URL}/api/locations`,
    prepareHeaders: (headers) => {
      const token = localStorage.getItem('access_token')
      if (token) {
        headers.set('Authorization', `Bearer ${token}`)
      }
      return headers
    },
  }),
  tagTypes: ['Location', 'LocationTree'],
  endpoints: (builder) => ({
    getLocations: builder.query<Location[], {
      type?: LocationType
      parent_id?: string | null
      is_visible?: boolean
      search?: string
      skip?: number
      limit?: number
    }>({
      query: (params) => ({
        url: '',
        params,
      }),
      providesTags: ['Location'],
    }),

    getLocationTree: builder.query<LocationTree[], void>({
      query: () => '/tree',
      providesTags: ['LocationTree'],
    }),

    getLocation: builder.query<Location, string>({
      query: (id) => `/${id}`,
      providesTags: (result, error, id) => [{ type: 'Location', id }],
    }),

    createLocation: builder.mutation<Location, LocationCreate>({
      query: (data) => ({
        url: '',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Location', 'LocationTree'],
    }),

    updateLocation: builder.mutation<Location, { id: string; data: LocationUpdate }>({
      query: ({ id, data }) => ({
        url: `/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Location', id },
        'Location',
        'LocationTree',
      ],
    }),

    deleteLocation: builder.mutation<{ success: boolean; message: string }, string>({
      query: (id) => ({
        url: `/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Location', 'LocationTree'],
    }),

    toggleLocationVisibility: builder.mutation<Location, { id: string; is_visible: boolean }>({
      query: ({ id, is_visible }) => ({
        url: `/${id}/visibility`,
        method: 'PATCH',
        params: { is_visible },
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Location', id },
        'Location',
        'LocationTree',
      ],
    }),
  }),
})

export const {
  useGetLocationsQuery,
  useGetLocationTreeQuery,
  useGetLocationQuery,
  useCreateLocationMutation,
  useUpdateLocationMutation,
  useDeleteLocationMutation,
  useToggleLocationVisibilityMutation,
} = locationApi
