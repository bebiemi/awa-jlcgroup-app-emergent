import { configureStore } from '@reduxjs/toolkit'
import { authApi } from '@/features/auth/api/authApi'
import { mfaApi } from '@/features/auth/api/mfaApi'
import { profileApi } from '@/features/profile/api/profileApi'
import { validationApi } from '@/features/admin/api/validationApi'
import { notificationApi } from '@/features/notifications/api/notificationApi'
import { adminApi } from '@/features/admin/api/adminApi'
import { usersApi } from '@/features/admin/api/usersApi'
import { securityApi } from '@/features/admin/api/securityApi'
import { locationsApi } from '@/features/admin/api/locationsApi'
import { locationApi } from '@/features/admin/api/locationApi'
import { missionApi } from '@/features/missions/api/missionApi'
import { configurationApi } from '@/features/admin/api/configurationApi'
import { featureFlagApi } from '@/features/admin/api/featureFlagApi'
import { emailSettingsApi } from '@/features/admin/api/emailSettingsApi'
import { emailHistoryApi } from '@/features/admin/api/emailHistoryApi'
import { emailTemplatesApi } from '@/features/admin/api/emailTemplatesApi'
import { contractApi } from '@/features/contracts/api/contractApi'
import { applicationApi } from '@/features/interim/api/applicationApi'
import authReducer from '@/features/auth/slices/authSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    [authApi.reducerPath]: authApi.reducer,
    [mfaApi.reducerPath]: mfaApi.reducer,
    [profileApi.reducerPath]: profileApi.reducer,
    [validationApi.reducerPath]: validationApi.reducer,
    [notificationApi.reducerPath]: notificationApi.reducer,
    [adminApi.reducerPath]: adminApi.reducer,
    [usersApi.reducerPath]: usersApi.reducer,
    [securityApi.reducerPath]: securityApi.reducer,
    [locationsApi.reducerPath]: locationsApi.reducer,
    [locationApi.reducerPath]: locationApi.reducer,
    [missionApi.reducerPath]: missionApi.reducer,
    [configurationApi.reducerPath]: configurationApi.reducer,
    [featureFlagApi.reducerPath]: featureFlagApi.reducer,
    [emailSettingsApi.reducerPath]: emailSettingsApi.reducer,
    [emailHistoryApi.reducerPath]: emailHistoryApi.reducer,
    [emailTemplatesApi.reducerPath]: emailTemplatesApi.reducer,
    [contractApi.reducerPath]: contractApi.reducer,
    [applicationApi.reducerPath]: applicationApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware()
      .concat(authApi.middleware)
      .concat(mfaApi.middleware)
      .concat(profileApi.middleware)
      .concat(validationApi.middleware)
      .concat(notificationApi.middleware)
      .concat(adminApi.middleware)
      .concat(usersApi.middleware)
      .concat(securityApi.middleware)
      .concat(locationsApi.middleware)
      .concat(locationApi.middleware)
      .concat(missionApi.middleware)
      .concat(configurationApi.middleware)
      .concat(featureFlagApi.middleware)
      .concat(emailSettingsApi.middleware)
      .concat(emailHistoryApi.middleware)
      .concat(emailTemplatesApi.middleware),
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
