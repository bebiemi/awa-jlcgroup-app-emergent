/**
 * Configuration globale des APIs
 * 
 * Ce fichier centralise TOUTE la configuration des endpoints API.
 * Il garantit l'uniformité et empêche les duplications /api/api/...
 * 
 * RÈGLE : Tous les endpoints doivent suivre le format /api/<service>/<resource>
 */

/**
 * URL de base de l'API
 * En production/preview: URLs relatives via ingress
 * En développement local: URLs relatives via proxy Vite
 */
export const API_BASE_URL = '/api' as const

/**
 * Services disponibles
 * Utilisés pour construire des endpoints typés et validés
 */
export const API_SERVICES = {
  AUTH: 'auth',
  IAM: 'iam',
  USERS: 'users',
  PROFILES: 'profiles',
  SECURITY: 'security',
  EMAILS: 'emails',
  CONFIG: 'auth/config',  // Exception: config sous auth
  BESOINS: 'besoins',
  ENTREPRISES: 'entreprises',
  MISSIONS: 'missions',
  CONTRACTS: 'contracts',
  APPLICATIONS: 'applications',
  VALIDATIONS: 'validations',
  NOTIFICATIONS: 'notifications',
  LOCATIONS: 'locations',
  FEATURE_FLAGS: 'feature-flags',
  VERSIONS: 'versions',
} as const

/**
 * Helper pour construire des endpoints typés
 * Usage: buildEndpoint('auth', 'local/login') → '/api/auth/local/login'
 */
export function buildEndpoint(service: keyof typeof API_SERVICES, path: string = ''): string {
  const servicePath = API_SERVICES[service]
  const cleanPath = path.startsWith('/') ? path.slice(1) : path
  return cleanPath ? `${API_BASE_URL}/${servicePath}/${cleanPath}` : `${API_BASE_URL}/${servicePath}`
}

/**
 * Validation d'endpoint
 * Vérifie qu'un endpoint suit le format correct
 */
export function validateEndpoint(endpoint: string): boolean {
  // Doit commencer par /api/
  if (!endpoint.startsWith('/api/')) {
    console.error(`❌ Invalid endpoint: "${endpoint}" - Must start with /api/`)
    return false
  }
  
  // Ne doit pas contenir /api/api/
  if (endpoint.includes('/api/api/')) {
    console.error(`❌ Invalid endpoint: "${endpoint}" - Contains duplicate /api/`)
    return false
  }
  
  return true
}

/**
 * Configuration pour createBaseQueryWithAuth
 * À utiliser dans tous les createApi()
 */
export const BASE_QUERY_CONFIG = {
  baseUrl: API_BASE_URL,
  validateEndpoints: process.env.NODE_ENV === 'development',
} as const
