import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import type { RootState } from '@/store/store'

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
    baseUrl: '/auth-api',
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token
      if (token) {
        headers.set('authorization', `Bearer ${token}`)
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
        url: '/locations',
        params,
      }),
      providesTags: ['Location'],
    }),

    getLocationTree: builder.query<LocationTree[], void>({
      query: () => '/locations/tree',
      providesTags: ['LocationTree'],
    }),

    getLocation: builder.query<Location, string>({
      query: (id) => `/locations/${id}`,
      providesTags: (result, error, id) => [{ type: 'Location', id }],
    }),

    createLocation: builder.mutation<Location, LocationCreate>({
      query: (data) => ({
        url: '/locations',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Location', 'LocationTree'],
    }),

    updateLocation: builder.mutation<Location, { id: string; data: LocationUpdate }>({
      query: ({ id, data }) => ({
        url: `/locations/${id}`,
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
        url: `/locations/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Location', 'LocationTree'],
    }),

    toggleLocationVisibility: builder.mutation<Location, { id: string; is_visible: boolean }>({
      query: ({ id, is_visible }) => ({
        url: `/locations/${id}/visibility`,
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
