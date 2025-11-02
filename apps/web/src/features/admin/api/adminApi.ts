import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import type { DashboardKPIs } from '@/types'
import type { RootState } from '@/store/store'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'

export const adminApi = createApi({
  reducerPath: 'adminApi',
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
  endpoints: (builder) => ({
    getDashboardKPIs: builder.query<DashboardKPIs, void>({
      query: () => '/admin/dashboard/kpis',
    }),
    getUserAudit: builder.query<any, string>({
      query: (userId) => `/admin/users/${userId}/audit`,
    }),
  }),
})

export const { useGetDashboardKPIsQuery, useGetUserAuditQuery } = adminApi
