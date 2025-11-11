import { createApi } from '@reduxjs/toolkit/query/react'
import { baseQueryWithAuth } from '@/utils/baseQueryWithAuth';

// Use relative URL to go through Vite proxy

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
  baseQuery: baseQueryWithAuth,
  tagTypes: ['Applications'],
  endpoints: (builder) => ({
    getMyApplications: builder.query<{ applications: Application[] }, void>({
      query: () => '/missions/my-applications',
      providesTags: ['Applications'],
    }),
  }),
});

export const { useGetMyApplicationsQuery } = applicationApi;
