import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import type { MfaStatus, TOTPSetupResponse, RecoveryCodesResponse, LoginResponse } from '@/types'
import type { RootState } from '@/store/store'

const AUTH_SERVICE_URL = '/auth-api'

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
        url: '/auth/mfa/verify/totp',
        method: 'POST',
        body,
      }),
    }),

    // Setup Email OTP
    setupEmailOtp: builder.mutation<{ success: boolean; message: string; email: string }, void>({
      query: () => ({
        url: '/auth/mfa/setup/email',
        method: 'POST',
      }),
    }),

    // Enable MFA
    enableMfa: builder.mutation<{ success: boolean; message: string; method: string }, { method: 'totp' | 'email' }>({
      query: (body) => ({
        url: '/auth/mfa/enable',
        method: 'POST',
        body,
      }),
      invalidatesTags: ['MfaStatus'],
    }),

    // Disable MFA
    disableMfa: builder.mutation<{ success: boolean; message: string }, { password: string }>({
      query: (body) => ({
        url: '/auth/mfa/disable',
        method: 'POST',
        body,
      }),
      invalidatesTags: ['MfaStatus'],
    }),

    // Get recovery codes
    getRecoveryCodes: builder.query<RecoveryCodesResponse, void>({
      query: () => '/auth/mfa/recovery-codes',
    }),

    // Generate new recovery codes
    generateRecoveryCodes: builder.mutation<RecoveryCodesResponse, { password: string }>({
      query: (body) => ({
        url: '/auth/mfa/recovery-codes/generate',
        method: 'POST',
        body,
      }),
    }),

    // Complete MFA login
    completeMfaLogin: builder.mutation<
      LoginResponse,
      {
        session_id: string
        code: string
        code_type: 'totp' | 'email' | 'recovery'
      }
    >({
      query: (body) => ({
        url: '/auth/local/login/complete-mfa',
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
  useEnableMfaMutation,
  useDisableMfaMutation,
  useGetRecoveryCodesQuery,
  useGenerateRecoveryCodesMutation,
  useCompleteMfaLoginMutation,
} = mfaApi
