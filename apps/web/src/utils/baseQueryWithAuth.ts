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
  // Custom fetch pour corriger Mixed Content sur Emergent (HTTPS uniquement)
  const customFetch: typeof fetch = async (input, init) => {
    // Validation en développement
    const url = typeof input === 'string' ? input : input.url
    
    // Normalisation des anciennes routes IAM (fallback safe)
    if (url.includes('/api/permissions')) {
      const normalizedUrl = url.replace('/api/permissions', '/api/iam/permissions')
      if (process.env.NODE_ENV === 'development') {
        console.warn('🔁 Normalized legacy IAM permissions route ->', normalizedUrl)
      }
      if (typeof input === 'string') {
        return fetch(normalizedUrl, init)
      } else {
        const req = input as Request
        const reqInit: RequestInit = {
          method: req.method,
          headers: req.headers,
          body: req.body,
          mode: req.mode,
          credentials: req.credentials,
          cache: req.cache,
          redirect: req.redirect,
          referrer: req.referrer,
          integrity: req.integrity,
        }
        return fetch(normalizedUrl, { ...reqInit, ...init })
      }
    }

    // Normalisation config: certains appels peuvent cibler /api/auth/config/... au lieu de /api/config/...
    if (url.includes('/api/auth/config/')) {
      const normalizedUrl = url.replace('/api/auth/config/', '/api/config/')
      if (process.env.NODE_ENV === 'development') {
        console.warn('🔁 Normalized config route ->', normalizedUrl)
      }
      if (typeof input === 'string') {
        return fetch(normalizedUrl, init)
      } else {
        const req = input as Request
        const reqInit: RequestInit = {
          method: req.method,
          headers: req.headers,
          body: req.body,
          mode: req.mode,
          credentials: req.credentials,
          cache: req.cache,
          redirect: req.redirect,
          referrer: req.referrer,
          integrity: req.integrity,
        }
        return fetch(normalizedUrl, { ...reqInit, ...init })
      }
    }

    // Normalisation des routes IAM users (archive/suppressions) : /api/auth/iam/users -> /api/iam/users
    if (url.includes('/api/auth/iam/users/')) {
      const normalizedUrl = url.replace('/api/auth/iam/users/', '/api/iam/users/')
      if (process.env.NODE_ENV === 'development') {
        console.warn('🔁 Normalized IAM users route ->', normalizedUrl)
      }
      if (typeof input === 'string') {
        return fetch(normalizedUrl, init)
      } else {
        const req = input as Request
        const reqInit: RequestInit = {
          method: req.method,
          headers: req.headers,
          body: req.body,
          mode: req.mode,
          credentials: req.credentials,
          cache: req.cache,
          redirect: req.redirect,
          referrer: req.referrer,
          integrity: req.integrity,
        }
        return fetch(normalizedUrl, { ...reqInit, ...init })
      }
    }
    if (process.env.NODE_ENV === 'development' && url.includes('/api/api/')) {
      console.error('❌ INVALID ENDPOINT: Duplicate /api/ detected:', url)
    }
    
    // Conversion HTTP → HTTPS uniquement sur Emergent preview (HTTPS)
    if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
      const hostname = window.location.hostname
      const isEmergentPreview = hostname.includes('preview.emergentagent.com') || hostname.includes('emergent.host')
      
      if (isEmergentPreview && url.startsWith('http://')) {
        const httpsUrl = url.replace('http://', 'https://')
        console.log('🔒 Fixed Mixed Content URL:', httpsUrl)
        
        // IMPORTANT: Reconstruire correctement la requête avec HTTPS
        if (typeof input === 'string') {
          return fetch(httpsUrl, init)
        } else {
          // Pour un Request object, extraire toutes les propriétés et créer un nouveau Request
          // Cette approche garantit que le body et tous les headers sont préservés
          const originalRequest = input as Request
          const requestInit: RequestInit = {
            method: originalRequest.method,
            headers: originalRequest.headers,
            body: originalRequest.body,
            mode: originalRequest.mode,
            credentials: originalRequest.credentials,
            cache: originalRequest.cache,
            redirect: originalRequest.redirect,
            referrer: originalRequest.referrer,
            integrity: originalRequest.integrity,
          }
          return fetch(httpsUrl, { ...requestInit, ...init })
        }
      }
    }
    
    // Si aucun token (non authentifié), rediriger /api/config/all vers /api/config/public (public minimal)
    const hasToken = typeof window !== 'undefined' && localStorage.getItem('access_token')
    if (!hasToken) {
      const normalizedConfigPublic = url.replace('/api/config/all', '/api/config/public')
      if (normalizedConfigPublic !== url && process.env.NODE_ENV === 'development') {
        console.warn('🔁 Using public config endpoint (no token):', normalizedConfigPublic)
      }
      input = typeof input === 'string' ? normalizedConfigPublic : new Request(normalizedConfigPublic, input as RequestInit)
    }

    // Pas de conversion nécessaire : utiliser fetch natif
    return fetch(input, init)
  }
  
  // Déterminer le baseUrl en fonction de l'environnement
  // Sur Emergent preview (HTTPS), forcer HTTPS pour éviter Mixed Content
  const getBaseUrl = () => {
    if (typeof window === 'undefined') return '/api'
    
    const isHTTPS = window.location.protocol === 'https:'
    const hostname = window.location.hostname
    const isEmergentPreview = hostname.includes('preview.emergentagent.com') || hostname.includes('emergent.host')
    
    if (isHTTPS && isEmergentPreview) {
      // Forcer HTTPS pour éviter Mixed Content
      const httpsBaseUrl = `https://${hostname}/api`
      console.log('🔒 Emergent Preview detected - Using HTTPS baseUrl:', httpsBaseUrl)
      return httpsBaseUrl
    }
    
    // Développement local ou autre environnement : utiliser URL relative
    return '/api'
  }
  
  const baseQuery = fetchBaseQuery({
    baseUrl: getBaseUrl(),
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
      const argUrl = typeof args === 'string' ? args : (args as FetchArgs).url
      // Cas spécial: fallback public pour /config/all
      if (argUrl && argUrl.toString().includes('/config/all')) {
        const publicArgs =
          typeof args === 'string'
            ? args.replace('/config/all', '/config/public')
            : {
                ...(args as FetchArgs),
                url: (args as FetchArgs).url?.toString().replace('/config/all', '/config/public'),
              }
        if (process.env.NODE_ENV === 'development') {
          console.warn('🔁 401 on /config/all -> retry /config/public')
        }
        const retry = await baseQuery(publicArgs, api, extraOptions)
        return retry
      }

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
