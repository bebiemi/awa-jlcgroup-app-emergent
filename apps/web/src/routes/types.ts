import { ReactNode } from 'react'

export type AppRoute = {
  path: string
  element: ReactNode
  requiredPermissions?: string[]
  requireAllPermissions?: boolean
  requireAuth?: boolean
  children?: AppRoute[]
}
