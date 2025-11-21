/**
 * Sidebar Resolver
 * Charge la version de sidebar selon les préférences utilisateur
 * v2 = Classique (fond blanc)
 * v3 = Premium (fond dark avec gradient)
 */

import SidebarV2 from './SidebarNew'
import SidebarV3 from './SidebarNew.v3'
import { useUIPreferences } from '@/hooks/useUIPreferences'

export default function SidebarResolver() {
  const { preferences, isLoading } = useUIPreferences()

  // Pendant le chargement, afficher la version par défaut
  if (isLoading) {
    return <SidebarV2 />
  }

  // Charger le composant approprié selon les préférences
  if (preferences.sidebar_style === 'v3') {
    return <SidebarV3 />
  }
  
  return <SidebarV2 />
}
