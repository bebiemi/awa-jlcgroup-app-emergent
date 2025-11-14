import { fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import type { BaseQueryFn, FetchArgs, FetchBaseQueryError } from '@reduxjs/toolkit/query/react'
import { logoutAction } from '@/features/auth/slices/authSlice'

/**
 * Base query with automatic 401 handling
 * Logs out user and redirects to login on authentication failure
 * 
 * IMPORTANT: Ne PAS passer de baseUrl en paramètre !
 * Le baseUrl doit toujours être /api (configuration globale)
 * Les endpoints doivent être des chemins relatifs sans /api
 */
export const createBaseQueryWithAuth = (): BaseQueryFn<
  string | FetchArgs,
  unknown,
  FetchBaseQueryError
> => {
  // Custom fetch function that fixes Mixed Content in production/preview environments
  const customFetch: typeof fetch = async (input, init) => {
    let url = typeof input === 'string' ? input : input.url
    
    // Validation en développement
    if (process.env.NODE_ENV === 'development' && url.includes('/api/api/')) {
      console.error('❌ INVALID ENDPOINT: Duplicate /api/ detected:', url)
    }
    
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
    
    // Call native fetch with corrected URL
    // IMPORTANT: Si input est une string, passer url et init tels quels
    // Si input est un Request, il faut recréer le Request avec la nouvelle URL
    if (typeof input === 'string') {
      return fetch(url, init)
    } else {
      // Créer un nouveau Request en préservant TOUS les attributs (body, headers, method, etc.)
      const newRequest = new Request(url, input)
      return fetch(newRequest, init)
    }
  }
  
  const baseQuery = fetchBaseQuery({
    baseUrl: '/api',  // TOUJOURS /api - pas de paramètre
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

/**
 * Instance par défaut de baseQuery avec authentification
 * Utilise toujours /api comme baseUrl
 * 
 * Usage dans vos API:
 * ```
 * export const myApi = createApi({
 *   reducerPath: 'myApi',
 *   baseQuery: createBaseQueryWithAuth(),  // ← Pas de paramètre !
 *   endpoints: (builder) => ({
 *     getData: builder.query({
 *       query: () => '/users/me',  // ← Chemin relatif sans /api
 *     }),
 *   }),
 * })
 * ```
 */
export const baseQueryWithAuth = createBaseQueryWithAuth()
