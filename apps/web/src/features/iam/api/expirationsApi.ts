/**
 * API Client pour les Expirations de Profils
 */
import { createApi } from '@reduxjs/toolkit/query/react';
import { baseQueryWithAuth } from '@/utils/baseQueryWithAuth';

export interface TemporaryProfile {
  profile_id: string;
  assigned_at: string;
  expires_at: string;
  reason?: string;
  notified_at?: string;
  is_expired: boolean;
  days_until_expiration: number;
}

export interface ExpirationCheck {
  user_id: string;
  username: string;
  email: string;
  expired_count: number;
  expiring_soon_count: number;
  expired_profiles: TemporaryProfile[];
  expiring_soon: TemporaryProfile[];
  downgrade_to_profile_id: string;
}

export interface ExpirationStats {
  total_users_checked: number;
  users_with_expiring: number;
  total_expired: number;
  total_expiring_soon: number;
  last_check: string;
}

export const expirationsApi = createApi({
  reducerPath: 'expirationsApi',
  baseQuery: baseQueryWithAuth,
  tagTypes: ['Expirations', 'ExpirationStats'],
  endpoints: (builder) => ({
    // Vérifier mes expirations
    checkMyExpirations: builder.query<ExpirationCheck, void>({
      query: () => '/iam/expirations/check/me',
      providesTags: ['Expirations'],
    }),

    // Vérifier expirations d'un utilisateur
    checkUserExpirations: builder.query<ExpirationCheck, string>({
      query: (userId) => `/iam/expirations/check/${userId}`,
      providesTags: ['Expirations'],
    }),

    // Vérifier toutes les expirations
    checkAllExpirations: builder.query<ExpirationCheck[], void>({
      query: () => '/iam/expirations/check/all',
      providesTags: ['Expirations'],
    }),

    // Traiter les expirations (downgrade auto)
    processExpirations: builder.mutation<any, void>({
      query: () => ({
        url: '/iam/expirations/process',
        method: 'POST',
      }),
      invalidatesTags: ['Expirations', 'ExpirationStats'],
    }),

    // Envoyer les notifications
    sendNotifications: builder.mutation<any, void>({
      query: () => ({
        url: '/iam/expirations/notify',
        method: 'POST',
      }),
    }),

    // Statistiques d'expiration
    getExpirationStats: builder.query<ExpirationStats, void>({
      query: () => '/iam/expirations/stats',
      providesTags: ['ExpirationStats'],
    }),

    // Downgrade manuel d'un profil
    manualDowngrade: builder.mutation<any, { userId: string; profileId: string }>({
      query: ({ userId, profileId }) => ({
        url: `/iam/expirations/downgrade/${userId}/${profileId}`,
        method: 'POST',
      }),
      invalidatesTags: ['Expirations', 'ExpirationStats'],
    }),
  }),
});

export const {
  useCheckMyExpirationsQuery,
  useCheckUserExpirationsQuery,
  useCheckAllExpirationsQuery,
  useProcessExpirationsMutation,
  useSendNotificationsMutation,
  useGetExpirationStatsQuery,
  useManualDowngradeMutation,
} = expirationsApi;
