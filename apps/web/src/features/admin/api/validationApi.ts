import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import type { AccountValidation, ValidationListResponse } from '@/types'
import type { RootState } from '@/store/store'

export const validationApi = createApi({
  reducerPath: 'validationApi',
  baseQuery: fetchBaseQuery({
    baseUrl: '/api',
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token
      if (token) {
        headers.set('authorization', `Bearer ${token}`)
      }
      return headers
    },
  }),
  tagTypes: ['Validation'],
  endpoints: (builder) => ({
    getValidations: builder.query<
      ValidationListResponse,
      { status?: string; type?: string; page?: number; page_size?: number }
    >({
      query: (params) => ({
        url: '/validations/admin',
        params,
      }),
      providesTags: ['Validation'],
    }),
    getMyValidation: builder.query<AccountValidation, void>({
      query: () => '/validations/me',
      providesTags: ['Validation'],
    }),
    approveValidation: builder.mutation<
      AccountValidation,
      { id: string; comment?: string }
    >({
      query: ({ id, comment }) => ({
        url: `/validations/admin/${id}/approve`,
        method: 'POST',
        body: { comment },
      }),
      invalidatesTags: ['Validation'],
    }),
    rejectValidation: builder.mutation<
      AccountValidation,
      { id: string; comment: string }
    >({
      query: ({ id, comment }) => ({
        url: `/validations/admin/${id}/reject`,
        method: 'POST',
        body: { comment },
      }),
      invalidatesTags: ['Validation'],
    }),
  }),
})

export const {
  useGetValidationsQuery,
  useGetMyValidationQuery,
  useApproveValidationMutation,
  useRejectValidationMutation,
} = validationApi
