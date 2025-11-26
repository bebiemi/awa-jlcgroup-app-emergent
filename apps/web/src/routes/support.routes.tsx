import SupportTicketsPage from '@/features/support/pages/SupportTicketsPage'
import CreateTicketPage from '@/features/support/pages/CreateTicketPage'
import TicketDetailPage from '@/features/support/pages/TicketDetailPage'
import { AppRoute } from './types'

export const supportRoutes: AppRoute[] = [
  {
    path: '/support/tickets',
    element: <SupportTicketsPage />,
    requiredPermissions: ['support.manage'],
  },
  {
    path: '/support/tickets/new',
    element: <CreateTicketPage />,
    requiredPermissions: ['support.manage'],
  },
  {
    path: '/support/tickets/:id',
    element: <TicketDetailPage />,
    requiredPermissions: ['support.manage'],
  },
]
