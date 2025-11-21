/**
 * Sidebar Resolver
 * Charge la version de sidebar selon les préférences utilisateur
 * v2 = Classique (fond blanc)
 * v3 = Premium (fond dark avec gradient)
 */

import SidebarV2 from './SidebarNew'
import SidebarV3 from './SidebarNew.v3'
import { useAppSelector } from '@/store/hooks'

export default function SidebarResolver() {
  const { user } = useAppSelector((state) => state.auth)
  
  // Récupérer la préférence utilisateur, par défaut v2 (classique)
  const sidebarStyle = user?.ui_preferences?.sidebar_style ?? 'v2'

  // Charger le composant approprié
  if (sidebarStyle === 'v3') {
    return <SidebarV3 />
  }
  
  return <SidebarV2 />
}
