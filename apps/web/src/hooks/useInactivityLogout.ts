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
      // Clear timer if not authenticated
      if (logoutTimeoutRef.current) clearTimeout(logoutTimeoutRef.current)
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
      if (logoutTimeoutRef.current) {
        clearTimeout(logoutTimeoutRef.current)
      }
    }
  }, [isAuthenticated, resetTimer])
}
