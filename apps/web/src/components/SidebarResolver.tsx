// /**
//  * Sidebar Resolver
//  * Charge la version de sidebar selon les préférences utilisateur
//  * v2 = Classique (fond blanc)
//  * v3 = Premium (fond dark avec gradient)
//  * 
//  * SIMPLE: Lecture synchrone localStorage uniquement, pas d'API blocking
//  */

// import SidebarV2 from './SidebarNew'
// import SidebarV3 from './SidebarNew.v3'

// export default function SidebarResolver() {
//   // Lecture SYNCHRONE depuis localStorage uniquement
//   const sidebarStyle = localStorage.getItem('sidebar_style')

//   // Charger le composant approprié
//   if (sidebarStyle === 'v3') {
//     return <SidebarV3 />
//   }
  
//   return <SidebarV2 />
// }
/**
 * SidebarResolver (Unified Loader)
 * Charge uniquement SidebarUltimate.
 * Les anciennes variantes SidebarNew / SidebarNew.v3 sont dépréciées.
 */
import SidebarUltimate from './SidebarUltimate'

export default function SidebarResolver() {
  return <SidebarUltimate />
}