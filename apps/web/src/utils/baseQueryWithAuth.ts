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
  // Custom fetch function that fixes Mixed Content in production/preview environments
  const customFetch: typeof fetch = async (input, init) => {
    let url = typeof input === 'string' ? input : input.url
    
    // Only apply HTTP → HTTPS conversion in production/preview environments (not local Docker)
    if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
      const hostname = window.location.hostname
      const isEmergentPreview = hostname.includes('preview.emergentagent.com') || hostname.includes('emergent.host')
      
      // Only convert HTTP to HTTPS in Emergent preview environments
      if (isEmergentPreview && url.startsWith('http://')) {
        url = url.replace('http://', 'https://')
        console.log('🔒 Fixed Mixed Content URL for Emergent:', url)
      }
    }
    
    // Call native fetch with corrected URL (or original if no conversion needed)
    const modifiedInput = typeof input === 'string' ? url : new Request(url, input)
    return fetch(modifiedInput, init)
  }
  
  const baseQuery = fetchBaseQuery({
    baseUrl: baseUrl === undefined ? '/api' : baseUrl,
    fetchFn: customFetch,
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
