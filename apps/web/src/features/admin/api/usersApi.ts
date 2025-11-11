import { createApi } from '@reduxjs/toolkit/query/react'
import { baseQueryWithAuth } from '@/utils/baseQueryWithAuth'
import type { RootState } from '@/store/store'

export interface User {
  id: string
  username: string
  email: string
  full_name?: string
  provider: string
  status: 'active' | 'pending' | 'suspended' | 'deleted'
  roles: string[]
  created_at: string
  updated_at: string
  last_login_at?: string
}

export interface UsersResponse {
  users: User[]
  pagination: {
    page: number
    page_size: number
    total: number
    total_pages: number
    has_next: boolean
    has_prev: boolean
  }
}

export const usersApi = createApi({
  reducerPath: 'usersApi',
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
  tagTypes: ['Users'],
  endpoints: (builder) => ({
    getUsers: builder.query<UsersResponse, { page?: number; page_size?: number; search?: string; status?: string; role?: string }>({
      query: ({ page = 1, page_size = 15, search, status, role }) => {
        const params = new URLSearchParams({ page: page.toString(), page_size: page_size.toString() })
        if (search) params.append('search', search)
        if (status) params.append('status', status)
        if (role) params.append('role', role)
        return `/users?${params.toString()}`
      },
      providesTags: ['Users'],
    }),
    updateUserStatus: builder.mutation<{ message: string }, { user_id: string; status: string }>({
      query: ({ user_id, status }) => ({
        url: `/users/${user_id}/status`,
        method: 'PATCH',
        body: { status },
      }),
      invalidatesTags: ['Users'],
    }),
    updateUser: builder.mutation<{ message: string }, { user_id: string; data: Partial<User> }>({
      query: ({ user_id, data }) => ({
        url: `/users/${user_id}`,
        method: 'PATCH',
        body: data,
      }),
      invalidatesTags: ['Users'],
    }),
    deleteUser: builder.mutation<{ message: string }, string>({
      query: (user_id) => ({
        url: `/users/${user_id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Users'],
    }),
    resetUserMfa: builder.mutation<{ success: boolean; message: string; user_id: string }, string>({
      query: (user_id) => ({
        url: `/admin/users/${user_id}/mfa/reset`,
        method: 'POST',
      }),
      invalidatesTags: ['Users'],
    }),
  }),
})

export const {
  useGetUsersQuery,
  useUpdateUserStatusMutation,
  useUpdateUserMutation,
  useDeleteUserMutation,
  useResetUserMfaMutation,
} = usersApi
