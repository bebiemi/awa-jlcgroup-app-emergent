import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

// Use relative URL to go through Vite proxy
const API_URL = '/auth-api';

export interface Application {
  id: string;
  mission_id: string;
  mission_title: string;
  company_name: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export const applicationApi = createApi({
  reducerPath: 'applicationApi',
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
  tagTypes: ['Applications'],
  endpoints: (builder) => ({
    getMyApplications: builder.query<{ applications: Application[] }, void>({
      query: () => '/missions/my-applications',
      providesTags: ['Applications'],
    }),
  }),
});

export const { useGetMyApplicationsQuery } = applicationApi;
