import { createApi } from '@reduxjs/toolkit/query/react'
import { baseQueryWithAuth } from '@/utils/baseQueryWithAuth'
import type { NotificationListResponse } from '@/types'
import type { RootState } from '@/store/store'

export const notificationApi = createApi({
  reducerPath: 'notificationApi',
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
