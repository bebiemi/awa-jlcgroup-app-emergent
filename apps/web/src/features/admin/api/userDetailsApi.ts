import { createApi } from '@reduxjs/toolkit/query/react'
import { createBaseQueryWithAuth } from '@/utils/baseQueryWithAuth'
import { IAM_ENDPOINTS, QUERY_KEYS } from '@/constants/api'

// Use auth service URL for IAM endpoints
const authServiceUrl = import.meta.env.VITE_AUTH_SERVICE_URL || 'http://localhost:8000'
const baseQueryWithAuthService = createBaseQueryWithAuth(authServiceUrl)

// Extended User Detail Interface
export interface UserDetail {
  id: string
  username: string
  email: string
  full_name?: string
  provider: string
  status: 'active' | 'pending' | 'suspended' | 'deleted'
  roles: string[]
  groups: UserGroup[]
  profiles: UserProfile[]
  permissions: string[]
  mfa_enabled: boolean
  mfa_method?: 'totp' | 'email'
  phone?: string
  location?: string
  location_label?: string
  created_at: string
  updated_at: string
  last_login_at?: string
  last_activity_at?: string
  login_count?: number
  failed_login_attempts?: number
  metadata?: Record<string, any>
}

export interface UserGroup {
  id: string
  code: string
  name: string
  description?: string
}

export interface UserProfile {
  id: string
  code: string
  name: string
  description?: string
  color?: string
  icon?: string
}

export interface UserDocument {
  id: string
  user_id: string
  type: string
  name: string
  file_name: string
  file_size: number
  mime_type: string
  url: string
  verified: boolean
  verified_by?: string
  verified_at?: string
  uploaded_at: string
  metadata?: Record<string, any>
}

export interface UserActivity {
  id: string
  user_id: string
  action: string
  resource_type?: string
  resource_id?: string
  ip_address?: string
  user_agent?: string
  metadata?: Record<string, any>
  created_at: string
}

export interface GroupAssignment {
  group_id: string
  notes?: string
}

export interface ProfileAssignment {
  profile_id: string
  notes?: string
}

export const userDetailsApi = createApi({
  reducerPath: 'userDetailsApi',
  baseQuery: baseQueryWithAuthService,
  tagTypes: ['UserDetail', 'UserDocuments', 'UserGroups', 'UserProfiles', 'UserActivity'],
  endpoints: (builder) => ({
    // Get User Detail
    getUserDetail: builder.query<UserDetail, string>({
      query: (id) => IAM_ENDPOINTS.USERS.DETAIL(id),
      providesTags: (result, error, id) => [{ type: 'UserDetail', id }],
    }),

    // Get User Documents
    getUserDocuments: builder.query<UserDocument[], string>({
      query: (id) => IAM_ENDPOINTS.USERS.DOCUMENTS(id),
      providesTags: (result, error, id) => [
        { type: 'UserDocuments', id },
        ...(result || []).map((doc) => ({ type: 'UserDocuments' as const, id: doc.id })),
      ],
    }),

    // Verify Document
    verifyDocument: builder.mutation<{ success: boolean; message: string }, { userId: string; docId: string }>({
      query: ({ userId, docId }) => ({
        url: IAM_ENDPOINTS.USERS.DOCUMENT_VERIFY(userId, docId),
        method: 'PATCH',
      }),
      invalidatesTags: (result, error, { userId, docId }) => [
        { type: 'UserDocuments', id: userId },
        { type: 'UserDocuments', id: docId },
      ],
    }),

    // Delete Document
    deleteDocument: builder.mutation<{ success: boolean; message: string }, { userId: string; docId: string }>({
      query: ({ userId, docId }) => ({
        url: IAM_ENDPOINTS.USERS.DOCUMENT_DELETE(userId, docId),
        method: 'DELETE',
      }),
      invalidatesTags: (result, error, { userId }) => [{ type: 'UserDocuments', id: userId }],
    }),

    // Upload Document
    uploadDocument: builder.mutation<UserDocument, { userId: string; formData: FormData }>({
      query: ({ userId, formData }) => ({
        url: IAM_ENDPOINTS.USERS.DOCUMENTS(userId),
        method: 'POST',
        body: formData,
      }),
      invalidatesTags: (result, error, { userId }) => [{ type: 'UserDocuments', id: userId }],
    }),

    // Get User Groups
    getUserGroups: builder.query<UserGroup[], string>({
      query: (id) => IAM_ENDPOINTS.USERS.GROUPS(id),
      providesTags: (result, error, id) => [{ type: 'UserGroups', id }],
    }),

    // Assign Group to User
    assignGroup: builder.mutation<{ success: boolean; message: string }, { userId: string; data: GroupAssignment }>({
      query: ({ userId, data }) => ({
        url: IAM_ENDPOINTS.USERS.GROUPS(userId),
        method: 'POST',
        body: data,
      }),
      invalidatesTags: (result, error, { userId }) => [
        { type: 'UserGroups', id: userId },
        { type: 'UserDetail', id: userId },
      ],
    }),

    // Remove Group from User
    removeGroup: builder.mutation<{ success: boolean; message: string }, { userId: string; groupId: string }>({
      query: ({ userId, groupId }) => ({
        url: `${IAM_ENDPOINTS.USERS.GROUPS(userId)}/${groupId}`,
        method: 'DELETE',
      }),
      invalidatesTags: (result, error, { userId }) => [
        { type: 'UserGroups', id: userId },
        { type: 'UserDetail', id: userId },
      ],
    }),

    // Get User Profiles
    getUserProfiles: builder.query<UserProfile[], string>({
      query: (id) => IAM_ENDPOINTS.USERS.PROFILES(id),
      providesTags: (result, error, id) => [{ type: 'UserProfiles', id }],
    }),

    // Assign Profile to User
    assignProfile: builder.mutation<{ success: boolean; message: string }, { userId: string; data: ProfileAssignment }>({
      query: ({ userId, data }) => ({
        url: IAM_ENDPOINTS.USERS.PROFILES(userId),
        method: 'POST',
        body: data,
      }),
      invalidatesTags: (result, error, { userId }) => [
        { type: 'UserProfiles', id: userId },
        { type: 'UserDetail', id: userId },
      ],
    }),

    // Remove Profile from User
    removeProfile: builder.mutation<{ success: boolean; message: string }, { userId: string; profileId: string }>({
      query: ({ userId, profileId }) => ({
        url: `${IAM_ENDPOINTS.USERS.PROFILES(userId)}/${profileId}`,
        method: 'DELETE',
      }),
      invalidatesTags: (result, error, { userId }) => [
        { type: 'UserProfiles', id: userId },
        { type: 'UserDetail', id: userId },
      ],
    }),

    // Get User Activity
    getUserActivity: builder.query<{ activities: UserActivity[]; total: number }, { userId: string; page?: number; page_size?: number }>({
      query: ({ userId, page = 1, page_size = 20 }) => {
        const params = new URLSearchParams({ page: page.toString(), page_size: page_size.toString() })
        return `${IAM_ENDPOINTS.USERS.ACTIVITY(userId)}?${params.toString()}`
      },
      providesTags: (result, error, { userId }) => [{ type: 'UserActivity', id: userId }],
    }),

    // Reset Password
    resetPassword: builder.mutation<{ success: boolean; message: string }, string>({
      query: (userId) => ({
        url: IAM_ENDPOINTS.USERS.RESET_PASSWORD(userId),
        method: 'POST',
      }),
    }),

    // Reset MFA
    resetMfa: builder.mutation<{ success: boolean; message: string }, string>({
      query: (userId) => ({
        url: IAM_ENDPOINTS.USERS.RESET_MFA(userId),
        method: 'POST',
      }),
      invalidatesTags: (result, error, userId) => [{ type: 'UserDetail', id: userId }],
    }),

    // Send Notification
    sendNotification: builder.mutation<{ success: boolean; message: string }, { userId: string; data: { title: string; message: string; type?: string } }>({
      query: ({ userId, data }) => ({
        url: IAM_ENDPOINTS.USERS.SEND_NOTIFICATION(userId),
        method: 'POST',
        body: data,
      }),
    }),
  }),
})

export const {
  useGetUserDetailQuery,
  useLazyGetUserDetailQuery,
  useGetUserDocumentsQuery,
  useVerifyDocumentMutation,
  useDeleteDocumentMutation,
  useUploadDocumentMutation,
  useGetUserGroupsQuery,
  useAssignGroupMutation,
  useRemoveGroupMutation,
  useGetUserProfilesQuery,
  useAssignProfileMutation,
  useRemoveProfileMutation,
  useGetUserActivityQuery,
  useResetPasswordMutation,
  useResetMfaMutation,
  useSendNotificationMutation,
} = userDetailsApi
