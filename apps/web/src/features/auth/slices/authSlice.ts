import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import type { User } from '@/types'
import { authApi } from '../api/authApi'
import { extractPermissionsFromJWT } from '@/utils/jwt'

interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
}

const initialState: AuthState = {
  user: localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')!) : null,
  token: localStorage.getItem('access_token'),
  refreshToken: localStorage.getItem('refresh_token'),
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,
}

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setCredentials: (
      state,
      action: PayloadAction<{ user: User; token: string; refreshToken?: string }>
    ) => {
      // Extract permissions from JWT
      const permissions = extractPermissionsFromJWT(action.payload.token)
      
      // Add permissions to user object
      const userWithPermissions = {
        ...action.payload.user,
        permissions,
      }
      
      state.user = userWithPermissions
      state.token = action.payload.token
      state.refreshToken = action.payload.refreshToken || null
      state.isAuthenticated = true
      localStorage.setItem('access_token', action.payload.token)
      localStorage.setItem('user', JSON.stringify(userWithPermissions))
      if (action.payload.refreshToken) {
        localStorage.setItem('refresh_token', action.payload.refreshToken)
      }
    },
    logout: (state) => {
      state.user = null
      state.token = null
      state.refreshToken = null
      state.isAuthenticated = false
      
      // CRITICAL: Complete cleanup of all auth-related data
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      sessionStorage.clear() // Clear session storage too
      
      console.log('✅ Auth state cleared completely')
    },
  },
  extraReducers: (builder) => {
    builder.addMatcher(
      authApi.endpoints.localLogin.matchFulfilled,
      (state, { payload }) => {
        // Extract permissions from JWT
        const permissions = extractPermissionsFromJWT(payload.access_token)
        
        // Add permissions to user object
        const userWithPermissions = {
          ...payload.user,
          permissions,
        }
        
        state.user = userWithPermissions
        state.token = payload.access_token
        state.refreshToken = payload.refresh_token || null
        state.isAuthenticated = true
        localStorage.setItem('access_token', payload.access_token)
        localStorage.setItem('user', JSON.stringify(userWithPermissions))
        if (payload.refresh_token) {
          localStorage.setItem('refresh_token', payload.refresh_token)
        }
      }
    )
    builder.addMatcher(
      authApi.endpoints.getCurrentUser.matchFulfilled,
      (state, { payload }) => {
        state.user = payload
        state.isAuthenticated = true
        localStorage.setItem('user', JSON.stringify(payload))
      }
    )
  },
})

export const { setCredentials, logout: logoutAction } = authSlice.actions
export default authSlice.reducer
