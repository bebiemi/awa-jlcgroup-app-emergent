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
    baseUrl: baseUrl || undefined,
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
// CRITICAL: Leave undefined to force truly relative URLs (no protocol, no domain)
// This prevents Mixed Content errors in production (HTTPS pages making HTTP requests)
const getBaseUrl = (): string | undefined => {
  const envUrl = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL
  
  // If env URL is set and not empty, use it (for local dev with specific ports)
  if (envUrl && envUrl.trim() !== '') {
    return envUrl
  }
  
  // In production: return undefined to force relative URLs
  // RTK Query will use relative paths like /api/config/countries
  // which will automatically use the same protocol as the page (HTTPS)
  return undefined
}

const backendUrl = getBaseUrl()
export const baseQueryWithAuth = createBaseQueryWithAuth(backendUrl)
