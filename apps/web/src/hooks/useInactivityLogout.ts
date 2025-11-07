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

  const logout = useCallback(() => {
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
        await updatePresence({ status: 'online' }).unwrap()
        isAwayRef.current = false
      } catch (error) {
        console.error('Failed to set online status:', error)
      }
    }
  }, [updatePresence])

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
