import { createApi } from '@reduxjs/toolkit/query/react'
import { baseQueryWithAuth } from '@/utils/baseQueryWithAuth';

// Use relative URL to go through Vite proxy

export type EmailTemplateType = 'rollback' | 'feature_flag' | 'user_welcome' | 'password_reset' | 'custom';

export interface EmailTemplate {
  id: string;
  name: string;
  type: EmailTemplateType;
  subject: string;
  html_content: string;
  text_content: string | null;
  variables: string[];
  is_active: boolean;
  is_system: boolean;
  created_at: string;
  updated_at: string;
  created_by: string;
}

export interface EmailTemplateCreate {
  name: string;
  type: EmailTemplateType;
  subject: string;
  html_content: string;
  text_content?: string;
  variables?: string[];
}

export interface EmailTemplateUpdate {
  name?: string;
  subject?: string;
  html_content?: string;
  text_content?: string;
  variables?: string[];
  is_active?: boolean;
}

export interface TemplatePreview {
  preview: string;
  subject: string;
  variables_used: string[];
}

export const emailTemplatesApi = createApi({
  reducerPath: 'emailTemplatesApi',
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
  tagTypes: ['EmailTemplates'],
  endpoints: (builder) => ({
    getTemplates: builder.query<{ templates: EmailTemplate[]; count: number }, {
      template_type?: EmailTemplateType;
      is_active?: boolean;
    }>({
      query: ({ template_type, is_active }) => {
        const params = new URLSearchParams();
        if (template_type) params.append('template_type', template_type);
        if (is_active !== undefined) params.append('is_active', is_active.toString());
        return `/api/emails/templates?${params.toString()}`;
      },
      providesTags: ['EmailTemplates'],
    }),
    getTemplate: builder.query<EmailTemplate, string>({
      query: (id) => `/api/emails/templates/${id}`,
      providesTags: ['EmailTemplates'],
    }),
    createTemplate: builder.mutation<any, EmailTemplateCreate>({
      query: (template) => ({
        url: '/api/emails/templates',
        method: 'POST',
        body: template,
      }),
      invalidatesTags: ['EmailTemplates'],
    }),
    updateTemplate: builder.mutation<any, { id: string; data: EmailTemplateUpdate }>({
      query: ({ id, data }) => ({
        url: `/api/emails/templates/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: ['EmailTemplates'],
    }),
    deleteTemplate: builder.mutation<any, string>({
      query: (id) => ({
        url: `/api/emails/templates/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['EmailTemplates'],
    }),
    previewTemplate: builder.mutation<TemplatePreview, { id: string; variables: Record<string, any> }>({
      query: ({ id, variables }) => ({
        url: `/api/emails/templates/${id}/preview`,
        method: 'POST',
        body: variables,
      }),
    }),
    initDefaultTemplates: builder.mutation<any, void>({
      query: () => ({
        url: '/api/emails/templates/init-defaults',
        method: 'POST',
      }),
      invalidatesTags: ['EmailTemplates'],
    }),
  }),
});

export const {
  useGetTemplatesQuery,
  useGetTemplateQuery,
  useCreateTemplateMutation,
  useUpdateTemplateMutation,
  useDeleteTemplateMutation,
  usePreviewTemplateMutation,
  useInitDefaultTemplatesMutation,
} = emailTemplatesApi;
