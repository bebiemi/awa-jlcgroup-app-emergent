import { useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { logoutAction } from '@/features/auth/slices/authSlice'
import toast from 'react-hot-toast'

const INACTIVITY_TIMEOUT = 60 * 60 * 1000 // 60 minutes (1 hour) in milliseconds
const WARNING_TIME = 5 * 60 * 1000 // Show warning 5 minutes before logout

export function useInactivityLogout() {
  const navigate = useNavigate()
  const dispatch = useAppDispatch()
  const { isAuthenticated } = useAppSelector((state) => state.auth)
  const timeoutRef = useRef<NodeJS.Timeout | null>(null)
  const warningTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  const logout = useCallback(() => {
    dispatch(logoutAction())
    toast.error('Session expirée pour cause d\'inactivité')
    navigate('/', { replace: true })
  }, [dispatch, navigate])

  const showWarning = useCallback(() => {
    toast('Vous serez déconnecté dans 5 minutes pour inactivité', {
      icon: '⏰',
      duration: 5000,
    })
  }, [])

  const resetTimer = useCallback(() => {
    // Clear existing timers
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }
    if (warningTimeoutRef.current) {
      clearTimeout(warningTimeoutRef.current)
    }

    // Only set timers if user is authenticated
    if (isAuthenticated) {
      // Set warning timer (9 minutes)
      warningTimeoutRef.current = setTimeout(showWarning, INACTIVITY_TIMEOUT - WARNING_TIME)

      // Set logout timer (10 minutes)
      timeoutRef.current = setTimeout(logout, INACTIVITY_TIMEOUT)
    }
  }, [isAuthenticated, logout, showWarning])

  useEffect(() => {
    if (!isAuthenticated) {
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

    // Add event listeners
    events.forEach((event) => {
      document.addEventListener(event, handleActivity)
    })

    // Initialize timer
    resetTimer()

    // Cleanup
    return () => {
      events.forEach((event) => {
        document.removeEventListener(event, handleActivity)
      })
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
      if (warningTimeoutRef.current) {
        clearTimeout(warningTimeoutRef.current)
      }
    }
  }, [isAuthenticated, resetTimer])
}
