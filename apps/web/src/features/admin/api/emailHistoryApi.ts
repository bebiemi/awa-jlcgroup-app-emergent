import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface EmailHistoryEntry {
  id: string;
  to_emails: string[];
  subject: string;
  body: string;
  sent_at: string;
  success: boolean;
  error_message?: string;
}

export const emailHistoryApi = createApi({
  reducerPath: 'emailHistoryApi',
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
  tagTypes: ['EmailHistory'],
  endpoints: (builder) => ({
    getEmailHistory: builder.query<{ history: EmailHistoryEntry[]; total: number }, { limit?: number; skip?: number }>({
      query: ({ limit = 50, skip = 0 }) => `/api/email-history?limit=${limit}&skip=${skip}`,
      providesTags: ['EmailHistory'],
    }),
  }),
});

export const { useGetEmailHistoryQuery } = emailHistoryApi;
