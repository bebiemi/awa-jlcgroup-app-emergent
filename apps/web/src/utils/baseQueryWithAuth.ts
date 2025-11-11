import { fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import type { BaseQueryFn, FetchArgs, FetchBaseQueryError } from '@reduxjs/toolkit/query/react'
import { logoutAction } from '@/features/auth/slices/authSlice'

/**
 * Base query with automatic 401 handling
 * Logs out user and redirects to login on authentication failure
 */
export const createBaseQueryWithAuth = (baseUrl?: string): BaseQueryFn<
  string | FetchArgs,
  unknown,
  FetchBaseQueryError
> => {
  const baseQuery = fetchBaseQuery({
    // Use '/api' as baseUrl to create truly relative URLs
    // This inherits the page protocol (HTTP in dev, HTTPS in preview)
    baseUrl: baseUrl || '/api',
    prepareHeaders: (headers) => {
      const token = localStorage.getItem('access_token')
      if (token) {
        headers.set('Authorization', `Bearer ${token}`)
      }
      return headers
    },
  })

  return async (args, api, extraOptions) => {
    const result = await baseQuery(args, api, extraOptions)

    // Handle 401 Unauthorized - Session expired or invalid token
    if (result.error && result.error.status === 401) {
      console.error('🚨 401 Unauthorized - Session expired, logging out...')
      
      // Clear all API caches
      api.dispatch({ type: 'presenceApi/resetApiState' })
      api.dispatch({ type: 'api/resetApiState' })
      
      // Logout user
      api.dispatch(logoutAction())
      
      // Redirect to login (will be handled by App component)
      window.location.href = '/login'
      
      // Return error without retry
      return result
    }

    return result
  }
}

// Default instance with backend URL from environment
// CRITICAL: ALWAYS use undefined to force truly relative URLs
// This prevents Mixed Content errors in production (HTTPS pages making HTTP requests)
// SOLUTION: Always use undefined to ensure relative URLs work in all environments
export const baseQueryWithAuth = createBaseQueryWithAuth(undefined)
