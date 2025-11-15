/**
 * App Configuration API
 * RTK Query API for dynamic application configuration
 */
import { createApi } from '@reduxjs/toolkit/query/react'
import { baseQueryWithAuth } from '@/utils/baseQueryWithAuth'

export interface AppConfig {
  key: string
  value: any
  category: string
  description: string
  updated_at: string
  updated_by: string
}

export interface BadgeConfig {
  enabled: boolean
  expiration_days: number
  expiration_mode: 'first_view' | 'creation_date' | 'both'
  badge_text: {
    fr: string
    en: string
  }
}

export interface DocumentCategory {
  id: string
  name: {
    fr: string
    en: string
  }
  required: boolean
  expirable: boolean
  expiration_reminder_days?: number[]
  retention_years: number | null
  allowed_formats: string[]
  max_size_mb: number
  required_for_roles: string[]
}

export interface NotificationType {
  enabled: boolean
  channels: string[]
  template: string
  reminder_days?: number[]
  min_match_score?: number
}

export interface DashboardWidget {
  enabled: boolean
  priority: number
  max_items?: number
  roles: string[]
}

export const appConfigApi = createApi({
  reducerPath: 'appConfigApi',
  baseQuery: baseQueryWithAuth,
  tagTypes: ['AppConfig'],
  endpoints: (builder) => ({
    // Get config by key
    getConfig: builder.query<AppConfig, string>({
      query: (key) => `/config/app?key=${key}`,
      providesTags: (result, error, key) => [{ type: 'AppConfig', id: key }],
    }),

    // Get config value directly
    getConfigValue: builder.query<any, string>({
      query: (key) => `/config/app/value?key=${key}`,
      transformResponse: (response: { value: any }) => response.value,
      providesTags: (result, error, key) => [{ type: 'AppConfig', id: key }],
    }),

    // Get configs by category
    getConfigsByCategory: builder.query<AppConfig[], string>({
      query: (category) => `/config/app?category=${category}`,
      transformResponse: (response: { configs: AppConfig[] }) => response.configs,
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ key }) => ({ type: 'AppConfig' as const, id: key })),
              { type: 'AppConfig', id: 'LIST' },
            ]
          : [{ type: 'AppConfig', id: 'LIST' }],
    }),

    // Get all configs
    getAllConfigs: builder.query<AppConfig[], void>({
      query: () => `/config/app`,
      transformResponse: (response: { configs: AppConfig[] }) => response.configs,
      providesTags: [{ type: 'AppConfig', id: 'LIST' }],
    }),

    // Get categories
    getCategories: builder.query<string[], void>({
      query: () => `/config/app/categories`,
      transformResponse: (response: { categories: string[] }) => response.categories,
    }),

    // Update config (admin)
    updateConfig: builder.mutation<void, { key: string; value: any; description?: string }>({
      query: ({ key, value, description }) => ({
        url: `/config/app/${key}`,
        method: 'PATCH',
        body: { value, description },
      }),
      invalidatesTags: (result, error, { key }) => [{ type: 'AppConfig', id: key }],
    }),

    // Create config (admin)
    createConfig: builder.mutation<
      void,
      { key: string; value: any; category: string; description?: string }
    >({
      query: (body) => ({
        url: `/config/app`,
        method: 'POST',
        body,
      }),
      invalidatesTags: [{ type: 'AppConfig', id: 'LIST' }],
    }),

    // Delete config (admin)
    deleteConfig: builder.mutation<void, string>({
      query: (key) => ({
        url: `/config/app/${key}`,
        method: 'DELETE',
      }),
      invalidatesTags: (result, error, key) => [
        { type: 'AppConfig', id: key },
        { type: 'AppConfig', id: 'LIST' },
      ],
    }),
  }),
})

export const {
  useGetConfigQuery,
  useGetConfigValueQuery,
  useGetConfigsByCategoryQuery,
  useGetAllConfigsQuery,
  useGetCategoriesQuery,
  useUpdateConfigMutation,
  useCreateConfigMutation,
  useDeleteConfigMutation,
} = appConfigApi

// Typed hooks for specific configs
export const useBadgeConfig = () => {
  return useGetConfigValueQuery('profiles.badge_new_user') as {
    data: BadgeConfig | undefined
    isLoading: boolean
    error: any
  }
}

export const useDocumentCategories = () => {
  return useGetConfigValueQuery('documents.categories') as {
    data: DocumentCategory[] | undefined
    isLoading: boolean
    error: any
  }
}

export const useNotificationTypes = () => {
  return useGetConfigValueQuery('notifications.types') as {
    data: Record<string, NotificationType> | undefined
    isLoading: boolean
    error: any
  }
}

export const useDashboardWidgets = () => {
  return useGetConfigValueQuery('dashboard.widgets') as {
    data: Record<string, DashboardWidget> | undefined
    isLoading: boolean
    error: any
  }
}
