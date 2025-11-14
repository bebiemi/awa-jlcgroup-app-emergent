import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import type { MfaStatus, TOTPSetupResponse, RecoveryCodesResponse, LoginResponse } from '@/types'
import type { RootState } from '@/store/store'

const AUTH_SERVICE_URL = '/api'

export const mfaApi = createApi({
  reducerPath: 'mfaApi',
  baseQuery: fetchBaseQuery({
    baseUrl: AUTH_SERVICE_URL,
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token
      if (token) {
        headers.set('authorization', `Bearer ${token}`)
      }
      return headers
    },
  }),
  tagTypes: ['MfaStatus'],
  endpoints: (builder) => ({
    // Get MFA status
    getMfaStatus: builder.query<MfaStatus, void>({
      query: () => '/auth/mfa/status',
      providesTags: ['MfaStatus'],
    }),

    // Setup TOTP
    setupTotp: builder.mutation<TOTPSetupResponse, void>({
      query: () => ({
        url: '/auth/mfa/setup/totp',
        method: 'POST',
      }),
    }),

    // Verify TOTP during setup
    verifyTotp: builder.mutation<{ success: boolean; message: string }, { code: string }>({
      query: (body) => ({
        url: '/auth/mfa/setup/totp/verify',
        method: 'POST',
        body,
      }),
      invalidatesTags: ['MfaStatus'],
    }),

    // Setup Email OTP
    setupEmailOtp: builder.mutation<{ success: boolean; message: string; email: string }, void>({
      query: () => ({
        url: '/auth/mfa/setup/email',
        method: 'POST',
      }),
      invalidatesTags: ['MfaStatus'],
    }),

    // Disable MFA method
    disableMfaMethod: builder.mutation<{ success: boolean; message: string }, { method: string; password: string }>({
      query: ({ method }) => ({
        url: `/auth/mfa/method/${method}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['MfaStatus'],
    }),

    // Get backup/recovery codes
    getBackupCodes: builder.query<RecoveryCodesResponse, void>({
      query: () => '/auth/mfa/backup-codes',
    }),

    // Generate new backup codes
    generateBackupCodes: builder.mutation<RecoveryCodesResponse, { password: string }>({
      query: (body) => ({
        url: '/auth/mfa/backup-codes/regenerate',
        method: 'POST',
        body,
      }),
    }),

    // Complete MFA login
    completeMfaLogin: builder.mutation<
      LoginResponse,
      {
        session_token: string
        code: string
        method: 'totp' | 'email' | 'backup'
      }
    >({
      query: (body) => ({
        url: '/auth/local/login/complete',
        method: 'POST',
        body,
      }),
    }),
  }),
})

export const {
  useGetMfaStatusQuery,
  useSetupTotpMutation,
  useVerifyTotpMutation,
  useSetupEmailOtpMutation,
  useDisableMfaMethodMutation,
  useGetBackupCodesQuery,
  useGenerateBackupCodesMutation,
  useCompleteMfaLoginMutation,
} = mfaApi
