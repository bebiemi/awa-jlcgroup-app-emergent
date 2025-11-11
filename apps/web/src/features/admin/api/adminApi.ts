import { createApi } from '@reduxjs/toolkit/query/react'
import { baseQueryWithAuth } from '@/utils/baseQueryWithAuth'
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
  baseQuery: baseQueryWithAuth,
  tagTypes: ['AdminStats'],
  endpoints: (builder) => ({
    getAdminStats: builder.query<AdminStats, void>({
      query: () => '/admin/stats',
      providesTags: ['AdminStats'],
    }),
  }),
})

export const { useGetAdminStatsQuery } = adminApi
