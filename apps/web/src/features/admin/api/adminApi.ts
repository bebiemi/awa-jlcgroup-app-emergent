import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import type { RootState } from '@/store/store'

export interface AdminStats {
  total_users: number
  users_by_status: {
    active: number
    pending: number
    suspended: number
  }
  users_by_role: {
    admin: number
    super_admin: number
    interim: number
    company: number
    agency: number
  }
  users_by_provider: {
    local: number
    google: number
  }
  mfa_enabled: number
  recent_users_7d: number
  recent_logins_24h: number
  groups_count: number
  profiles_count: number
  last_updated: string
}

export const adminApi = createApi({
  reducerPath: 'adminApi',
  baseQuery: fetchBaseQuery({
    baseUrl: '/auth-api/auth',
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token
      if (token) {
        headers.set('authorization', `Bearer ${token}`)
      }
      return headers
    },
  }),
  tagTypes: ['AdminStats'],
  endpoints: (builder) => ({
    getAdminStats: builder.query<AdminStats, void>({
      query: () => '/admin/stats',
      providesTags: ['AdminStats'],
    }),
  }),
})

export const { useGetAdminStatsQuery } = adminApi
