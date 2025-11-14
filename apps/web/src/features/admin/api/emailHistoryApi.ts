import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

// Use relative URL to go through Vite proxy
const API_URL = '/api';

export interface EmailHistoryItem {
  id: string;
  to_emails: string[];
  subject: string;
  template_name: string | null;
  status: 'sent' | 'failed' | 'pending';
  sent_at: string | null;
  error_message: string | null;
  sent_by: string;
  metadata: Record<string, any>;
  created_at: string;
}

export interface EmailHistoryResponse {
  items: EmailHistoryItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface EmailStats {
  total: number;
  sent: number;
  failed: number;
  last_7_days: number;
  success_rate: number;
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
    getEmailHistory: builder.query<EmailHistoryResponse, {
      page?: number;
      page_size?: number;
      status_filter?: string;
      sent_by?: string;
    }>({
      query: ({ page = 1, page_size = 20, status_filter, sent_by }) => {
        const params = new URLSearchParams();
        params.append('page', page.toString());
        params.append('page_size', page_size.toString());
        if (status_filter) params.append('status_filter', status_filter);
        if (sent_by) params.append('sent_by', sent_by);
        return `/emails/history?${params.toString()}`;
      },
      providesTags: ['EmailHistory'],
    }),
    getEmailStats: builder.query<EmailStats, void>({
      query: () => '/api/emails/history/stats',
      providesTags: ['EmailHistory'],
    }),
    clearEmailHistory: builder.mutation<any, number>({
      query: (older_than_days) => ({
        url: `/api/emails/history?older_than_days=${older_than_days}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['EmailHistory'],
    }),
  }),
});

export const {
  useGetEmailHistoryQuery,
  useGetEmailStatsQuery,
  useClearEmailHistoryMutation,
} = emailHistoryApi;
