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
  // Fix Mixed Content issue: If page is HTTPS, ensure API calls are also HTTPS
  // In production/preview (HTTPS), force relative URLs to use same protocol
  let finalBaseUrl = baseUrl || undefined
  
  // If we're on HTTPS and no baseUrl is specified, ensure relative URLs work
  if (typeof window !== 'undefined' && window.location.protocol === 'https:' && !finalBaseUrl) {
    // Use relative URLs - browser will automatically use HTTPS
    finalBaseUrl = undefined
  }
  
  const baseQuery = fetchBaseQuery({
    baseUrl: finalBaseUrl,
    prepareHeaders: (headers) => {
      const token = localStorage.getItem('access_token')
      if (token) {
        headers.set('Authorization', `Bearer ${token}`)
      }
      return headers
    },
  })

  return async (args, api, extraOptions) => {
    // Fix Mixed Content: Ensure URLs use correct protocol
    let modifiedArgs = args
    if (typeof args === 'object' && 'url' in args && typeof args.url === 'string') {
      // If URL is absolute HTTP and we're on HTTPS, convert to relative
      if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
        if (args.url.startsWith('http://')) {
          // Convert to relative URL
          const url = new URL(args.url)
          modifiedArgs = { ...args, url: url.pathname + url.search }
          console.log('🔒 Fixed Mixed Content:', args.url, '→', modifiedArgs.url)
        }
      }
    } else if (typeof args === 'string' && args.startsWith('http://')) {
      // String URL case
      if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
        const url = new URL(args)
        modifiedArgs = url.pathname + url.search
        console.log('🔒 Fixed Mixed Content:', args, '→', modifiedArgs)
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

// Default instance with backend URL from environment
// CRITICAL: ALWAYS use undefined to force truly relative URLs
// This prevents Mixed Content errors in production (HTTPS pages making HTTP requests)
// SOLUTION: Always use undefined to ensure relative URLs work in all environments
export const baseQueryWithAuth = createBaseQueryWithAuth(undefined)
