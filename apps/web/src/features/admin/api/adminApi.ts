import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import type { DashboardKPIs } from '@/types'
import type { RootState } from '@/store/store'

export const adminApi = createApi({
  reducerPath: 'adminApi',
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
