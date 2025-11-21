/**
 * Hook pour gérer les préférences UI utilisateur
 * Sync entre localStorage et API backend
 */

import { useState, useEffect, useCallback } from 'react'
import { useAppSelector } from '@/store/hooks'

interface UIPreferences {
  sidebar_style: 'v2' | 'v3'
}

// Utiliser une URL relative (vide) pour que Vite proxy/production routing fonctionne
const API_BASE = import.meta.env.VITE_BACKEND_URL || ''

export function useUIPreferences() {
  const { isAuthenticated } = useAppSelector((state) => state.auth)
  const [preferences, setPreferences] = useState<UIPreferences>({
    sidebar_style: 'v2'
  })
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Charger les préférences au montage
  useEffect(() => {
    const loadPreferences = async () => {
      if (!isAuthenticated) {
        // Non authentifié : charger depuis localStorage
        const localStyle = localStorage.getItem('sidebar_style') as 'v2' | 'v3' | null
        if (localStyle) {
          setPreferences({ sidebar_style: localStyle })
        }
        setIsLoading(false)
        return
      }

      try {
        // Authentifié : charger depuis l'API
        const token = localStorage.getItem('access_token')
        if (!token) {
          // Pas de token : fallback localStorage
          const localStyle = localStorage.getItem('sidebar_style') as 'v2' | 'v3' | null
          if (localStyle) {
            setPreferences({ sidebar_style: localStyle })
          }
          setIsLoading(false)
          return
        }

        const response = await fetch(`${API_BASE}/api/auth/users/me/preferences`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        })

        if (response.ok) {
          const data = await response.json()
          const apiPrefs: UIPreferences = {
            sidebar_style: data.ui_preferences?.sidebar_style || 'v2'
          }
          setPreferences(apiPrefs)
          // Sync avec localStorage
          localStorage.setItem('sidebar_style', apiPrefs.sidebar_style)
        } else {
          // Fallback sur localStorage si l'API échoue
          console.warn(`API preferences failed with status ${response.status}, using localStorage fallback`)
          const localStyle = localStorage.getItem('sidebar_style') as 'v2' | 'v3' | null
          if (localStyle) {
            setPreferences({ sidebar_style: localStyle })
          }
        }
      } catch (err) {
        // Fallback silencieux sur localStorage pour ne pas perturber l'UX
        console.warn('Unable to load preferences from API, using localStorage:', err)
        const localStyle = localStorage.getItem('sidebar_style') as 'v2' | 'v3' | null
        if (localStyle) {
          setPreferences({ sidebar_style: localStyle })
        }
      } finally {
        setIsLoading(false)
      }
    }

    loadPreferences()
  }, [isAuthenticated])

  // Mettre à jour les préférences
  const updatePreferences = useCallback(async (newPrefs: Partial<UIPreferences>) => {
    try {
      setError(null)

      // Mettre à jour l'état local immédiatement
      setPreferences(prev => ({ ...prev, ...newPrefs }))

      // Sauvegarder dans localStorage
      if (newPrefs.sidebar_style) {
        localStorage.setItem('sidebar_style', newPrefs.sidebar_style)
      }

      // Si authentifié, sauvegarder sur le serveur
      if (isAuthenticated) {
        const token = localStorage.getItem('access_token')
        if (token) {
          try {
            const response = await fetch(`${API_BASE}/api/auth/users/me/preferences`, {
              method: 'PATCH',
              headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`
              },
              body: JSON.stringify(newPrefs)
            })

            if (response.ok) {
              const data = await response.json()
              // Mettre à jour avec les données du serveur
              setPreferences({
                sidebar_style: data.ui_preferences?.sidebar_style || 'v2'
              })
            } else {
              console.warn(`Failed to save preferences to server (${response.status}), but localStorage saved`)
              // Ne pas considérer comme une erreur si localStorage est sauvegardé
            }
          } catch (apiErr) {
            console.warn('Failed to save preferences to API, but localStorage saved:', apiErr)
            // Ne pas considérer comme une erreur si localStorage est sauvegardé
          }
        }
      }

      return true
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Erreur inconnue'
      setError(errorMsg)
      console.error('Erreur lors de la mise à jour des préférences:', err)
      return false
    }
  }, [isAuthenticated])

  return {
    preferences,
    updatePreferences,
    isLoading,
    error
  }
}
