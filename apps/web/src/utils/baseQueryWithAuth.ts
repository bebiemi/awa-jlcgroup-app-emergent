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
  const baseQuery = fetchBaseQuery({
    baseUrl: '/api',  // TOUJOURS /api - pas de paramètre
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
