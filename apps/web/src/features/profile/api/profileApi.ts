import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import type { Profile } from '@/types'
import type { RootState } from '@/store/store'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'

export const profileApi = createApi({
  reducerPath: 'profileApi',
  baseQuery: fetchBaseQuery({
    baseUrl: `${API_BASE_URL}/api`,
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token
      if (token) {
        headers.set('authorization', `Bearer ${token}`)
      }
      return headers
    },
  }),
  tagTypes: ['Profile'],
  endpoints: (builder) => ({
    getMyProfile: builder.query<Profile, void>({
      query: () => '/profiles/me',
      providesTags: ['Profile'],
    }),
    updateMyProfile: builder.mutation<Profile, Partial<Profile>>({
      query: (data) => ({
        url: '/profiles/me',
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: ['Profile'],
    }),
    uploadAvatar: builder.mutation<Profile, FormData>({
      query: (formData) => ({
        url: '/profiles/me/avatar',
        method: 'POST',
        body: formData,
      }),
      invalidatesTags: ['Profile'],
    }),
    getUserProfile: builder.query<Profile, string>({
      query: (userId) => `/profiles/${userId}`,
    }),
  }),
})

export const {
  useGetMyProfileQuery,
  useUpdateMyProfileMutation,
  useUploadAvatarMutation,
  useGetUserProfileQuery,
} = profileApi
