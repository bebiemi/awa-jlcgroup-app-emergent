import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import type { RootState } from '@/store/store'

export type LocationType = 'country' | 'province' | 'city' | 'district' | 'neighborhood'

export interface Location {
  id: string
  type: LocationType
  name: string
  parent_id: string | null
  is_visible: boolean
  is_required: boolean
  postal_code?: string
  gps_latitude?: number
  gps_longitude?: number
  custom_field_1?: string
  custom_field_2?: string
  custom_field_3?: string
  custom_field_4?: string
  custom_field_5?: string
  custom_field_1_label?: string
  custom_field_2_label?: string
  custom_field_3_label?: string
  custom_field_4_label?: string
  custom_field_5_label?: string
  created_at: string
  updated_at: string
  created_by?: string
}

export interface LocationTree extends Location {
  children: LocationTree[]
}

export interface LocationCreate {
  type: LocationType
  name: string
  parent_id?: string | null
  postal_code?: string
  gps_latitude?: number
  gps_longitude?: number
  custom_field_1?: string
  custom_field_2?: string
  custom_field_3?: string
  custom_field_4?: string
  custom_field_5?: string
  custom_field_1_label?: string
  custom_field_2_label?: string
  custom_field_3_label?: string
  custom_field_4_label?: string
  custom_field_5_label?: string
}

export interface LocationUpdate {
  name?: string
  is_visible?: boolean
  postal_code?: string
  gps_latitude?: number
  gps_longitude?: number
  custom_field_1?: string
  custom_field_2?: string
  custom_field_3?: string
  custom_field_4?: string
  custom_field_5?: string
  custom_field_1_label?: string
  custom_field_2_label?: string
  custom_field_3_label?: string
  custom_field_4_label?: string
  custom_field_5_label?: string
}

export const locationsApi = createApi({
  reducerPath: 'locationsApi',
  baseQuery: fetchBaseQuery({
    baseUrl: '/api',
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token
      if (token) {
        headers.set('authorization', `Bearer ${token}`)
      }
      return headers
    },
  }),
  tagTypes: ['Locations', 'LocationTree'],
  endpoints: (builder) => ({
    getLocations: builder.query<Location[], { type?: LocationType; parent_id?: string; search?: string }>({
      query: (params) => {
        const searchParams = new URLSearchParams()
        if (params.type) searchParams.append('type', params.type)
        if (params.parent_id !== undefined) searchParams.append('parent_id', params.parent_id || '')
        if (params.search) searchParams.append('search', params.search)
        return `/locations?${searchParams.toString()}`
      },
      providesTags: ['Locations'],
    }),

    getLocationTree: builder.query<LocationTree[], void>({
      query: () => '/locations/tree',
      providesTags: ['LocationTree'],
    }),

    getLocation: builder.query<Location, string>({
      query: (id) => `/locations/${id}`,
      providesTags: ['Locations'],
    }),

    getLocationChildren: builder.query<Location[], string>({
      query: (parentId) => `/locations/children/${parentId}`,
      providesTags: ['Locations'],
    }),

    createLocation: builder.mutation<Location, LocationCreate>({
      query: (body) => ({
        url: '/locations',
        method: 'POST',
        body,
      }),
      invalidatesTags: ['Locations', 'LocationTree'],
    }),

    updateLocation: builder.mutation<Location, { id: string; data: LocationUpdate }>({
      query: ({ id, data }) => ({
        url: `/locations/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: ['Locations', 'LocationTree'],
    }),

    deleteLocation: builder.mutation<{ success: boolean; message: string }, string>({
      query: (id) => ({
        url: `/locations/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Locations', 'LocationTree'],
    }),

    toggleLocationVisibility: builder.mutation<{ success: boolean; message: string }, { id: string; is_visible: boolean }>({
      query: ({ id, is_visible }) => ({
        url: `/locations/${id}/visibility?is_visible=${is_visible}`,
        method: 'PATCH',
      }),
      invalidatesTags: ['Locations', 'LocationTree'],
    }),
  }),
})

export const {
  useGetLocationsQuery,
  useGetLocationTreeQuery,
  useGetLocationQuery,
  useGetLocationChildrenQuery,
  useCreateLocationMutation,
  useUpdateLocationMutation,
  useDeleteLocationMutation,
  useToggleLocationVisibilityMutation,
} = locationsApi
