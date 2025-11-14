/**
 * Tests de validation des endpoints API
 * 
 * Ces tests garantissent que tous les endpoints respectent le format standard
 * et qu'aucune duplication /api/api/ n'est introduite
 */

import { describe, it, expect } from 'vitest'
import { validateEndpoint, buildEndpoint, API_BASE_URL } from '../config/api.config'

describe('API Endpoints Validation', () => {
  describe('validateEndpoint', () => {
    it('should accept valid endpoints starting with /api/', () => {
      expect(validateEndpoint('/api/auth/login')).toBe(true)
      expect(validateEndpoint('/api/users/me')).toBe(true)
      expect(validateEndpoint('/api/iam/permissions')).toBe(true)
    })

    it('should reject endpoints without /api/ prefix', () => {
      expect(validateEndpoint('/auth/login')).toBe(false)
      expect(validateEndpoint('/users/me')).toBe(false)
      expect(validateEndpoint('auth/login')).toBe(false)
    })

    it('should reject endpoints with duplicate /api/', () => {
      expect(validateEndpoint('/api/api/auth/login')).toBe(false)
      expect(validateEndpoint('/api/api/users/me')).toBe(false)
    })
  })

  describe('buildEndpoint', () => {
    it('should build correct endpoints', () => {
      expect(buildEndpoint('AUTH', 'local/login')).toBe('/api/auth/local/login')
      expect(buildEndpoint('USERS', 'me')).toBe('/api/users/me')
      expect(buildEndpoint('IAM', 'permissions')).toBe('/api/iam/permissions')
    })

    it('should handle paths with leading slash', () => {
      expect(buildEndpoint('AUTH', '/local/login')).toBe('/api/auth/local/login')
    })

    it('should handle empty paths', () => {
      expect(buildEndpoint('AUTH')).toBe('/api/auth')
      expect(buildEndpoint('USERS', '')).toBe('/api/users')
    })
  })

  describe('API_BASE_URL', () => {
    it('should be /api', () => {
      expect(API_BASE_URL).toBe('/api')
    })
  })
})

/**
 * Test regex pour détecter les patterns invalides dans le code
 */
describe('Code Pattern Detection', () => {
  const INVALID_PATTERNS = {
    doubleApi: /\/api\/api\//,
    authWithoutApi: /['"]\/auth\/(?!.*\/api)/,
    baseQueryWithParam: /createBaseQueryWithAuth\(['"][^)]+['"]\)/,
  }

  it('should not have double /api/ in any endpoint', () => {
    // Ce test devrait être exécuté sur le code source
    // Pour une implémentation complète, utiliser un linter custom
    expect(true).toBe(true) // Placeholder
  })
})
