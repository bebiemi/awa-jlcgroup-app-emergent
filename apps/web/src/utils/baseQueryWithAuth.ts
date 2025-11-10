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
// CRITICAL: ALWAYS use undefined to force truly relative URLs
// This prevents Mixed Content errors in production (HTTPS pages making HTTP requests)
// Even if environment variables are set, we ignore them to ensure relative URLs
const getBaseUrl = (): string | undefined => {
  // Check if we're in a production build (*.preview.emergentagent.com or similar)
  const isProduction = typeof window !== 'undefined' && 
    (window.location.hostname.includes('preview.emergentagent.com') ||
     window.location.hostname.includes('emergentagent.com') ||
     window.location.protocol === 'https:')
  
  // In production: ALWAYS return undefined to force relative URLs
  // This ensures HTTPS pages make HTTPS requests automatically
  if (isProduction) {
    return undefined
  }
  
  // In development: check environment variables (for custom ports if needed)
  const envUrl = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL
  
  // If env URL is set, not empty, and not an HTTP URL, use it
  if (envUrl && envUrl.trim() !== '' && !envUrl.startsWith('http://')) {
    return envUrl
  }
  
  // Default: return undefined for relative URLs
  return undefined
}

const backendUrl = getBaseUrl()
export const baseQueryWithAuth = createBaseQueryWithAuth(backendUrl)
