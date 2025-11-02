import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import type { NotificationListResponse } from '@/types'
import type { RootState } from '@/store/store'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'

export const notificationApi = createApi({
  reducerPath: 'notificationApi',
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
  tagTypes: ['Notification'],
  endpoints: (builder) => ({
    getNotifications: builder.query<
      NotificationListResponse,
      { is_read?: boolean; page?: number; page_size?: number }
    >({
      query: (params) => ({
        url: '/notifications',
        params,
      }),
      providesTags: ['Notification'],
    }),
    markNotificationsRead: builder.mutation<void, { notification_ids: string[] }>({
      query: (body) => ({
        url: '/notifications/mark-read',
        method: 'POST',
        body,
      }),
      invalidatesTags: ['Notification'],
    }),
  }),
})

export const { useGetNotificationsQuery, useMarkNotificationsReadMutation } =
  notificationApi
