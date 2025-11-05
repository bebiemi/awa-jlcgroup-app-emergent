import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

// Use relative URL to go through Vite proxy
const API_URL = '/auth-api';

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

export interface EmailTestResponse {
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
    getEmailSettings: builder.query<EmailConfig, void>({
      query: () => '/api/emails/settings',
      providesTags: ['EmailSettings'],
    }),
    updateEmailSettings: builder.mutation<any, EmailConfigUpdate>({
      query: (config) => ({
        url: '/api/emails/settings',
        method: 'PUT',
        body: config,
      }),
      invalidatesTags: ['EmailSettings'],
    }),
    testEmailConfig: builder.mutation<EmailTestResponse, EmailTestRequest>({
      query: (testData) => ({
        url: '/api/emails/settings/test',
        method: 'POST',
        body: testData,
      }),
    }),
    deleteEmailSettings: builder.mutation<any, void>({
      query: () => ({
        url: '/api/emails/settings',
        method: 'DELETE',
      }),
      invalidatesTags: ['EmailSettings'],
    }),
  }),
});

export const {
  useGetEmailSettingsQuery,
  useUpdateEmailSettingsMutation,
  useTestEmailConfigMutation,
  useDeleteEmailSettingsMutation,
} = emailSettingsApi;

export const EMAIL_PROVIDERS: EmailProvider[] = [
  { value: 'gmail', label: 'Gmail' },
  { value: 'sendgrid', label: 'SendGrid' },
  { value: 'office365', label: 'Office 365' },
  { value: 'mailtrap', label: 'Mailtrap (Test)' },
  { value: 'custom', label: 'Personnalisé' },
];

export const PROVIDER_PRESETS: Record<string, Partial<EmailConfigUpdate>> = {
  gmail: {
    smtp_host: 'smtp.gmail.com',
    smtp_port: 587,
    smtp_use_tls: true,
  },
  sendgrid: {
    smtp_host: 'smtp.sendgrid.net',
    smtp_port: 587,
    smtp_user: 'apikey',
    smtp_use_tls: true,
  },
  office365: {
    smtp_host: 'smtp.office365.com',
    smtp_port: 587,
    smtp_use_tls: true,
  },
  mailtrap: {
    smtp_host: 'smtp.mailtrap.io',
    smtp_port: 2525,
    smtp_use_tls: true,
  },
  custom: {},
};
