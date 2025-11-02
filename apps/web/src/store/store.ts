import { configureStore } from '@reduxjs/toolkit'
import { authApi } from '@/features/auth/api/authApi'
import { profileApi } from '@/features/profile/api/profileApi'
import { validationApi } from '@/features/admin/api/validationApi'
import { notificationApi } from '@/features/notifications/api/notificationApi'
import { adminApi } from '@/features/admin/api/adminApi'
import { usersApi } from '@/features/admin/api/usersApi'
import authReducer from '@/features/auth/slices/authSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    [authApi.reducerPath]: authApi.reducer,
    [profileApi.reducerPath]: profileApi.reducer,
    [validationApi.reducerPath]: validationApi.reducer,
    [notificationApi.reducerPath]: notificationApi.reducer,
    [adminApi.reducerPath]: adminApi.reducer,
    [usersApi.reducerPath]: usersApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware()
      .concat(authApi.middleware)
      .concat(profileApi.middleware)
      .concat(validationApi.middleware)
      .concat(notificationApi.middleware)
      .concat(adminApi.middleware)
      .concat(usersApi.middleware),
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
