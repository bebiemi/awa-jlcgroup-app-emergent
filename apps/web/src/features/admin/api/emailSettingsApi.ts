import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface EmailProvider {
  value: 'gmail' | 'sendgrid' | 'office365' | 'mailtrap' | 'custom';
  label: string;
}

export interface EmailConfig {
  id: string;
  enabled: boolean;
  provider: string;
  smtp_host: string;
  smtp_port: number;
  smtp_user: string;
  smtp_use_tls: boolean;
  from_email: string;
  from_name: string;
  admin_emails: string[];
  created_at: string;
  updated_at: string;
  updated_by: string;
  is_configured: boolean;
}

export interface EmailConfigUpdate {
  enabled?: boolean;
  provider?: string;
  smtp_host?: string;
  smtp_port?: number;
  smtp_user?: string;
  smtp_password?: string;
  smtp_use_tls?: boolean;
  from_email?: string;
  from_name?: string;
  admin_emails?: string[];
}

export interface EmailTestRequest {
  smtp_host: string;
  smtp_port: number;
  smtp_user: string;
  smtp_password: string;
  smtp_use_tls: boolean;
  from_email: string;
  to_email: string;
}


export interface EmailSettings {
  enabled: boolean;
  smtp_host: string;
  smtp_port: number;
  smtp_user: string;
  smtp_use_tls: boolean;
  smtp_use_ssl: boolean;
  from_email: string;
  from_name: string;
  admin_emails: string[];
}

export interface EmailSettingsUpdate {
  enabled?: boolean;
  smtp_host?: string;
  smtp_port?: number;
  smtp_user?: string;
  smtp_password?: string;
  smtp_use_tls?: boolean;
  smtp_use_ssl?: boolean;
  from_email?: string;
  from_name?: string;
  admin_emails?: string[];
}

export interface TestEmailRequest {
  test_email: string;
}

export interface TestEmailResponse {
  success: boolean;
  message: string;
}

export const emailSettingsApi = createApi({
  reducerPath: 'emailSettingsApi',
  baseQuery: fetchBaseQuery({
    baseUrl: API_URL,
    prepareHeaders: (headers) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        headers.set('Authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ['EmailSettings'],
  endpoints: (builder) => ({
    getEmailSettings: builder.query<EmailSettings, void>({
      query: () => '/api/email-settings',
      providesTags: ['EmailSettings'],
    }),
    updateEmailSettings: builder.mutation<EmailSettings, EmailSettingsUpdate>({
      query: (settings) => ({
        url: '/api/email-settings',
        method: 'PUT',
        body: settings,
      }),
      invalidatesTags: ['EmailSettings'],
    }),
    testEmailConfig: builder.mutation<TestEmailResponse, TestEmailRequest>({
      query: (body) => ({
        url: '/api/email-settings/test',
        method: 'POST',
        body,
      }),
    }),
  }),
});

export const {
  useGetEmailSettingsQuery,
  useUpdateEmailSettingsMutation,
  useTestEmailConfigMutation,
} = emailSettingsApi;
