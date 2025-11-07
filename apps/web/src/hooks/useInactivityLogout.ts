import { useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { logoutAction } from '@/features/auth/slices/authSlice'
import toast from 'react-hot-toast'

// Simple inactivity logout - 30 minutes
const LOGOUT_TIMEOUT = 30 * 60 * 1000 // 30 minutes to auto-logout

export function useInactivityLogout() {
  const navigate = useNavigate()
  const dispatch = useAppDispatch()
  const { isAuthenticated } = useAppSelector((state) => state.auth)
  const logoutTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  const logout = useCallback(() => {
    dispatch(logoutAction())
    toast.error('Déconnecté pour inactivité (30 minutes)')
    navigate('/', { replace: true })
  }, [dispatch, navigate])

  const resetTimer = useCallback(() => {
    // Clear existing timer
    if (logoutTimeoutRef.current) {
      clearTimeout(logoutTimeoutRef.current)
    }

    // Only set timer if user is authenticated
    if (isAuthenticated) {
      // Set logout timer (30 minutes)
      logoutTimeoutRef.current = setTimeout(logout, LOGOUT_TIMEOUT)
    }
  }, [isAuthenticated, logout])

  useEffect(() => {
    if (!isAuthenticated) {
      // Clear all timers if not authenticated
      if (awayTimeoutRef.current) clearTimeout(awayTimeoutRef.current)
      if (logoutTimeoutRef.current) clearTimeout(logoutTimeoutRef.current)
      if (activityIntervalRef.current) clearInterval(activityIntervalRef.current)
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

    // Reset timer on any user activity
    const handleActivity = () => {
      resetTimer()
      
      // Throttle activity updates to max once per minute
      const now = Date.now()
      const timeSinceLastUpdate = now - lastActivityUpdateRef.current
      
      if (timeSinceLastUpdate > 60000) { // Only update if 1+ minute since last update
        lastActivityUpdateRef.current = now
        updateActivity().catch(console.error)
      }
    }

    // Add event listeners
    events.forEach((event) => {
      document.addEventListener(event, handleActivity, { passive: true })
    })

    // Initialize timer
    resetTimer()

    // Periodic activity update (every 2 minutes if user is active)
    activityIntervalRef.current = setInterval(() => {
      if (isAuthenticated) {
        updateActivity().catch(console.error)
      }
    }, ACTIVITY_UPDATE_INTERVAL)

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
      if (activityIntervalRef.current) {
        clearInterval(activityIntervalRef.current)
      }
    }
  }, [isAuthenticated, resetTimer, updateActivity])
}
