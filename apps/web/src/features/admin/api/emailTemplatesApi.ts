import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface EmailTemplate {
  id: string;
  name: string;
  subject: string;
  body: string;
  variables: string[];
  created_at: string;
  updated_at: string;
}

export interface CreateTemplateRequest {
  name: string;
  subject: string;
  body: string;
  variables?: string[];
}

export interface UpdateTemplateRequest {
  name?: string;
  subject?: string;
  body?: string;
  variables?: string[];
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
    getTemplates: builder.query<{ templates: EmailTemplate[] }, void>({
      query: () => '/api/email-templates',
      providesTags: ['EmailTemplates'],
    }),
    createTemplate: builder.mutation<EmailTemplate, CreateTemplateRequest>({
      query: (template) => ({
        url: '/api/email-templates',
        method: 'POST',
        body: template,
      }),
      invalidatesTags: ['EmailTemplates'],
    }),
    updateTemplate: builder.mutation<EmailTemplate, { id: string; data: UpdateTemplateRequest }>({
      query: ({ id, data }) => ({
        url: `/api/email-templates/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: ['EmailTemplates'],
    }),
    deleteTemplate: builder.mutation<void, string>({
      query: (id) => ({
        url: `/api/email-templates/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['EmailTemplates'],
    }),
  }),
});

export const {
  useGetTemplatesQuery,
  useCreateTemplateMutation,
  useUpdateTemplateMutation,
  useDeleteTemplateMutation,
} = emailTemplatesApi;
