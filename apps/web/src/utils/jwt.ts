/**
 * JWT utility functions
 * Handles JWT decoding and permission extraction
 */

interface JWTPayload {
  sub: string  // User ID
  email: string
  roles: string[]
  permissions?: string[]
  session_id: string
  exp: number
  iat: number
  type: string
}

/**
 * Decode JWT token and extract payload
 * @param token - JWT token string
 * @returns Decoded payload or null if invalid
 */
export function decodeJWT(token: string): JWTPayload | null {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) {
      console.error('Invalid JWT format')
      return null
    }

    // Decode the payload (part 1)
    const payload = parts[1]
    // Add padding if needed
    const paddedPayload = payload + '='.repeat((4 - (payload.length % 4)) % 4)
    
    // Decode base64
    const decoded = atob(paddedPayload)
    const payloadData = JSON.parse(decoded) as JWTPayload
    
    return payloadData
  } catch (error) {
    console.error('Failed to decode JWT:', error)
    return null
  }
}

/**
 * Extract permissions from JWT token
 * @param token - JWT token string
 * @returns Array of permission codes or empty array if invalid
 */
export function extractPermissionsFromJWT(token: string): string[] {
  const payload = decodeJWT(token)
  return payload?.permissions || []
}

/**
 * Check if JWT token is expired
 * @param token - JWT token string
 * @returns true if expired, false otherwise
 */
export function isJWTExpired(token: string): boolean {
  const payload = decodeJWT(token)
  if (!payload || !payload.exp) return true
  
  const currentTime = Math.floor(Date.now() / 1000)
  return currentTime > payload.exp
}
