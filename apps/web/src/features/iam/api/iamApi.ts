import { createApi } from '@reduxjs/toolkit/query/react'
import { baseQueryWithAuth } from '@/utils/baseQueryWithAuth'

// Types
export interface Permission {
  id: string
  code: string
  name: string
  description?: string
  resource: string
  action: string
  scope: string
  is_system: boolean
  category: string
  created_at: string
  updated_at: string
}

export interface Profile {
  id: string
  code: string
  name: string
  description?: string
  permission_ids: string[]
  is_system_role: boolean
  is_protected: boolean
  priority: number
  category: string
  color?: string
  icon?: string
  created_at: string
  updated_at: string
  created_by?: string
}

export interface Group {
  id: string
  code: string
  name: string
  description?: string
  profile_ids: string[]
  user_ids: string[]
  is_system_group: boolean
  is_protected: boolean
  parent_group_id?: string
  organization_id?: string
  team_id?: string
  created_at: string
  updated_at: string
  created_by?: string
}

export interface UserPermissionsResponse {
  user_id: string
  direct_profiles: Profile[]
  group_profiles: Profile[]
  all_permissions: Permission[]
  groups: Group[]
}

export interface PermissionCheckResponse {
  has_permission: boolean
  granted_by: string[]
  reason?: string
}

export interface ProfileCreate {
  code: string
  name: string
  description?: string
  permission_ids?: string[]
  category?: string
  color?: string
  icon?: string
}

export interface ProfileUpdate {
  name?: string
  description?: string
  permission_ids?: string[]
  color?: string
  icon?: string
}

export interface GroupCreate {
  code: string
  name: string
  description?: string
  profile_ids?: string[]
  parent_group_id?: string
}

export interface GroupUpdate {
  name?: string
  description?: string
  profile_ids?: string[]
  parent_group_id?: string
}

export const iamApi = createApi({
  reducerPath: 'iamApi',
  baseQuery: baseQueryWithAuth,
  tagTypes: ['Permissions', 'Profiles', 'Groups', 'UserPermissions'],
  endpoints: (builder) => ({
    // Permissions
    listPermissions: builder.query<Permission[], void>({
      query: () => '/permissions',
      providesTags: ['Permissions'],
    }),
    
    createPermission: builder.mutation<Permission, Partial<Permission>>({
      query: (permission) => ({
        url: '/permissions',
        method: 'POST',
        body: permission,
      }),
      invalidatesTags: ['Permissions'],
    }),
    
    deletePermission: builder.mutation<void, string>({
      query: (permissionId) => ({
        url: `/permissions/${permissionId}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Permissions'],
    }),
    
    // Profiles
    listProfiles: builder.query<Profile[], void>({
      query: () => '/profiles',
      providesTags: ['Profiles'],
    }),
    
    getProfile: builder.query<Profile, string>({
      query: (profileId) => `/profiles/${profileId}`,
      providesTags: (_result, _error, profileId) => [{ type: 'Profiles', id: profileId }],
    }),
    
    createProfile: builder.mutation<Profile, ProfileCreate>({
      query: (profile) => ({
        url: '/profiles',
        method: 'POST',
        body: profile,
      }),
      invalidatesTags: ['Profiles'],
    }),
    
    updateProfile: builder.mutation<Profile, { id: string; data: ProfileUpdate }>({
      query: ({ id, data }) => ({
        url: `/profiles/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: ['Profiles'],
    }),
    
    deleteProfile: builder.mutation<void, string>({
      query: (profileId) => ({
        url: `/profiles/${profileId}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Profiles'],
    }),
    
    // Groups
    listGroups: builder.query<Group[], void>({
      query: () => '/groups',
      providesTags: ['Groups'],
    }),
    
    getGroup: builder.query<Group, string>({
      query: (groupId) => `/groups/${groupId}`,
      providesTags: (_result, _error, groupId) => [{ type: 'Groups', id: groupId }],
    }),
    
    createGroup: builder.mutation<Group, GroupCreate>({
      query: (group) => ({
        url: '/groups',
        method: 'POST',
        body: group,
      }),
      invalidatesTags: ['Groups'],
    }),
    
    updateGroup: builder.mutation<Group, { id: string; data: GroupUpdate }>({
      query: ({ id, data }) => ({
        url: `/groups/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: ['Groups'],
    }),
    
    deleteGroup: builder.mutation<void, string>({
      query: (groupId) => ({
        url: `/groups/${groupId}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Groups'],
    }),
    
    // User Assignments
    assignProfilesToUser: builder.mutation<void, { user_id: string; profile_ids: string[] }>({
      query: ({ user_id, profile_ids }) => ({
        url: `/users/${user_id}/profiles`,
        method: 'POST',
        body: { user_id, profile_ids },
      }),
      invalidatesTags: ['UserPermissions'],
    }),
    
    assignGroupsToUser: builder.mutation<void, { user_id: string; group_ids: string[] }>({
      query: ({ user_id, group_ids }) => ({
        url: `/users/${user_id}/groups`,
        method: 'POST',
        body: { user_id, group_ids },
      }),
      invalidatesTags: ['UserPermissions'],
    }),
    
    getUserPermissions: builder.query<UserPermissionsResponse, string>({
      query: (userId) => `/users/${userId}/permissions`,
      providesTags: (_result, _error, userId) => [{ type: 'UserPermissions', id: userId }],
    }),
    
    checkPermission: builder.mutation<PermissionCheckResponse, { user_id: string; permission_code: string; resource_id?: string }>({
      query: (data) => ({
        url: '/check-permission',
        method: 'POST',
        body: data,
      }),
    }),
  }),
})

export const {
  useListPermissionsQuery,
  useCreatePermissionMutation,
  useDeletePermissionMutation,
  
  useListProfilesQuery,
  useGetProfileQuery,
  useCreateProfileMutation,
  useUpdateProfileMutation,
  useDeleteProfileMutation,
  
  useListGroupsQuery,
  useGetGroupQuery,
  useCreateGroupMutation,
  useUpdateGroupMutation,
  useDeleteGroupMutation,
  
  useAssignProfilesToUserMutation,
  useAssignGroupsToUserMutation,
  useGetUserPermissionsQuery,
  useCheckPermissionMutation,
} = iamApi
