import { createApi } from '@reduxjs/toolkit/query/react'
import { createBaseQueryWithAuth } from '@/utils/baseQueryWithAuth'

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
  baseQuery: createBaseQueryWithAuth(),
  tagTypes: ['Permissions', 'Profiles', 'Groups', 'UserPermissions'],
  endpoints: (builder) => ({
    // Permissions
    listPermissions: builder.query<Permission[], void>({
      query: () => '/iam/permissions',
      providesTags: ['Permissions'],
    }),
    
    createPermission: builder.mutation<Permission, Partial<Permission>>({
      query: (permission) => ({
        url: '/iam/permissions',
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
      query: () => '/iam/profiles',
      providesTags: ['Profiles'],
    }),
    
    getProfile: builder.query<Profile, string>({
      query: (profileId) => `/iam/profiles/${profileId}`,
      providesTags: (_result, _error, profileId) => [{ type: 'Profiles', id: profileId }],
    }),
    
    createProfile: builder.mutation<Profile, ProfileCreate>({
      query: (profile) => ({
        url: '/iam/profiles',
        method: 'POST',
        body: profile,
      }),
      invalidatesTags: ['Profiles'],
    }),
    
    updateProfile: builder.mutation<Profile, { id: string; data: ProfileUpdate }>({
      query: ({ id, data }) => ({
        url: `/iam/profiles/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: ['Profiles'],
    }),
    
    deleteProfile: builder.mutation<void, string>({
      query: (profileId) => ({
        url: `/iam/profiles/${profileId}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Profiles'],
    }),
    
    // Groups
    listGroups: builder.query<Group[], void>({
      query: () => '/iam/groups',
      providesTags: ['Groups'],
    }),
    
    getGroup: builder.query<Group, string>({
      query: (groupId) => `/iam/groups/${groupId}`,
      providesTags: (_result, _error, groupId) => [{ type: 'Groups', id: groupId }],
    }),
    
    createGroup: builder.mutation<Group, GroupCreate>({
      query: (group) => ({
        url: '/iam/groups',
        method: 'POST',
        body: group,
      }),
      invalidatesTags: ['Groups'],
    }),
    
    updateGroup: builder.mutation<Group, { id: string; data: GroupUpdate }>({
      query: ({ id, data }) => ({
        url: `/iam/groups/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: ['Groups'],
    }),
    
    deleteGroup: builder.mutation<void, string>({
      query: (groupId) => ({
        url: `/iam/groups/${groupId}`,
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
      query: (userId) => `/iam/unified/users/${userId}/permissions`,
      providesTags: (_result, _error, userId) => [{ type: 'UserPermissions', id: userId }],
      transformResponse: (response: any) => {
        // Transformer la réponse unifiée au format attendu
        return {
          user_id: response.user_id,
          direct_profiles: [],
          group_profiles: [],
          all_permissions: response.permissions || [],
          groups: []
        }
      },
    }),
    
    checkPermission: builder.mutation<PermissionCheckResponse, { user_id: string; permission_code: string; resource_id?: string }>({
      query: (data) => ({
        url: '/check-permission',
        method: 'POST',
        body: data,
      }),
    }),
    
    // ============================================================================
    // IAM Roles Management (Modèle Hybride)
    // ============================================================================
    
    // Liste des rôles IAM disponibles
    listIAMRoles: builder.query<any[], void>({
      query: () => '/iam/roles',
      providesTags: ['Profiles'],  // On réutilise le tag pour invalider
    }),
    
    // Profile → IAM Roles
    assignRolesToProfile: builder.mutation<any, { profileId: string; role_ids: string[] }>({
      query: ({ profileId, role_ids }) => ({
        url: `/iam/profiles/${profileId}/roles`,
        method: 'POST',
        body: { role_ids },
      }),
      invalidatesTags: ['Profiles'],
    }),
    
    removeRoleFromProfile: builder.mutation<any, { profileId: string; roleId: string }>({
      query: ({ profileId, roleId }) => ({
        url: `/iam/profiles/${profileId}/roles/${roleId}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Profiles'],
    }),
    
    getProfileRoles: builder.query<any, string>({
      query: (profileId) => `/iam/profiles/${profileId}/roles`,
      providesTags: (_result, _error, profileId) => [{ type: 'Profiles', id: profileId }],
    }),
    
    // Group → IAM Roles
    assignRolesToGroup: builder.mutation<any, { groupId: string; role_ids: string[] }>({
      query: ({ groupId, role_ids }) => ({
        url: `/iam/groups/${groupId}/roles`,
        method: 'POST',
        body: { role_ids },
      }),
      invalidatesTags: ['Groups'],
    }),
    
    removeRoleFromGroup: builder.mutation<any, { groupId: string; roleId: string }>({
      query: ({ groupId, roleId }) => ({
        url: `/iam/groups/${groupId}/roles/${roleId}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Groups'],
    }),
    
    getGroupRoles: builder.query<any, string>({
      query: (groupId) => `/iam/groups/${groupId}/roles`,
      providesTags: (_result, _error, groupId) => [{ type: 'Groups', id: groupId }],
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
  
  // IAM Roles Management (Modèle Hybride)
  useListIAMRolesQuery,
  useAssignRolesToProfileMutation,
  useRemoveRoleFromProfileMutation,
  useGetProfileRolesQuery,
  useAssignRolesToGroupMutation,
  useRemoveRoleFromGroupMutation,
  useGetGroupRolesQuery,
} = iamApi
