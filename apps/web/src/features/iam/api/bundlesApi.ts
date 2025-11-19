/**
 * API Client pour les Capability Bundles
 */
import { createApi } from '@reduxjs/toolkit/query/react';
import { baseQueryWithAuth } from '@/utils/baseQueryWithAuth';

export interface CapabilityBundle {
  id: string;
  code: string;
  name: string;
  description: string;
  category: string;
  permission_ids: string[];
  tags: string[];
  is_system: boolean;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface CreateBundleRequest {
  code: string;
  name: string;
  description: string;
  category: string;
  permission_ids: string[];
  tags?: string[];
}

export interface UpdateBundleRequest {
  name?: string;
  description?: string;
  permission_ids?: string[];
  tags?: string[];
}

export const bundlesApi = createApi({
  reducerPath: 'bundlesApi',
  baseQuery: baseQueryWithAuth,
  tagTypes: ['Bundle', 'Bundles'],
  endpoints: (builder) => ({
    // Lister tous les bundles
    getBundles: builder.query<CapabilityBundle[], { category?: string }>({
      query: (params) => ({
        url: '/iam/bundles',
        params,
      }),
      providesTags: ['Bundles'],
    }),

    // Détails d'un bundle
    getBundle: builder.query<CapabilityBundle, string>({
      query: (id) => `/iam/bundles/${id}`,
      providesTags: (result, error, id) => [{ type: 'Bundle', id }],
    }),

    // Créer un bundle
    createBundle: builder.mutation<CapabilityBundle, CreateBundleRequest>({
      query: (data) => ({
        url: '/iam/bundles',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Bundles'],
    }),

    // Modifier un bundle
    updateBundle: builder.mutation<CapabilityBundle, { id: string; data: UpdateBundleRequest }>({
      query: ({ id, data }) => ({
        url: `/iam/bundles/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [{ type: 'Bundle', id }, 'Bundles'],
    }),

    // Supprimer un bundle
    deleteBundle: builder.mutation<{ success: boolean }, string>({
      query: (id) => ({
        url: `/iam/bundles/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Bundles'],
    }),
  }),
});

export const {
  useGetBundlesQuery,
  useGetBundleQuery,
  useCreateBundleMutation,
  useUpdateBundleMutation,
  useDeleteBundleMutation,
} = bundlesApi;
