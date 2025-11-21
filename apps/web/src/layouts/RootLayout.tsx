import React from 'react'
import SidebarResolver from '@/components/SidebarResolver'
import { SidebarProvider } from '@/contexts/SidebarContext'
import { useAppSelector } from '@/store/hooks'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAppSelector((state) => state.auth)

  if (!isAuthenticated) {
    // Si non authentifié, pas de sidebar
    return <>{children}</>
  }

  return (
    <SidebarProvider>
      <SidebarResolver />
      {children}
    </SidebarProvider>
  )
}
