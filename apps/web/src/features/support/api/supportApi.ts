import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import type { RootState } from '@/store/store'

export interface Ticket {
  id: string
  user_id: string
  user_email: string
  user_name?: string
  subject: string
  category: string
  priority: string
  status: string
  assigned_to?: string
  assigned_to_name?: string
  created_at: string
  updated_at: string
  resolved_at?: string
  closed_at?: string
  message_count: number
}

export interface Message {
  id: string
  ticket_id: string
  user_id: string
  user_email: string
  user_name?: string
  message: string
  is_internal: boolean
  created_at: string
}

export interface CreateTicketRequest {
  subject: string
  message: string
  category: string
  priority?: string
}

export interface CreateMessageRequest {
  message: string
}

export const supportApi = createApi({
  reducerPath: 'supportApi',
  baseQuery: fetchBaseQuery({
    baseUrl: '/api/support',
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token
      if (token) {
        headers.set('authorization', `Bearer ${token}`)
      }
      return headers
    },
  }),
  tagTypes: ['Tickets', 'Messages'],
  endpoints: (builder) => ({
    // Create ticket
    createTicket: builder.mutation<Ticket, CreateTicketRequest>({
      query: (data) => ({
        url: '/tickets',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Tickets'],
    }),

    // List tickets
    listTickets: builder.query<Ticket[], { status?: string; category?: string }>({
      query: (params) => ({
        url: '/tickets',
        params,
      }),
      providesTags: ['Tickets'],
    }),

    // Get ticket
    getTicket: builder.query<Ticket, string>({
      query: (id) => `/tickets/${id}`,
      providesTags: (result, error, id) => [{ type: 'Tickets', id }],
    }),

    // Add message to ticket
    addMessage: builder.mutation<Message, { ticket_id: string; data: CreateMessageRequest }>({
      query: ({ ticket_id, data }) => ({
        url: `/tickets/${ticket_id}/messages`,
        method: 'POST',
        body: data,
      }),
      invalidatesTags: (result, error, { ticket_id }) => [
        'Messages',
        { type: 'Tickets', id: ticket_id },
        'Tickets',
      ],
    }),

    // List messages
    listMessages: builder.query<Message[], string>({
      query: (ticket_id) => `/tickets/${ticket_id}/messages`,
      providesTags: (result, error, ticket_id) => [
        'Messages',
        { type: 'Messages', id: ticket_id },
      ],
    }),

    // Close ticket
    closeTicket: builder.mutation<Ticket, string>({
      query: (ticket_id) => ({
        url: `/tickets/${ticket_id}/close`,
        method: 'PATCH',
      }),
      invalidatesTags: (result, error, ticket_id) => [
        'Tickets',
        { type: 'Tickets', id: ticket_id },
      ],
    }),
  }),
})

export const {
  useCreateTicketMutation,
  useListTicketsQuery,
  useGetTicketQuery,
  useAddMessageMutation,
  useListMessagesQuery,
  useCloseTicketMutation,
} = supportApi
