import { configureStore } from '@reduxjs/toolkit'
import { authApi } from '@/features/auth/api/authApi'
import { mfaApi } from '@/features/auth/api/mfaApi'
import { profileApi } from '@/features/profile/api/profileApi'
import { validationApi } from '@/features/admin/api/validationApi'
import { notificationApi } from '@/features/notifications/api/notificationApi'
import { adminApi } from '@/features/admin/api/adminApi'
import { usersApi } from '@/features/users/api/usersApi'
import { userDetailsApi } from '@/features/admin/api/userDetailsApi'
import { securityApi } from '@/features/admin/api/securityApi'
import { locationsApi } from '@/features/admin/api/locationsApi'
import { locationApi } from '@/features/admin/api/locationApi'
import { missionApi } from '@/features/missions/api/missionApi'
import { configurationApi } from '@/features/admin/api/configurationApi'
import { featureFlagApi } from '@/features/admin/api/featureFlagApi'
import { emailSettingsApi } from '@/features/admin/api/emailSettingsApi'
import { emailHistoryApi } from '@/features/admin/api/emailHistoryApi'
import { emailTemplatesApi } from '@/features/admin/api/emailTemplatesApi'
import { emailDomainsApi } from '@/features/admin/api/emailDomainsApi'
import { contractApi } from '@/features/contracts/api/contractApi'
import { applicationApi } from '@/features/interim/api/applicationApi'
import { presenceApi } from '@/features/presence/api/presenceApi'
import { iamApi } from '@/features/iam/api/iamApi'
import { countryConfigApi } from '@/features/admin/api/countryConfigApi'
import { securityConfigApi } from '@/features/admin/api/securityConfigApi'
import { besoinApi } from '@/features/besoins/api/besoinApi'
import { configApi } from '@/features/besoins/api/configApi'
import { entrepriseApi } from '@/features/company/api/entrepriseApi'
import { invitationApi } from '@/features/company/api/invitationApi'
import { entrepriseFormConfigApi } from '@/features/company/api/entrepriseFormConfigApi'
import { appConfigApi } from '@/features/config/api/appConfigApi'
import { referencesApi } from '@/features/profile/api/referencesApi'
import { missionsApi } from '@/features/missions/api/missionsApi'
import { retentionPoliciesApi } from '@/features/admin/api/retentionPoliciesApi'
import { experiencesApi } from '@/features/profile/api/experiencesApi'
import { supportApi } from '@/features/support/api/supportApi'
import { documentsApi } from '@/features/documents/api/documentsApi'
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
    [userDetailsApi.reducerPath]: userDetailsApi.reducer,
    [securityApi.reducerPath]: securityApi.reducer,
    [locationsApi.reducerPath]: locationsApi.reducer,
    [locationApi.reducerPath]: locationApi.reducer,
    [missionApi.reducerPath]: missionApi.reducer,
    [configurationApi.reducerPath]: configurationApi.reducer,
    [featureFlagApi.reducerPath]: featureFlagApi.reducer,
    [emailSettingsApi.reducerPath]: emailSettingsApi.reducer,
    [emailHistoryApi.reducerPath]: emailHistoryApi.reducer,
    [emailTemplatesApi.reducerPath]: emailTemplatesApi.reducer,
    [emailDomainsApi.reducerPath]: emailDomainsApi.reducer,
    [contractApi.reducerPath]: contractApi.reducer,
    [applicationApi.reducerPath]: applicationApi.reducer,
    [presenceApi.reducerPath]: presenceApi.reducer,
    [iamApi.reducerPath]: iamApi.reducer,
    [countryConfigApi.reducerPath]: countryConfigApi.reducer,
    [securityConfigApi.reducerPath]: securityConfigApi.reducer,
    [besoinApi.reducerPath]: besoinApi.reducer,
    [configApi.reducerPath]: configApi.reducer,
    [entrepriseApi.reducerPath]: entrepriseApi.reducer,
    [invitationApi.reducerPath]: invitationApi.reducer,
    [entrepriseFormConfigApi.reducerPath]: entrepriseFormConfigApi.reducer,
    [appConfigApi.reducerPath]: appConfigApi.reducer,
    [referencesApi.reducerPath]: referencesApi.reducer,
    [missionsApi.reducerPath]: missionsApi.reducer,
    [retentionPoliciesApi.reducerPath]: retentionPoliciesApi.reducer,
    [experiencesApi.reducerPath]: experiencesApi.reducer,
    [supportApi.reducerPath]: supportApi.reducer,
    [documentsApi.reducerPath]: documentsApi.reducer,
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
      .concat(userDetailsApi.middleware)
      .concat(securityApi.middleware)
      .concat(locationsApi.middleware)
      .concat(locationApi.middleware)
      .concat(missionApi.middleware)
      .concat(configurationApi.middleware)
      .concat(featureFlagApi.middleware)
      .concat(emailSettingsApi.middleware)
      .concat(emailHistoryApi.middleware)
      .concat(emailTemplatesApi.middleware)
      .concat(emailDomainsApi.middleware)
      .concat(contractApi.middleware)
      .concat(applicationApi.middleware)
      .concat(presenceApi.middleware)
      .concat(iamApi.middleware)
      .concat(countryConfigApi.middleware)
      .concat(securityConfigApi.middleware)
      .concat(besoinApi.middleware)
      .concat(configApi.middleware)
      .concat(entrepriseApi.middleware)
      .concat(invitationApi.middleware)
      .concat(entrepriseFormConfigApi.middleware)
      .concat(appConfigApi.middleware)
      .concat(referencesApi.middleware)
      .concat(missionsApi.middleware)
      .concat(retentionPoliciesApi.middleware)
      .concat(experiencesApi.middleware)
      .concat(supportApi.middleware)
      .concat(documentsApi.middleware),
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
