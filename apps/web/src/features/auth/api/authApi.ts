import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import type { User, LoginResponse } from '@/types'
import type { RootState } from '@/store/store'
import { setCredentials } from '../slices/authSlice'

// Use relative URLs to go through Vite proxy
const AUTH_SERVICE_URL = '/auth-api'

export const authApi = createApi({
  reducerPath: 'authApi',
  baseQuery: fetchBaseQuery({
    baseUrl: AUTH_SERVICE_URL,
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token
      if (token) {
        headers.set('authorization', `Bearer ${token}`)
      }
      return headers
    },
  }),
  endpoints: (builder) => ({
    localLogin: builder.mutation<LoginResponse, { username: string; password: string }>({
      query: (credentials) => ({
        url: '/auth/local/login',
        method: 'POST',
        body: credentials,
      }),
      async onQueryStarted(arg, { dispatch, queryFulfilled }) {
        try {
          const { data } = await queryFulfilled
          if (data.access_token && data.user) {
            // Store credentials in Redux store
            dispatch(
              setCredentials({
                user: data.user,
                token: data.access_token,
                refreshToken: data.refresh_token,
              })
            )
            // Store in localStorage for persistence
            localStorage.setItem('access_token', data.access_token)
            if (data.refresh_token) {
              localStorage.setItem('refresh_token', data.refresh_token)
            }
            localStorage.setItem('user', JSON.stringify(data.user))
          }
        } catch (error) {
          // Error handled by mutation
        }
      },
    }),
    register: builder.mutation<
      LoginResponse,
      {
        username: string
        email: string
        password: string
        full_name: string
        phone?: string
        date_of_birth?: string
        company_name?: string
        legal_representative?: string
        nif?: string
        location?: any
      }
    >({
      query: (data) => ({
        url: '/auth/local/register',
        method: 'POST',
        body: data,
      }),
    }),
    getCurrentUser: builder.query<User, void>({
      query: () => '/auth/me',
    }),
    logout: builder.mutation<void, void>({
      query: () => ({
        url: '/auth/logout',
        method: 'POST',
      }),
    }),
    refreshToken: builder.mutation<LoginResponse, { refresh_token: string }>({
      query: (body) => ({
        url: '/auth/refresh',
        method: 'POST',
        body,
      }),
    }),
  }),
})

export const {
  useLocalLoginMutation,
  useRegisterMutation,
  useGetCurrentUserQuery,
  useLogoutMutation,
  useRefreshTokenMutation,
} = authApi
