import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

export interface Permission {
  id: string
  name: string
  label: string
  description?: string
  module: string
  created_at: string
}

export interface Profile {
  id: string
  name: string
  description?: string
  permissions: string[]
  is_system: boolean
  created_at: string
  updated_at: string
  created_by?: string
}

export interface Group {
  id: string
  name: string
  description?: string
  profile_id?: string
  member_ids: string[]
  created_at: string
  updated_at: string
  created_by?: string
}

export interface CreateUserRequest {
  email: string
  username?: string
  full_name?: string
  password?: string
  roles: string[]
  group_ids: string[]
  profile_id?: string
  send_invitation: boolean
}

export interface CreateGroupRequest {
  name: string
  description?: string
  profile_id?: string
  member_ids: string[]
}

export interface CreateProfileRequest {
  name: string
  description?: string
  permissions: string[]
}

export const securityApi = createApi({
  reducerPath: 'securityApi',
  baseQuery: fetchBaseQuery({
    baseUrl: '/auth-api/auth/security',
    prepareHeaders: (headers) => {
      // CRITICAL: Use localStorage directly for more reliable token access
      const token = localStorage.getItem('access_token')
      if (token) {
        headers.set('Authorization', `Bearer ${token}`) // Note: Capital 'A' in Authorization
      }
      return headers
    },
  }),
  tagTypes: ['Permissions', 'Profiles', 'Groups'],
  endpoints: (builder) => ({
    // Permissions
    getPermissions: builder.query<Permission[], { module?: string }>({
      query: ({ module }) => ({
        url: '/permissions',
        params: module ? { module } : {},
      }),
      providesTags: ['Permissions'],
    }),

    // Profiles
    getProfiles: builder.query<Profile[], void>({
      query: () => '/profiles',
      providesTags: ['Profiles'],
    }),
    getProfile: builder.query<Profile, string>({
      query: (id) => `/profiles/${id}`,
      providesTags: ['Profiles'],
    }),
    createProfile: builder.mutation<Profile, CreateProfileRequest>({
      query: (data) => ({
        url: '/profiles',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Profiles'],
    }),
    updateProfile: builder.mutation<Profile, { id: string; data: CreateProfileRequest }>({
      query: ({ id, data }) => ({
        url: `/profiles/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: ['Profiles'],
    }),
    deleteProfile: builder.mutation<{ message: string }, string>({
      query: (id) => ({
        url: `/profiles/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Profiles'],
    }),

    // Groups
    getGroups: builder.query<Group[], void>({
      query: () => '/groups',
      providesTags: ['Groups'],
    }),
    getGroup: builder.query<Group, string>({
      query: (id) => `/groups/${id}`,
      providesTags: ['Groups'],
    }),
    createGroup: builder.mutation<Group, CreateGroupRequest>({
      query: (data) => ({
        url: '/groups',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Groups'],
    }),
    updateGroup: builder.mutation<Group, { id: string; data: CreateGroupRequest }>({
      query: ({ id, data }) => ({
        url: `/groups/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: ['Groups'],
    }),
    deleteGroup: builder.mutation<{ message: string }, string>({
      query: (id) => ({
        url: `/groups/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Groups'],
    }),
    addMemberToGroup: builder.mutation<{ message: string }, { groupId: string; userId: string }>({
      query: ({ groupId, userId }) => ({
        url: `/groups/${groupId}/members/${userId}`,
        method: 'POST',
      }),
      invalidatesTags: ['Groups'],
    }),
    removeMemberFromGroup: builder.mutation<{ message: string }, { groupId: string; userId: string }>({
      query: ({ groupId, userId }) => ({
        url: `/groups/${groupId}/members/${userId}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Groups'],
    }),

    // Create User
    createUser: builder.mutation<any, CreateUserRequest>({
      query: (data) => ({
        url: '/users',
        method: 'POST',
        body: data,
      }),
    }),
  }),
})

export const {
  useGetPermissionsQuery,
  useGetProfilesQuery,
  useGetProfileQuery,
  useCreateProfileMutation,
  useUpdateProfileMutation,
  useDeleteProfileMutation,
  useGetGroupsQuery,
  useGetGroupQuery,
  useCreateGroupMutation,
  useUpdateGroupMutation,
  useDeleteGroupMutation,
  useAddMemberToGroupMutation,
  useRemoveMemberFromGroupMutation,
  useCreateUserMutation,
} = securityApi
