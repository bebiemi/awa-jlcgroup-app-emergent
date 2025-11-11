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
    baseUrl: baseUrl || '',  // Empty string to force relative URLs
    prepareHeaders: (headers) => {
      const token = localStorage.getItem('access_token')
      if (token) {
        headers.set('Authorization', `Bearer ${token}`)
      }
      return headers
    },
  })

  return async (args, api, extraOptions) => {
    // Force relative URLs by ensuring no absolute URLs are passed
    let modifiedArgs = args
    if (typeof args === 'string') {
      // Already relative
      modifiedArgs = args
    } else if (typeof args === 'object' && 'url' in args) {
      // Ensure URL is relative
      const url = args.url || ''
      if (url.startsWith('http://') || url.startsWith('https://')) {
        // Extract just the path from absolute URLs
        try {
          const urlObj = new URL(url)
          modifiedArgs = { ...args, url: urlObj.pathname + urlObj.search }
        } catch (e) {
          // If URL parsing fails, use as is
          modifiedArgs = args
        }
      } else {
        modifiedArgs = args
      }
    }
    
    const result = await baseQuery(modifiedArgs, api, extraOptions)

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

// Default instance with empty string to force relative URLs
// CRITICAL: Empty string ensures all URLs are relative to current origin
// This prevents Mixed Content errors in production (HTTPS pages making HTTP requests)
// In development: Vite proxy handles routing (/api/* → correct service)
// In production: Kubernetes/nginx handles routing based on path
export const baseQueryWithAuth = createBaseQueryWithAuth('')
