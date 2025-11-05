import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface Contract {
  id: string;
  mission_id: string;
  mission_title: string;
  mission_description: string;
  company_name: string;
  location: string;
  start_date: string;
  end_date: string;
  contract_type: string;
  status: string;
  application_date: string;
  contract_signed_date: string | null;
  salary_range: string;
  work_schedule: string;
  is_active?: boolean;
  is_ended?: boolean;
  days_remaining?: number;
  alert_upcoming_end?: boolean;
}

export interface ContractsResponse {
  contracts: Contract[];
  total: number;
  active_contract: Contract | null;
  upcoming_end: {
    contract_id: string;
    mission_title: string;
    end_date: string;
    days_remaining: number;
  } | null;
  can_apply: boolean;
}

export const contractApi = createApi({
  reducerPath: 'contractApi',
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
  tagTypes: ['Contracts'],
  endpoints: (builder) => ({
    getMyContracts: builder.query<ContractsResponse, { status_filter?: string; include_ended?: boolean }>({
      query: ({ status_filter, include_ended = false }) => {
        const params = new URLSearchParams();
        if (status_filter) params.append('status_filter', status_filter);
        if (include_ended) params.append('include_ended', 'true');
        return `/api/contracts/me?${params.toString()}`;
      },
      providesTags: ['Contracts'],
    }),
    getActiveContract: builder.query<{
      active_contract: Contract | null;
      upcoming_end: any | null;
      can_apply: boolean;
    }, void>({
      query: () => '/api/contracts/active',
      providesTags: ['Contracts'],
    }),
    getContractDetails: builder.query<{ contract: Contract }, string>({
      query: (contractId) => `/api/contracts/${contractId}`,
      providesTags: ['Contracts'],
    }),
  }),
});

export const {
  useGetMyContractsQuery,
  useGetActiveContractQuery,
  useGetContractDetailsQuery,
} = contractApi;
