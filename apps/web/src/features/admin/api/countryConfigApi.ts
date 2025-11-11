import { createApi } from '@reduxjs/toolkit/query/react'
import { baseQueryWithAuth } from '@/utils/baseQueryWithAuth'

// Types
export interface Country {
  id: string
  name: string
  iso_code: string
  phone_prefix: string
  currency_code: string
  currency_symbol: string
  active: boolean
  is_default: boolean
  created_at?: string
  updated_at?: string
}

export interface City {
  id: string
  country_id: string
  name: string
  active: boolean
  created_at?: string
  updated_at?: string
}

export interface CountryCreate {
  name: string
  iso_code: string
  phone_prefix: string
  currency_code: string
  currency_symbol: string
  active?: boolean
}

export interface CountryUpdate {
  name?: string
  phone_prefix?: string
  currency_code?: string
  currency_symbol?: string
  active?: boolean
}

export interface CityCreate {
  name: string
  active?: boolean
}

export const countryConfigApi = createApi({
  reducerPath: 'countryConfigApi',
  baseQuery: baseQueryWithAuth,
  tagTypes: ['Countries', 'Cities'],
  endpoints: (builder) => ({
    // Get all countries
    getCountries: builder.query<Country[], { active_only?: boolean }>({
      query: ({ active_only = true }) => ({
        url: '/config/countries',
        params: { active_only },
      }),
      providesTags: ['Countries'],
    }),

    // Get single country
    getCountry: builder.query<Country, string>({
      query: (countryId) => `/config/countries/${countryId}`,
      providesTags: (result, error, id) => [{ type: 'Countries', id }],
    }),

    // Initialize default countries
    initDefaultCountries: builder.mutation<{ message: string; count: number }, void>({
      query: () => ({
        url: '/config/countries/init-default',
        method: 'POST',
      }),
      invalidatesTags: ['Countries'],
    }),

    // Create country
    createCountry: builder.mutation<Country, CountryCreate>({
      query: (country) => ({
        url: '/config/countries',
        method: 'POST',
        body: country,
      }),
      invalidatesTags: ['Countries'],
    }),

    // Update country
    updateCountry: builder.mutation<Country, { id: string; data: CountryUpdate }>({
      query: ({ id, data }) => ({
        url: `/config/countries/${id}`,
        method: 'PATCH',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [{ type: 'Countries', id }, 'Countries'],
    }),

    // Set country as default
    setDefaultCountry: builder.mutation<{ message: string; country_id: string }, string>({
      query: (countryId) => ({
        url: `/config/countries/${countryId}/set-default`,
        method: 'PATCH',
      }),
      invalidatesTags: ['Countries'],
    }),

    // Delete country
    deleteCountry: builder.mutation<{ message: string }, string>({
      query: (countryId) => ({
        url: `/config/countries/${countryId}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Countries'],
    }),

    // Get cities for a country
    getCities: builder.query<City[], { countryId: string; search?: string; active_only?: boolean }>({
      query: ({ countryId, search, active_only = true }) => ({
        url: `/config/countries/${countryId}/cities`,
        params: { search, active_only },
      }),
      providesTags: (result, error, { countryId }) => [{ type: 'Cities', id: countryId }],
    }),

    // Create city
    createCity: builder.mutation<City, { countryId: string; data: CityCreate }>({
      query: ({ countryId, data }) => ({
        url: `/config/countries/${countryId}/cities`,
        method: 'POST',
        body: data,
      }),
      invalidatesTags: (result, error, { countryId }) => [{ type: 'Cities', id: countryId }],
    }),

    // Delete city
    deleteCity: builder.mutation<{ message: string }, string>({
      query: (cityId) => ({
        url: `/config/countries/cities/${cityId}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Cities'],
    }),
  }),
})

export const {
  useGetCountriesQuery,
  useGetCountryQuery,
  useInitDefaultCountriesMutation,
  useCreateCountryMutation,
  useUpdateCountryMutation,
  useSetDefaultCountryMutation,
  useDeleteCountryMutation,
  useGetCitiesQuery,
  useCreateCityMutation,
  useDeleteCityMutation,
} = countryConfigApi
