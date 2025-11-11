import { createApi } from '@reduxjs/toolkit/query/react'
import { baseQueryWithAuth } from '@/utils/baseQueryWithAuth'

export type PresenceStatus = 'online' | 'away' | 'do_not_disturb' | 'offline' | 'invisible'

export interface UserPresence {
  user_id: string
  username: string
  full_name?: string
  presence_status: PresenceStatus
  presence_updated_at: string
  last_activity_at: string
}

export interface OnlineUsersResponse {
  users: UserPresence[]
  total: number
  timestamp: string
}

export const presenceApi = createApi({
  reducerPath: 'presenceApi',
  baseQuery: baseQueryWithAuth,
  // Prevent infinite retry loops
  refetchOnMountOrArgChange: false,
  refetchOnFocus: false,
  refetchOnReconnect: false,
  tagTypes: ['Presence', 'OnlineUsers'],
  endpoints: (builder) => ({
    getMyPresence: builder.query<UserPresence, void>({
      query: () => '/me',
      providesTags: ['Presence'],
    }),
    updateMyPresence: builder.mutation<UserPresence, { status: PresenceStatus }>({
      query: (body) => ({
        url: '/me',
        method: 'PATCH',
        body,
      }),
      invalidatesTags: ['Presence', 'OnlineUsers'],
    }),
    updateActivity: builder.mutation<{ success: boolean; timestamp: string }, void>({
      query: () => ({
        url: '/activity',
        method: 'POST',
      }),
      invalidatesTags: ['Presence'],
    }),
    getOnlineUsers: builder.query<OnlineUsersResponse, void>({
      query: () => '/online',
      providesTags: ['OnlineUsers'],
    }),
    getUserPresence: builder.query<UserPresence, string>({
      query: (userId) => `/${userId}`,
    }),
  }),
})

export const {
  useGetMyPresenceQuery,
  useUpdateMyPresenceMutation,
  useUpdateActivityMutation,
  useGetOnlineUsersQuery,
  useGetUserPresenceQuery,
} = presenceApi
