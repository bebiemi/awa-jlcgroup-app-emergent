/**
 * useFeatureFlag Hook
 * Check if a feature flag is enabled for the current user
 * 
 * Usage:
 * const { isEnabled, isLoading } = useFeatureFlag('feature.ai.matching')
 * 
 * if (isEnabled) {
 *   // Show feature
 * }
 */
import React, { useState, useEffect } from 'react'
import { useAppSelector } from '@/store/hooks'

interface FeatureFlagResult {
  isEnabled: boolean
  isLoading: boolean
  error: string | null
}

export function useFeatureFlag(flagKey: string): FeatureFlagResult {
  const [isEnabled, setIsEnabled] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { user } = useAppSelector((state) => state.auth)

  useEffect(() => {
    const checkFlag = async () => {
      if (!user) {
        setIsEnabled(false)
        setIsLoading(false)
        return
      }

      try {
        const token = localStorage.getItem('access_token')
        const response = await fetch(`/api/feature-flags/check/${flagKey}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        })

        if (response.ok) {
          const data = await response.json()
          setIsEnabled(data.enabled)
        } else {
          setIsEnabled(false)
          setError('Failed to check feature flag')
        }
      } catch (err) {
        console.error('Error checking feature flag:', err)
        setIsEnabled(false)
        setError('Network error')
      } finally {
        setIsLoading(false)
      }
    }

    checkFlag()
  }, [flagKey, user])

  return { isEnabled, isLoading, error }
}

/**
 * useFeatureFlags Hook
 * Check multiple feature flags at once
 * 
 * Usage:
 * const flags = useFeatureFlags(['feature.ai.matching', 'feature.chat.messaging'])
 * 
 * if (flags['feature.ai.matching']) {
 *   // Show AI matching
 * }
 */
export function useFeatureFlags(flagKeys: string[]): Record<string, boolean> {
  const [flags, setFlags] = useState<Record<string, boolean>>({})
  const { user } = useAppSelector((state) => state.auth)

  useEffect(() => {
    const checkFlags = async () => {
      if (!user || flagKeys.length === 0) {
        setFlags({})
        return
      }

      const token = localStorage.getItem('access_token')
      const results: Record<string, boolean> = {}

      await Promise.all(
        flagKeys.map(async (key) => {
          try {
            const response = await fetch(`/api/feature-flags/check/${key}`, {
              headers: {
                'Authorization': `Bearer ${token}`,
              },
            })

            if (response.ok) {
              const data = await response.json()
              results[key] = data.enabled
            } else {
              results[key] = false
            }
          } catch (err) {
            console.error(`Error checking flag ${key}:`, err)
            results[key] = false
          }
        })
      )

      setFlags(results)
    }

    checkFlags()
  }, [flagKeys.join(','), user])

  return flags
}

/**
 * FeatureGate Component
 * Conditionally render children based on feature flag
 * 
 * Usage:
 * <FeatureGate flag="feature.ai.matching">
 *   <AIMatchingButton />
 * </FeatureGate>
 */
export function FeatureGate({ 
  flag, 
  children, 
  fallback = null 
}: { 
  flag: string
  children: React.ReactNode
  fallback?: React.ReactNode
}): React.ReactElement | null {
  const { isEnabled, isLoading } = useFeatureFlag(flag)

  if (isLoading) {
    return null
  }

  return isEnabled ? <>{children}</> : <>{fallback}</>
}
