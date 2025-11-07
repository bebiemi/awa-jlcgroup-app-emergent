import { useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { logoutAction } from '@/features/auth/slices/authSlice'
import { useUpdateMyPresenceMutation } from '@/features/presence/api/presenceApi'
import toast from 'react-hot-toast'

const AWAY_TIMEOUT = 15 * 60 * 1000 // 15 minutes to set status to "away"
const LOGOUT_TIMEOUT = 30 * 60 * 1000 // 30 minutes to auto-logout

export function useInactivityLogout() {
  const navigate = useNavigate()
  const dispatch = useAppDispatch()
  const { isAuthenticated } = useAppSelector((state) => state.auth)
  const awayTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const logoutTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const isAwayRef = useRef(false)
  const [updatePresence] = useUpdateMyPresenceMutation()

  const logout = useCallback(async () => {
    try {
      // 1. FIRST: Set user status to "offline" in backend
      await fetch('/auth-api/users/presence/me', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ status: 'offline' })
      }).catch(() => {}) // Silent fail if network error
    } catch (error) {
      console.error('Error setting offline status:', error)
    }
    
    // 2. Clear all API caches to prevent stale data
    dispatch({ type: 'presenceApi/resetApiState' })
    dispatch({ type: 'api/resetApiState' })
    
    // 3. Logout
    dispatch(logoutAction())
    toast.error('Déconnecté pour inactivité (30 minutes)')
    navigate('/', { replace: true })
  }, [dispatch, navigate])

  const setAwayStatus = useCallback(async () => {
    if (!isAwayRef.current) {
      try {
        await updatePresence({ status: 'away' }).unwrap()
        isAwayRef.current = true
        toast('Statut changé en "Inactif" après 15 minutes d\'inactivité', {
          icon: '🟡',
          duration: 3000,
        })
      } catch (error) {
        console.error('Failed to set away status:', error)
      }
    }
  }, [updatePresence])

  const resetToOnline = useCallback(async () => {
    if (isAwayRef.current) {
      try {
        // Use direct fetch for immediate response
        const token = localStorage.getItem('access_token')
        if (token) {
          await fetch('/auth-api/users/presence/me', {
            method: 'PATCH',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ status: 'online' })
          })
          isAwayRef.current = false
          console.log('✅ Status reset to ONLINE after activity')
        }
      } catch (error) {
        // Silently fail - not critical
        console.error('Failed to set online status:', error)
      }
    }
  }, [])

  const resetTimer = useCallback(() => {
    // Clear existing timers
    if (awayTimeoutRef.current) {
      clearTimeout(awayTimeoutRef.current)
    }
    if (logoutTimeoutRef.current) {
      clearTimeout(logoutTimeoutRef.current)
    }

    // Reset to online if was away
    resetToOnline()

    // Only set timers if user is authenticated
    if (isAuthenticated) {
      // Set away timer (15 minutes)
      awayTimeoutRef.current = setTimeout(setAwayStatus, AWAY_TIMEOUT)
      
      // Set logout timer (30 minutes)
      logoutTimeoutRef.current = setTimeout(logout, LOGOUT_TIMEOUT)
    }
  }, [isAuthenticated, logout, setAwayStatus, resetToOnline])

  useEffect(() => {
    if (!isAuthenticated) {
      // Clear timers if not authenticated
      if (awayTimeoutRef.current) clearTimeout(awayTimeoutRef.current)
      if (logoutTimeoutRef.current) clearTimeout(logoutTimeoutRef.current)
      isAwayRef.current = false
      return
    }

    // Events that indicate user activity
    const events = [
      'mousedown',
      'mousemove',
      'keypress',
      'scroll',
      'touchstart',
      'click',
    ]

    // Throttle to avoid too many resets
    let throttleTimeout: NodeJS.Timeout | null = null
    let lastActivityTime = 0
    
    const handleActivity = () => {
      const now = Date.now()
      const timeSinceLastActivity = now - lastActivityTime
      
      // Always reset on first activity or after throttle period
      if (!throttleTimeout || timeSinceLastActivity > 5000) {
        lastActivityTime = now
        resetTimer() // This will call resetToOnline if was away
        
        // Throttle subsequent calls for 5 seconds
        if (throttleTimeout) clearTimeout(throttleTimeout)
        throttleTimeout = setTimeout(() => {
          throttleTimeout = null
        }, 5000)
      }
    }

    // Add event listeners with passive option for better performance
    events.forEach((event) => {
      document.addEventListener(event, handleActivity, { passive: true })
    })

    // Initialize timer
    resetTimer()

    // Cleanup
    return () => {
      events.forEach((event) => {
        document.removeEventListener(event, handleActivity)
      })
      if (awayTimeoutRef.current) {
        clearTimeout(awayTimeoutRef.current)
      }
      if (logoutTimeoutRef.current) {
        clearTimeout(logoutTimeoutRef.current)
      }
      if (throttleTimeout) {
        clearTimeout(throttleTimeout)
      }
    }
  }, [isAuthenticated, resetTimer])
}
