import { createApi } from '@reduxjs/toolkit/query/react'
import { baseQueryWithAuth } from '@/utils/baseQueryWithAuth'
import type { User, LoginResponse } from '@/types'
import type { RootState } from '@/store/store'

// Use relative URLs to go through Vite proxy

export const authApi = createApi({
  reducerPath: 'authApi',
  baseQuery: baseQueryWithAuth,
  endpoints: (builder) => ({
    localLogin: builder.mutation<LoginResponse, { username: string; password: string }>({
      query: (credentials) => ({
        url: '/api/auth/local/login',
        method: 'POST',
        body: credentials,
      }),
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
        url: '/api/auth/local/register',
        method: 'POST',
        body: data,
      }),
    }),
    getCurrentUser: builder.query<User, void>({
      query: () => '/auth/me',
    }),
    logout: builder.mutation<void, void>({
      query: () => ({
        url: '/api/auth/logout',
        method: 'POST',
      }),
    }),
    refreshToken: builder.mutation<LoginResponse, { refresh_token: string }>({
      query: (body) => ({
        url: '/api/auth/refresh',
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
